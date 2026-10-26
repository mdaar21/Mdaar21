from pathlib import Path
import argparse, json, hashlib, subprocess, re
import numpy as np

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);args=parser.parse_args()
rate=48000
def run(argv):return subprocess.run(argv,capture_output=True,check=True)
# Equal-power downmix can add 3 dB for identical stereo channels. Average instead,
# and keep headroom before the first integer PCM export, not after a clipped file.
raw=np.frombuffer(run(['ffmpeg','-v','error','-i',str(args.source),'-af','pan=mono|c0=0.5*c0+0.5*c1','-ar',str(rate),'-f','f32le','-']).stdout,dtype='<f4').copy()
duration=len(raw)/rate
det=run(['ffmpeg','-hide_banner','-i',str(args.source),'-af','silencedetect=noise=-28dB:d=0.30','-f','null','-']).stderr.decode()
(ROOT/'reports/silence-detection.txt').write_text(det)
gaps=[];a=None
for kind,value in re.findall(r'silence_(start|end): ([0-9.]+)',det):
    if kind=='start':a=float(value)
    elif a is not None:gaps.append((a,float(value)));a=None
words=json.loads((ROOT/'baseline/words-v6.json').read_text())
protected=[(max(0,w['sourceStart']-.035),min(duration,w['sourceEnd']+.035)) for w in words]
cuts=[]
for a,b in gaps:
    possible=(a+.13,b-.13) if a>.02 else (0,b-.10)
    if possible[1]<=possible[0]:continue
    pieces=[possible]
    for x,y in protected:
        next_pieces=[]
        for lo,hi in pieces:
            if y<=lo or x>=hi:next_pieces.append((lo,hi));continue
            if lo<x:next_pieces.append((lo,x))
            if hi>y:next_pieces.append((y,hi))
        pieces=next_pieces
    for lo,hi in pieces:
        if hi-lo>=.09:cuts.append((lo,hi))
cuts.sort()
segments=[];previous=0;cursor=0
for a,b in cuts+[(duration,duration)]:
    if a>previous:
        lo,hi=round(previous*rate),round(a*rate);length=(hi-lo)/rate
        segments.append({'sourceStart':lo/rate,'sourceEnd':hi/rate,'outputStart':cursor,'outputEnd':cursor+length});cursor+=length
    previous=b
parts=[]
for s in segments:
    x=raw[round(s['sourceStart']*rate):round(s['sourceEnd']*rate)].copy()*.60
    n=min(288,len(x)//4)
    x[:n]*=np.linspace(0,1,n);x[-n:]*=np.linspace(1,0,n);parts.append(x)
edited=np.concatenate(parts)
assert np.max(np.abs(edited))<.9
dry=ROOT/'assets/voice-edited.wav'
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(rate),'-ac','1','-i','-','-c:a','pcm_s24le',str(dry)],input=edited.astype('<f4').tobytes(),check=True)
chain='highpass=f=85,lowpass=f=15000,equalizer=f=280:t=q:w=0.75:g=-2.8,equalizer=f=1600:t=q:w=0.9:g=1.2,equalizer=f=3200:t=q:w=0.8:g=3,acompressor=threshold=0.18:ratio=1.45:attack=10:release=120:makeup=1'
first=run(['ffmpeg','-hide_banner','-i',str(dry),'-af',chain+',loudnorm=I=-14:TP=-1.5:LRA=8:print_format=json','-f','null','-']).stderr.decode()
measured=json.loads(first[first.rfind('{'):first.rfind('}')+1])
normal='loudnorm=I=-14:TP=-1.5:LRA=8:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}:linear=true:print_format=json'.format(**measured)
r=run(['ffmpeg','-hide_banner','-y','-i',str(dry),'-af',chain+','+normal,'-ar',str(rate),'-c:a','pcm_s24le',str(ROOT/'assets/voice-clean.wav')])
(ROOT/'reports/cleanup-ffmpeg.txt').write_text(r.stderr.decode())
run(['ffmpeg','-v','error','-y','-i',str(ROOT/'assets/voice-clean.wav'),'-c:a','libmp3lame','-b:a','256k',str(ROOT/'assets/voice-clean.mp3')])
def mapped(t):
    for s in segments:
        if t<=s['sourceEnd']:return s['outputStart']+max(0,t-s['sourceStart'])
    return len(edited)/rate
for w in words:w.update(start=round(mapped(w['sourceStart']),4),end=round(mapped(w['sourceEnd']),4))
(ROOT/'words-final.json').write_text(json.dumps(words,ensure_ascii=False,indent=2)+'\n')
report={'sourceSha256':hashlib.sha256(args.source.read_bytes()).hexdigest(),'sourceSeconds':duration,'editedSeconds':len(edited)/rate,'removedSeconds':duration-len(edited)/rate,'removedIntervals':cuts,'keptSegments':segments,'protectedWordMarginMs':35,'dryPrePcmPeak':float(np.max(np.abs(edited))),'dryPrePcmClippedSamples':int(np.sum(np.abs(edited)>=1)),'downmix':'Arithmetic channel mean, not equal-power sum','headroomGain':.60,'filters':chain,'loudnessTarget':{'integratedLUFS':-14,'truePeakDBTP':-1.5},'firstPass':measured,'voiceReplaced':False,'speechSpeedChanged':False,'musicAdded':False,'spectralNoiseGate':False,'allCutsOutsideProtectedWords':True}
(ROOT/'reports/audio-edit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['editedSeconds','removedSeconds','dryPrePcmPeak','dryPrePcmClippedSamples']}))
