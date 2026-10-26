"""Return to the owner's original recording, using only gentle corrective EQ."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import numpy as np

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent/'voice-ad-smooth'
ASSETS = ROOT/'assets'
RATE = 48000
WORK = ASSETS/'work'
WORK.mkdir(exist_ok=True)

def run(args, data=None):
    return subprocess.run(args,input=data,capture_output=True,check=True)

def write(path, data):
    data = np.asarray(data).reshape(len(data),-1)
    run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(RATE),'-ac',str(data.shape[1]),
         '-i','-','-c:a','pcm_s24le',str(path)],data.astype('<f4').tobytes())

def meter(path):
    s = run(['ffmpeg','-hide_banner','-i',str(path),'-af',
        'loudnorm=I=-19.5:TP=-4:LRA=8:print_format=json','-f','null','-']).stderr.decode()
    d = json.loads(s[s.rfind('{'):s.rfind('}')+1])
    return {k:float(d[v]) for k,v in [('integratedLUFS','input_i'),('truePeakDBTP','input_tp'),('loudnessRangeLU','input_lra')]}

parser = argparse.ArgumentParser()
parser.add_argument('source',type=Path)
args = parser.parse_args()
edit = json.loads((BASE/'reports/audio-edit.json').read_text())
source_hash = hashlib.sha256(args.source.read_bytes()).hexdigest()
assert source_hash == edit['sourceSha256']
raw = np.frombuffer(run(['ffmpeg','-v','error','-i',str(args.source),'-ar',str(RATE),
    '-ac','2','-f','f32le','-']).stdout,dtype='<f4').reshape(-1,2).mean(axis=1)
parts = []
for segment in edit['keptSegments']:
    x = raw[round(segment['sourceStart']*RATE):round(segment['sourceEnd']*RATE)].copy()*.60
    n = min(288,len(x)//4)
    x[:n] *= np.linspace(0,1,n)
    x[-n:] *= np.linspace(1,0,n)
    parts.append(x)
dry = np.concatenate(parts)
assert len(dry) == round(edit['editedSeconds']*RATE)
write(WORK/'dry.wav',dry)

# Three mild filters, deliberately avoiding the pitch-shifter, WPE, de-esser,
# spectral cleanup and compression used in earlier experiments.
filters = 'highpass=f=70,equalizer=f=250:t=q:w=0.85:g=-1.5,equalizer=f=2600:t=q:w=0.85:g=1.5'
filtered = np.frombuffer(run(['ffmpeg','-v','error','-i',str(WORK/'dry.wav'),'-af',filters,
    '-ar',str(RATE),'-ac','1','-f','f32le','-']).stdout,dtype='<f4').copy()
assert len(filtered) == len(dry)
voice = np.repeat(filtered[:,None],2,axis=1)
write(ASSETS/'voice-clean.wav',voice)
before = meter(ASSETS/'voice-clean.wav')
gain = min(-19.5-before['integratedLUFS'],-4.5-before['truePeakDBTP'])
voice *= 10**(gain/20)
write(ASSETS/'voice-clean.wav',voice)
fx = np.frombuffer(run(['ffmpeg','-v','error','-i',str(ASSETS/'effects-v8.flac'),
    '-ar',str(RATE),'-ac','2','-f','f32le','-']).stdout,dtype='<f4').copy().reshape(-1,2)
assert fx.shape == voice.shape
mix = voice+fx
assert np.max(np.abs(mix)) < .9
write(ASSETS/'final-mix.wav',mix)
delivery = meter(ASSETS/'final-mix.wav')
assert delivery['integratedLUFS'] < -19 and delivery['truePeakDBTP'] < -3
run(['ffmpeg','-v','error','-y','-i',str(ASSETS/'voice-clean.wav'),'-c:a','libmp3lame',
    '-b:a','256k',str(ASSETS/'voice-clean.mp3')])

video = BASE/'renders/mdaar_tiktok_v7_60fps.mp4'
if not video.exists():
    video = ROOT.parents[1]/'public/ad/voice-smooth/mdaar_tiktok_v7_60fps.mp4'
run(['ffmpeg','-v','error','-y','-i',str(video),'-i',str(ASSETS/'final-mix.wav'),
     '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k',
     '-movflags','+faststart',str(ROOT/'renders/mdaar_tiktok_v10_original_clear.mp4')])
report = {'sourceSha256':source_hash,'originalRecordingUsed':True,'voiceReplaced':False,
    'voiceCloned':False,'synthesizedSpeech':False,'pitchChanged':False,'timeStretch':False,
    'dereverb':False,'noiseGate':False,'spectralDenoising':False,'compression':False,
    'filters':filters,'headroomGainBeforePCM':.6,'voiceStaticGainDB':gain,
    'voiceLoudness':meter(ASSETS/'voice-clean.wav'),'mixLoudness':delivery,
    'seconds':len(dry)/RATE,'visualMasterSha256':hashlib.sha256(video.read_bytes()).hexdigest(),
    'visualStreamCopied':True,'wordsAndCaptionsFrom':'../voice-ad-smooth/',
    'effectsStem':'assets/effects-v8.flac','effectsStemSha256':hashlib.sha256((ASSETS/'effects-v8.flac').read_bytes()).hexdigest(),
    'effectsCount':16,'musicAdded':False,'clippedSamples':int(np.sum(np.abs(mix)>=1)),
    'limits':'Corrective EQ and level adjustment preserve the recorded speaker. Objective validation is not a human listening test or a guarantee of restored lost source detail.'}
(ROOT/'reports/audio-revision.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'seconds':len(dry)/RATE,'voice':report['voiceLoudness'],'mix':delivery}))
