from pathlib import Path
import json,subprocess
import numpy as np

ROOT=Path(__file__).resolve().parent;rate=48000
def decode(f):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-ar',str(rate),'-ac','1','-f','f32le','-']),dtype='<f4').copy()
voice=decode(ROOT/'assets/voice-clean.wav');fx=np.zeros_like(voice)
beats={b['id']:b for b in json.loads((ROOT/'beats.json').read_text())['beats']}
cues=[]
for scene,name,offset,peak,length in [('s8','whoosh-short',-.12,.026,.32),('s9','click-soft',.28,.018,.14),('s11','click-soft',.22,.018,.14),('s12','click-soft',1.63,.016,.13),('s14','whoosh-short',-.13,.022,.30)]:
    t=max(0,beats[scene]['start']+offset);x=decode(ROOT/'assets/sfx'/f'{name}.mp3')
    active=np.flatnonzero(np.abs(x)>np.max(np.abs(x))*.04);first=max(0,int(active[0])-192) if len(active) else 0
    x=x[first:first+round(length*rate)].copy();x*=peak/max(np.max(np.abs(x)),1e-6)
    n=min(720,len(x)//4);x[:n]*=np.linspace(0,1,n);x[-n:]*=np.linspace(1,0,n)
    a=round(t*rate);b=min(len(fx),a+len(x));fx[a:b]+=x[:b-a]
    cues.append({'scene':scene,'time':t,'source':name,'peak':peak,'seconds':length})
mix=voice+fx
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(rate),'-ac','1','-i','-','-af','alimiter=limit=0.841395:attack=5:release=50:level=false','-ar',str(rate),'-ac','2','-c:a','pcm_s24le',str(ROOT/'assets/final-mix.wav')],input=mix.astype('<f4').tobytes(),check=True)
# Measure the actual stereo delivery bus; apply only the safe linear gain needed.
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(ROOT/'assets/final-mix.wav'),'-af','loudnorm=I=-14:TP=-1.5:LRA=8:print_format=json','-f','null','-'],capture_output=True,check=True)
s=r.stderr.decode();meter=json.loads(s[s.rfind('{'):s.rfind('}')+1]);gain=min(-14-float(meter['input_i']),-1.5-float(meter['input_tp']))
tmp=ROOT/'assets/final-mix-normalized.wav'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'assets/final-mix.wav'),'-af',f'volume={gain}dB','-c:a','pcm_s24le',str(tmp)],check=True);tmp.replace(ROOT/'assets/final-mix.wav')
subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'assets/voice-clean.wav'),'-af',f'volume={gain}dB','-ac','2','-c:a','libmp3lame','-b:a','256k',str(ROOT/'assets/voice-clean.mp3')],check=True)
report={'musicAdded':False,'finalBusGainDB':gain,'voiceSource':'assets/voice-clean.wav','effects':cues,'voiceRmsDBFS':float(20*np.log10(np.sqrt(np.mean(voice**2)))),'sfxRmsDBFS':float(20*np.log10(np.sqrt(np.mean(fx**2))+1e-12)),'durationSeconds':len(mix)/rate,'note':'Five brief low-level accents, not a continuous bed. No music or voice replacement.'}
(ROOT/'reports/sound-mix.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
