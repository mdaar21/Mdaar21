"""Edit and mix retrieved, non-musical effects. No synthesis, instruments or music."""
from pathlib import Path
from shutil import copy2
import subprocess, json, wave, hashlib
import numpy as np

root=Path(__file__).resolve().parent
library=Path('/home/agent/.agents/skills/media-use/audio/assets/sfx')
sources=root/'assets'/'sfx';sources.mkdir(parents=True,exist_ok=True)
names=['whoosh-short','whoosh','click','click-soft','key-press','pop']
for name in names:
 if not (sources/(name+'.mp3')).exists():copy2(library/(name+'.mp3'),sources/(name+'.mp3'))
if not (sources/'CREDITS.md').exists():copy2(library/'CREDITS.md',sources/'CREDITS.md')
rate=48000;duration=20
clips={}
for name in names:
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(sources/(name+'.mp3')),'-f','f32le','-ac','2','-ar',str(rate),'-'])
 a=np.frombuffer(raw,dtype='<f4').reshape(-1,2).copy()
 # Remove encoder padding / silence so event onset matches the animation.
 active=np.flatnonzero(np.max(np.abs(a),axis=1)>.003)
 if len(active):a=a[max(0,active[0]-120):min(len(a),active[-1]+480)]
 peak=np.max(np.abs(a));a=a/max(peak,.01)
 clips[name]=a
# Cue offsets follow actions, not a BPM grid. No riser, chime, ping or tone assets.
cues=[
 (.13,'whoosh-short',.25,.34,'hook title'),(.34,'pop',.36,.24,'character leap'),
 (.68,'whoosh',.53,.23,'character landing'),(1.19,'click-soft',.17,.12,'flex snap'),
 (1.85,'whoosh-short',.45,.30,'paper push to confusion'),
 (2.38,'pop',.22,.19,'question mark'),(2.79,'click-soft',.14,.09,'scratch'),(3.18,'click-soft',.13,.11,'scratch'),
 (3.85,'whoosh',.5,.30,'push to training'),(4.28,'pop',.26,.21,'programme cards'),
 (4.72,'whoosh-short',.2,.21,'first lift'),(4.99,'key-press',.32,.13,'first bar lock'),
 (5.43,'click',.33,.13,'first bar return'),(5.75,'whoosh-short',.22,.21,'second lift'),
 (6.02,'key-press',.32,.13,'second bar lock'),(6.46,'click',.33,.13,'second bar return'),
 (6.85,'whoosh',.5,.36,'recipe reveal'),(7.23,'pop',.3,.24,'plate enters'),
 (7.97,'click-soft',.19,.13,'small hop landing'),(8.26,'pop',.21,.18,'plate gesture'),
 (9.35,'whoosh-short',.48,.31,'goals transition'),(9.88,'click',.27,.12,'first goal'),
 (10.27,'click-soft',.25,.11,'second goal'),(10.70,'click',.27,.12,'third goal'),
 (11.35,'whoosh',.47,.33,'guide transition'),(11.8,'whoosh-short',.24,.26,'cover pulled in'),
 (12.41,'key-press',.23,.13,'pages fan'),(13.85,'whoosh',.6,.44,'hero cover reveal'),
 (14.96,'pop',.28,.22,'celebratory landing'),(15.61,'click-soft',.17,.12,'character flex'),
 (16.65,'whoosh-short',.5,.34,'closing transition'),(17.47,'whoosh',.38,.25,'final landing'),
 (17.33,'pop',.3,.25,'purchase invitation'),(18.43,'click-soft',.17,.12,'CTA arrow')]
mix=np.zeros((rate*duration,2),np.float32)
manifest=[]
for t,name,gain,length,label in cues:
 source=clips[name];n=int(length*rate)
 # Time-compress the retrieved short effect; no added waveform or pitch source.
 pos=np.linspace(0,len(source)-1,n)
 a=np.column_stack([np.interp(pos,np.arange(len(source)),source[:,c]) for c in range(2)])
 fade=min(int(.008*rate),n//3)
 a[:fade]*=np.linspace(0,1,fade)[:,None];a[-fade:]*=np.linspace(1,0,fade)[:,None]
 start=round(t*rate);end=min(len(mix),start+n)
 mix[start:end]+=a[:end-start]*gain
 manifest.append({'time':t,'duration':length,'source':'assets/sfx/'+name+'.mp3','gain':gain,'action':label})
peak=float(np.max(np.abs(mix)));mix*=min(1,.68/max(peak,.01))
wav=root/'assets'/'sfx-only.wav'
with wave.open(str(wav),'wb') as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate);w.writeframes((mix*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-y','-v','error','-i',str(wav),'-c:a','libmp3lame','-b:a','192k',str(root/'assets'/'sfx-only.mp3')],check=True)
wav.unlink()
report={'duration':duration,'sampleRate':rate,'channels':2,'music':False,'voiceover':False,'sources':'Retrieved offline HyperFrames/Pixabay SFX library; see assets/sfx/CREDITS.md','excluded':['score.mp3','chime','ping','riser','instruments','background beat'], 'cues':manifest,'sourceHashes':{n:hashlib.sha256((sources/(n+'.mp3')).read_bytes()).hexdigest() for n in names},'peakDbfs':float(20*np.log10(np.max(np.abs(mix)))),'silentSampleFraction':float(np.mean(np.max(np.abs(mix),axis=1)<.001))}
(root/'effects-cues.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['cues','sourceHashes']},ensure_ascii=False))
