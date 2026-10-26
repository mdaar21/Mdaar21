"""Non-destructive speech cleanup; keep source untouched and export the edit map."""
from pathlib import Path
import argparse, hashlib, json, re, subprocess
import numpy as np

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
args = parser.parse_args()
source = args.source.resolve()
rate = 48000
def run(argv):
    return subprocess.run(argv, capture_output=True, check=True)

raw = np.frombuffer(run(['ffmpeg','-v','error','-i',str(source),'-ac','1','-ar',str(rate),'-f','f32le','-']).stdout, dtype='<f4').copy()
duration = len(raw) / rate
det = run(['ffmpeg','-hide_banner','-i',str(source),'-af','silencedetect=noise=-28dB:d=0.30','-f','null','-']).stderr.decode()
(ROOT/'reports/silence-detection.txt').write_text(det)
silences = []
start = None
for kind, val in re.findall(r'silence_(start|end): ([0-9.]+)', det):
    if kind == 'start': start = float(val)
    elif start is not None:
        silences.append((start, float(val))); start = None
if start is not None: silences.append((start, duration))
cuts = []
for a, b in silences:
    if a < .02:
        if b > .16: cuts.append((0, b-.10))
    elif b >= duration-.04:
        if b-a > .20: cuts.append((a+.12, duration))
    elif b-a > .31:
        # Retain 180 ms of each longer pause; no deletion inside voiced regions.
        cuts.append((a+.09, b-.09))
segments=[]; previous=0; output_cursor=0
for a,b in cuts+[(duration,duration)]:
    if a>previous:
        first,last=round(previous*rate),round(a*rate)
        seconds=(last-first)/rate
        segments.append({'sourceStart':first/rate,'sourceEnd':last/rate,'outputStart':output_cursor,'outputEnd':output_cursor+seconds})
        output_cursor+=seconds
    previous=b
pieces=[]
for item in segments:
    x=raw[round(item['sourceStart']*rate):round(item['sourceEnd']*rate)].copy()
    n=min(192,len(x)//4) # 4 ms, prevents clicks without overlapping time.
    if n:
        x[:n]*=np.linspace(0,1,n);x[-n:]*=np.linspace(1,0,n)
    pieces.append(x)
edited=np.concatenate(pieces)
dry=ROOT/'assets/voice-edited.wav'
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(rate),'-ac','1','-i','-','-c:a','pcm_s24le',str(dry)],input=edited.astype('<f4').tobytes(),check=True)
chain='highpass=f=70,lowpass=f=11500,afftdn=nr=6:nf=-38:tn=1,equalizer=f=280:t=q:w=1:g=-1.2,equalizer=f=3200:t=q:w=0.8:g=1,acompressor=threshold=0.18:ratio=1.8:attack=12:release=110:makeup=1'
measurement=run(['ffmpeg','-hide_banner','-i',str(dry),'-af',chain+',loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-']).stderr.decode()
loudness=json.loads(measurement[measurement.rfind('{'):measurement.rfind('}')+1])
normalize='loudnorm=I=-16:TP=-1.5:LRA=9:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}:linear=true:print_format=json'.format(**loudness)
clean=ROOT/'assets/voice-clean.wav'
result=run(['ffmpeg','-hide_banner','-y','-i',str(dry),'-af',chain+','+normalize,'-ar',str(rate),'-c:a','pcm_s24le',str(clean)])
(ROOT/'reports/cleanup-ffmpeg.txt').write_text(result.stderr.decode())
run(['ffmpeg','-v','error','-y','-i',str(clean),'-codec:a','libmp3lame','-b:a','192k','-write_xing','1',str(ROOT/'assets/voice-clean.mp3')])
report={'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceSeconds':duration,'editedSeconds':len(edited)/rate,'removedSeconds':duration-len(edited)/rate,'removedIntervals':cuts,'keptSegments':segments,'fadeAtJoinsMs':4,'filters':chain,'loudnessTarget':{'integratedLUFS':-16,'truePeakDBTP':-1.5},'firstPass':loudness,'voiceReplaced':False,'speechSpeedChanged':False,'musicAdded':False,'sourceUnchanged':True}
(ROOT/'reports/audio-edit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['sourceSeconds','editedSeconds','removedSeconds','voiceReplaced','speechSpeedChanged','musicAdded']}))
