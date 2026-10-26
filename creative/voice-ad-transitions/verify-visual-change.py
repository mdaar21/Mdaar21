"""Compare real encoded transition frames with V10's repeated wipes."""
from pathlib import Path
import json
import subprocess
import numpy as np

ROOT=Path(__file__).resolve().parent
baseline=ROOT.parents[1]/'public/ad/voice-original/mdaar_tiktok_v10_original_clear.mp4'
current=ROOT/'renders/mdaar_tiktok_v11_transitions.mp4'
plans=json.loads((ROOT/'transitions.json').read_text())
beats={b['id']:b for b in json.loads((ROOT/'beats.json').read_text())['beats']}
def frame(path,t):
    return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(path),
        '-frames:v','1','-vf','scale=360:640','-pix_fmt','rgb24','-f','rawvideo','-']),dtype=np.uint8).astype(np.float32)
rows=[]
for plan in plans:
    t=beats[plan['to']]['start']-.28+plan['duration']*.5
    a,b=frame(baseline,t),frame(current,t)
    mae=float(np.mean(np.abs(a-b)))
    assert mae>1,(plan['to'],mae)
    rows.append({'to':plan['to'],'family':plan['family'],'time':t,'meanAbsoluteRGBChange':mae})
report={'ok':True,'changedEncodedHandoffs':len(rows),'distinctFamilies':len(set(x['family'] for x in rows)),
        'comparisons':rows,'note':'Encoded frame differences confirm the delivered handoffs changed; pixel differences do not score artistic quality.'}
(ROOT/'reports/encoded-transition-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'ok':True,'changedHandoffs':len(rows),'families':report['distinctFamilies']}))
