from pathlib import Path
import json,subprocess,hashlib
import numpy as np
from scipy.signal import butter,sosfilt

R=Path(__file__).resolve().parent;SR=48000;N=30*SR
def run(a,data=None):return subprocess.run(a,input=data,capture_output=True,check=True)
def decode(p):return np.frombuffer(run(['ffmpeg','-v','error','-i',str(p),'-ar',str(SR),'-ac','1','-f','f32le','-']).stdout,dtype='<f4').copy()
def write(p,x):
 x=np.asarray(x);ch=1 if x.ndim==1 else x.shape[1]
 run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac',str(ch),'-i','-','-c:a','pcm_s24le',str(p)],x.astype('<f4').tobytes())
def meter(p):
 s=run(['ffmpeg','-hide_banner','-nostats','-i',str(p),'-af','loudnorm=I=-19:TP=-3:LRA=8:print_format=json','-f','null','-']).stderr.decode()
 return json.loads(s[s.rfind('{'):s.rfind('}')+1])

voice=np.zeros(N);words=[];clips=[];captions=[];activity=np.zeros(N)
for v in json.loads((R/'script.json').read_text()):
 p=R/'assets/voice'/v['id'];x=decode(p.with_suffix('.mp3'))
 ev=[json.loads(t) for t in p.with_suffix('.jsonl').read_text().splitlines()];ev=[t for t in ev if t['type']=='WordBoundary']
 ev=[{'text':t['text'],'start':t['offset']/1e7,'end':(t['offset']+t['duration'])/1e7} for t in ev]
 lo=max(0,ev[0]['start']-.025);hi=min(len(x)/SR,ev[-1]['end']+.035)
 gap=.08 if v['id']=='q1' else .17
 cuts=[(a['end']+.035,b['start']-.035) for a,b in zip(ev,ev[1:]) if b['start']-a['end']>.4]
 # Keep a short, explicit punctuation pause. Never stretch or shorten phonemes.
 cuts=[(a+gap/2,b-gap/2) for a,b in cuts if b-a>gap]
 mapping=[];parts=[];cursor=0;prev=lo
 for a,b in cuts+[(hi,hi)]:
  z=x[round(prev*SR):round(a*SR)].copy();n=min(144,len(z)//10)
  if n:z[:n]*=np.linspace(0,1,n);z[-n:]*=np.linspace(1,0,n)
  parts.append(z);mapping.append((prev,a,cursor));cursor+=len(z)/SR;prev=b
 z=np.concatenate(parts)
 assert v['start']+len(z)/SR<=v['deadline']+.08,(v['id'],len(z)/SR,v['deadline']-v['start'])
 z=sosfilt(butter(2,70,fs=SR,btype='highpass',output='sos'),z)
 # Consistent phrase RMS, bounded static peak. No compressor or time warping.
 active=z[np.abs(z)>.008];rms=np.sqrt(np.mean(active*active))
 gain=min(.088/max(rms,1e-8),.55/max(np.max(np.abs(z)),1e-8));z*=gain
 a=round(v['start']*SR);voice[a:a+len(z)]+=z;activity[a:a+len(z)]=1
 def mapped(t):
  for a,b,c in mapping:
   if t<=b:return v['start']+c+max(0,t-a)
  return v['start']+len(z)/SR
 timed=[{'text':w['text'],'start':round(mapped(w['start']),5),'end':round(mapped(w['end']),5),'role':v['role'],'id':v['id']} for w in ev]
 words+=timed
 if v['id']=='vo':
  batches=[timed[:5],timed[5:9],timed[9:13],timed[13:]]
 else:batches=[timed]
 for batch in batches:
  captions.append({'start':max(v['start'],batch[0]['start']-.02),'end':batch[-1]['end']+.08,'text':' '.join(w['text'] for w in batch),'role':v['role']})
 clips.append({'id':v['id'],'start':v['start'],'end':v['start']+len(z)/SR,'sha256':hashlib.sha256(p.with_suffix('.mp3').read_bytes()).hexdigest(),'nativeGapCuts':cuts,'gainDB':float(20*np.log10(gain))})

fx=np.zeros((N,2));cues=[];rng=np.random.default_rng(2181)
def add(t,x,name,peak=.06,pan=0):
 global fx
 x=np.asarray(x);x=x*peak/max(np.max(np.abs(x)),1e-9)
 n=min(240,len(x)//5);x[:n]*=np.linspace(0,1,n);x[-n:]*=np.linspace(1,0,n)
 a=round(t*SR);b=min(N,a+len(x));x=x[:b-a]
 # Effects duck below the clear foreground dialogue.
 duck=1-.58*activity[a:b];x=x*duck
 fx[a:b,0]+=x*(1-pan*.25);fx[a:b,1]+=x*(1+pan*.25)
 cues.append({'time':t,'seconds':len(x)/SR,'name':name,'peak':peak})
def click(t,correct=False):
 d=.12 if correct else .07;tt=np.arange(round(d*SR))/SR
 x=np.sin(2*np.pi*(1600 if correct else 730)*tt)*np.exp(-tt*42)+rng.normal(0,.15,len(tt))*np.exp(-tt*95)
 add(t,x,'correct electronic pulse' if correct else 'button / tile click',.065)
for t in [4.55,9.70]:click(t,True)
for t in [3.2,8.1,14.98,22.2,24.0,25.55]:click(t)
# One decaying electronic impact; no melody, harmony, accompaniment or jingle.
t=np.arange(round(.38*SR))/SR
add(16.65,np.sin(2*np.pi*(1150*t+140*t*t))*np.exp(-t*13),'hero correct-answer pulse',.12)
for t in [3.05,7.96,18.98,26.95]:
 tt=np.arange(round(.18*SR))/SR;n=rng.normal(0,1,len(tt));n=sosfilt(butter(2,4000,fs=SR,output='sos'),n)
 add(t,n*np.sin(np.pi*tt/.18)**2,'short air transition',.025)
# Licensed recordings incorporated in this film only; raw originals remain /tmp.
applause=decode('/tmp/mdaar-feud-applause.mp3')
for t,d,pk in [(5.85,.95,.052),(16.9,2.1,.085)]:add(t,applause[:round(d*SR)].copy(),'SoundJay Applause 8 recording',pk)
laugh=decode('/tmp/mdaar-feud-laughter.mp3');add(11.75,laugh[:round(.95*SR)].copy(),'SoundJay Laughter & Applause recording',.045)
mix=np.repeat(voice[:,None],2,axis=1)+fx
write(R/'assets/final-mix.wav',mix);before=meter(R/'assets/final-mix.wav')
gain=min(-19-float(before['input_i']),-3-float(before['input_tp']));mix*=10**(gain/20)
write(R/'assets/final-mix.wav',mix)
silence=(round((next(c['end'] for c in clips if c['id']=='a3')+.03)*SR),round(16.65*SR))
assert silence[1]-silence[0]>=.5*SR
assert np.max(np.abs(mix[silence[0]:silence[1]]))==0
(R/'words.json').write_text(json.dumps(words,ensure_ascii=False,indent=2)+'\n')
for a,b in zip(captions,captions[1:]):
 a['end']=min(a['end'],b['start']-.012)
(R/'captions.json').write_text(json.dumps(captions,ensure_ascii=False,indent=2)+'\n')
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
(R/'captions.srt').write_text(''.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}\n\n' for i,c in enumerate(captions)))
report={'seconds':30,'clips':clips,'effects':cues,'musicAdded':False,'melodicJingleAdded':False,'actorFourSpeaks':False,'postTimeStretch':False,'halfSecondSilenceSamples':silence[1]-silence[0],'finalLoudness':meter(R/'assets/final-mix.wav'),'clippedSamples':int(np.sum(np.abs(mix)>=1)),'globalGainDB':gain,'humanListeningVerified':False}
(R/'reports/audio.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'seconds':30,'clips':len(clips),'captionGroups':len(captions),'loudness':report['finalLoudness'],'silenceSeconds':(silence[1]-silence[0])/SR}))
