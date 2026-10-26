from pathlib import Path
import json,subprocess
import numpy as np

ROOT=Path(__file__).resolve().parent
rate=48000
def decode(file):
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(file),'-ar',str(rate),'-ac','1','-f','f32le','-'])
    return np.frombuffer(raw,dtype='<f4').copy()
voice=decode(ROOT/'assets/voice-clean.wav')
fx=np.zeros_like(voice)
beats=json.loads((ROOT/'beats.json').read_text())['beats']
cues=[]
for i,b in enumerate(beats):
    if i in [0,2,3,4,5,6,7,8,9,10,11,12,14]:
        name='whoosh-short' if i in [0,4,5,8,10,11,14] else 'click-soft' if i in [2,3,9,12] else 'whoosh'
        cues.append({'time':max(0,b['start']-.07),'name':name,'peak':.045 if 'whoosh' in name else .036,'seconds':.25 if 'whoosh' in name else .11})
cues += [{'time':beats[1]['start']+.65,'name':'key-press','peak':.035,'seconds':.10},{'time':beats[7]['start']+.92,'name':'pop','peak':.04,'seconds':.15},{'time':beats[12]['start']+1.55,'name':'click-soft','peak':.04,'seconds':.11}]
for c in cues:
    clip=decode(ROOT/'assets/sfx'/f"{c['name']}.mp3")
    # Reuse retrieved sound, trim around the onset; no generated oscillator or score.
    limit=round(c['seconds']*rate)
    peak=np.max(np.abs(clip))
    active=np.flatnonzero(np.abs(clip)>peak*.04)
    first=max(0,int(active[0]) - 96) if len(active) else 0
    clip=clip[first:first+limit].copy()
    if len(clip):
        clip*=c['peak']/max(np.max(np.abs(clip)),1e-6)
        n=min(240,len(clip)//4);clip[:n]*=np.linspace(0,1,n);clip[-n:]*=np.linspace(1,0,n)
        a=round(c['time']*rate);last=min(len(fx),a+len(clip));fx[a:last]+=clip[:last-a]
mix=voice+fx
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(rate),'-ac','1','-i','-','-af','alimiter=limit=0.841395:attack=5:release=50:level=false','-ar',str(rate),'-ac','2','-c:a','pcm_s24le',str(ROOT/'assets/final-mix.wav')],input=mix.astype('<f4').tobytes(),check=True)
report={'musicAdded':False,'voiceSource':'assets/voice-clean.wav','voiceAlteredBySfx':False,'effectSource':'Reused retrieved Pixabay library clips; assets/sfx/CREDITS.md','effects':cues,'sfxRmsDBFS':float(20*np.log10(np.sqrt(np.mean(fx**2))+1e-12)),'voiceRmsDBFS':float(20*np.log10(np.sqrt(np.mean(voice**2))+1e-12)),'durationSeconds':len(mix)/rate}
(ROOT/'reports/sound-mix.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['musicAdded','sfxRmsDBFS','voiceRmsDBFS','durationSeconds']}))
