"""Conservative source-voice edit, fixed Arabic captions, sparse SFX, no music bed."""
from pathlib import Path
import json, hashlib, subprocess
import numpy as np
from scipy.ndimage import uniform_filter1d

ROOT = Path(__file__).resolve().parent
ASSETS, REPORTS = ROOT/'assets', ROOT/'reports'
RATE, DURATION = 48000, 29.8
SOURCE = Path('/workspace/attachments/8051fcae-5c5d-4373-b62b-ed831a2a8602/smooth_60fps.mp4')
ASR = ROOT.parents[1]/'docs/elite50/ad-remake-2026-10-28/evidence/source-asr-medium.json'
SEGMENTS = [(8.69, 10.65), (17.18, 19.53), (20.00, 41.70)]


def decode(path, channels=2):
    return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-ar',str(RATE),'-ac',str(channels),'-f','f32le','-']),dtype='<f4').reshape(-1,channels).copy()


def write(path,x):
    x = np.asarray(x).reshape(len(x),-1)
    subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(RATE),'-ac',str(x.shape[1]),'-i','-','-c:a','pcm_s24le',str(path)],input=x.astype('<f4').tobytes(),check=True)


def meter(path):
    r=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-af','loudnorm=I=-18.5:TP=-2.5:LRA=8:print_format=json','-f','null','-'],capture_output=True,check=True)
    text=r.stderr.decode();d=json.loads(text[text.rfind('{'):text.rfind('}')+1])
    return {'integratedLUFS':float(d['input_i']),'truePeakDBTP':float(d['input_tp']),'loudnessRangeLU':float(d['input_lra'])}


raw=decode(ASSETS/'source-vocals.wav').mean(axis=1)
parts=[];mapping=[];cursor=0
for start,end in SEGMENTS:
    x=raw[round(start*RATE):round(end*RATE)].copy()*.65
    edge=min(384,len(x)//4)
    x[:edge]*=np.linspace(0,1,edge);x[-edge:]*=np.linspace(1,0,edge)
    parts.append(x);mapping.append({'sourceStart':start,'sourceEnd':end,'outputStart':cursor,'outputEnd':cursor+len(x)/RATE})
    cursor+=len(x)/RATE
voice=np.pad(np.concatenate(parts),(0,round(DURATION*RATE)-sum(len(x) for x in parts)))
write(ASSETS/'voice-before-eq.wav',voice)
filters='highpass=f=65,equalizer=f=240:t=q:w=0.85:g=-1,equalizer=f=2800:t=q:w=0.85:g=0.8'
voice=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(ASSETS/'voice-before-eq.wav'),'-af',filters,'-ar',str(RATE),'-ac','1','-f','f32le','-']),dtype='<f4').copy()
write(ASSETS/'voice-clean.wav',voice)
m=meter(ASSETS/'voice-clean.wav');gain=min(-18.5-m['integratedLUFS'],-3-m['truePeakDBTP']);voice*=10**(gain/20)
write(ASSETS/'voice-clean.wav',np.repeat(voice[:,None],2,axis=1))

# Caption wording is editorially corrected against two machine transcripts and
# visible source text; estimated source word boundaries remain inspectable.
words=[]
for segment in json.loads(ASR.read_text())['segments']:
    for w in segment['words']:
        mid=(w['start']+w['end'])/2
        keep=next((s for s in mapping if s['sourceStart']<=mid<s['sourceEnd']),None)
        if not keep:continue
        text=w['word'].strip()
        if w['start']==9.32:text='قاعد'
        if w['start']==9.62:text='أتمرّن'
        if 28.34<=w['start']<28.78:continue
        if w['start']==28.08:text='كذا'
        if w['start']==38.48:text='امشِ'
        if w['start']==39.90:text='واعرف'
        if w['start']==41.26:text='صح'
        words.append({'text':text,'sourceStart':w['start'],'sourceEnd':w['end'],'start':max(0,keep['outputStart']+w['start']-keep['sourceStart']),'end':keep['outputStart']+w['end']-keep['sourceStart']})
intro=next(s for s in mapping if s['sourceStart']<28.5<s['sourceEnd'])
words.append({'text':'سوّينا','sourceStart':28.34,'sourceEnd':28.78,'start':intro['outputStart']+28.34-intro['sourceStart'],'end':intro['outputStart']+28.78-intro['sourceStart']})
words.sort(key=lambda w:w['start'])
groups=[];offset=0
# Complete readable phrases, avoiding a flashing one-word final caption.
sizes=[5,3,4,5,5,3,3,2,4,3,4,4,4,4]
assert sum(sizes)==len(words),(sum(sizes),len(words))
for size in sizes:
    current=words[offset:offset+size];offset+=size
    nxt=words[offset] if offset<len(words) else None
    end=min(nxt['start']-.05 if nxt else cursor+.05,current[-1]['end']+.16)
    groups.append({'start':max(0,current[0]['start']-.025),'end':max(end,current[0]['start']+.16),'words':current})
(ROOT/'words-final.json').write_text(json.dumps(words,ensure_ascii=False,indent=2)+'\n')
(ROOT/'captions.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2)+'\n')
def timestamp(t):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
(ROOT/'captions.srt').write_text('\n\n'.join(f'{i+1}\n{timestamp(g["start"])} --> {timestamp(g["end"])}\n'+ ' '.join(w['text'] for w in g['words']) for i,g in enumerate(groups))+'\n')

fx=np.zeros_like(voice);cues=[]
for t,name,duration,peak in [(2.08,'click-soft',.12,.028),(4.28,'pop',.14,.035),(6.44,'whoosh-short',.42,.055),(10.84,'click-soft',.15,.036),(14.37,'whoosh-short',.32,.045),(17.05,'click-soft',.13,.035),(20.08,'whoosh-short',.32,.045),(22.20,'click-soft',.12,.043),(25.52,'whoosh-short',.40,.055)]:
    x=decode(ASSETS/'sfx'/f'{name}.mp3',1)[:,0]
    active=np.flatnonzero(np.abs(x)>np.max(np.abs(x))*.04);first=max(0,int(active[0])-240) if len(active) else 0
    x=x[first:first+round(duration*RATE)].copy();x*=peak/max(np.max(np.abs(x)),1e-8)
    n=min(600,len(x)//4);x[:n]*=np.linspace(0,1,n);x[-n:]*=np.linspace(1,0,n)
    a=round(t*RATE);b=min(len(fx),a+len(x));fx[a:b]+=x[:b-a]
    cues.append({'time':t,'source':name+'.mp3','maxPeakBeforeDucking':peak,'seconds':len(x)/RATE})
speech=np.sqrt(uniform_filter1d(voice**2,size=round(.06*RATE)))
duck=np.clip(1-(speech-.025)/.1,.5,1)
fx*=duck
mix=voice+fx
assert np.max(np.abs(mix))<.95
write(ASSETS/'sfx-only.wav',np.repeat(fx[:,None],2,axis=1))
write(ASSETS/'final-mix.wav',np.repeat(mix[:,None],2,axis=1))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(ASSETS/'voice-clean.wav'),'-c:a','libmp3lame','-b:a','256k',str(ASSETS/'voice-clean.mp3')],check=True)
result={'sourceSha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'sourceNarrationPreserved':True,'sourceVocalSeparation':'reports/voice-separation.json','segments':mapping,'spokenEditSeconds':cursor,'duration':DURATION,'tailHoldSeconds':DURATION-cursor,'filters':filters,'voiceGainDB':gain,'voiceLoudness':meter(ASSETS/'voice-clean.wav'),'mixLoudness':meter(ASSETS/'final-mix.wav'),'effects':cues,'musicTrackAdded':False,'pitchChanged':False,'timeStretch':False,'compression':False,'synthesizedVoice':False,'clippedSamples':int(np.sum(np.abs(mix)>=1)),'captionGroups':len(groups),'captionWords':len(words),'captionLimits':'Machine word boundaries with editorial text corrections; human listening unavailable. Source fragments preserved for independent verification.','voiceRMS':float(np.sqrt(np.mean(voice**2))),'fxRMS':float(np.sqrt(np.mean(fx**2)))}
(REPORTS/'audio-edit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False),flush=True)
