"""Assemble native Saudi clips, provider word timings, and brief existing SFX."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import numpy as np
from scipy.ndimage import gaussian_filter1d

ROOT = Path(__file__).resolve().parent
RATE = 48000
ASSETS = ROOT / 'assets'
WORK = ASSETS / 'work'
WORK.mkdir(exist_ok=True)

def run(args, data=None):
    return subprocess.run(args, input=data, capture_output=True, check=True)

def decode(path, channels=1):
    return np.frombuffer(run(['ffmpeg', '-v', 'error', '-i', str(path), '-ac', str(channels),
        '-ar', str(RATE), '-f', 'f32le', '-']).stdout, dtype='<f4').copy().reshape(-1, channels)

def write(path, x):
    x = np.asarray(x).reshape(len(x), -1)
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(RATE), '-ac', str(x.shape[1]),
         '-i', '-', '-c:a', 'pcm_s24le', str(path)], x.astype('<f4').tobytes())

def meter(path):
    log = run(['ffmpeg', '-hide_banner', '-i', str(path), '-af',
        'loudnorm=I=-19.5:TP=-4:LRA=8:print_format=json', '-f', 'null', '-']).stderr.decode()
    m = json.loads(log[log.rfind('{'):log.rfind('}') + 1])
    return {a:float(m[b]) for a,b in [('integratedLUFS','input_i'),('truePeakDBTP','input_tp'),('loudnessRangeLU','input_lra')]}

def plain(text):
    return re.sub(r'[\u064b-\u065f\u0670ـ]', '', text)

script = json.loads((ROOT / 'script.json').read_text())
parts, words, beats, clips = [], [], [], []
cursor = 0
for item in script:
    source = ASSETS / 'voice' / (item['id'] + '.mp3')
    audio = decode(source)[:,0]
    native = [json.loads(x) for x in source.with_suffix('.jsonl').read_text().splitlines()]
    native = [x for x in native if x['type'] == 'WordBoundary']
    assert native
    events = [dict(text=plain(x['text']), start=x['offset']/1e7, end=(x['offset']+x['duration'])/1e7) for x in native]
    start = max(0, events[0]['start'] - .08)
    end = min(len(audio)/RATE, events[-1]['end'] + .18)
    # Only shorten unusually long punctuation gaps; protect all native word
    # intervals, including 160 ms after and 190 ms before their boundaries.
    cuts = [(a['end'] + .16, b['start'] - .19) for a,b in zip(events,events[1:]) if b['start'] - a['end'] > .60]
    keep, previous = [], start
    for lo,hi in cuts + [(end,end)]:
        if lo > previous:
            keep.append((round(previous*RATE),round(lo*RATE)))
        previous = hi
    chunk = []
    mapping = []
    local_cursor = 0
    for a,b in keep:
        x = audio[a:b].copy()
        # 3 ms edge smoothing only, no phoneme fades or denoising.
        n = min(144,len(x)//8)
        x[:n] *= np.linspace(0,1,n)
        x[-n:] *= np.linspace(1,0,n)
        chunk.append(x)
        mapping.append((a/RATE,b/RATE,local_cursor/RATE))
        local_cursor += len(x)
    x = np.concatenate(chunk)
    def mapped(t):
        for a,b,c in mapping:
            if t <= b:
                return c + max(0,t-a)
        return len(x)/RATE
    display_tokens = item['text'].split()
    assert len(display_tokens) == len(events), (item,events)
    for event, authored in zip(events,display_tokens):
        normalized = lambda t:re.sub(r'[^\w]', '', plain(t))
        assert normalized(event['text']) == normalized(authored), (event,authored)
        words.append({'text':plain(authored),'start':round(cursor/RATE+mapped(event['start']),5),
                      'end':round(cursor/RATE+mapped(event['end']),5),'scene':item['id'],
                      'providerStart':event['start'],'providerEnd':event['end']})
    # A readable scene minimum; extra CTA hold gives the shop URL time to land.
    minimum = 3.9 if item['id']=='s14' else 1.95
    if len(x)/RATE < minimum:
        x = np.pad(x,(0,round(minimum*RATE)-len(x)))
    beats.append({'id':item['id'],'start':cursor/RATE,'end':(cursor+len(x))/RATE})
    clips.append({'id':item['id'],'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                  'nativeWords':len(events),'cuts':cuts,'keptMappings':mapping,'seconds':len(x)/RATE})
    parts.append(x)
    cursor += len(x)

speech = np.concatenate(parts)
# Native new narrator. No pitch-shifter, time-stretcher, WPE, noise gate,
# exciter, stereo doubler, de-esser or compression. One static level correction.
voice = np.repeat(speech[:,None],2,axis=1)
write(ASSETS/'voice-clean.wav',voice)
before = meter(ASSETS/'voice-clean.wav')
gain = min(-19.5-before['integratedLUFS'],-4.5-before['truePeakDBTP'])
voice *= 10**(gain/20)
write(ASSETS/'voice-clean.wav',voice)
speech = voice[:,0]
timeline = {'duration':len(speech)/RATE,'beats':beats,'clips':clips,'wordCount':len(words)}
(ROOT/'reports/voice-timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2)+'\n')
(ROOT/'words-final.json').write_text(json.dumps(words,ensure_ascii=False,indent=2)+'\n')
(ROOT/'SCRIPT.md').write_text('# التعليق السعودي الجديد\n\n'+'\n\n'.join(plain(x['text']) for x in script)+'\n')

# Reuse the same short SFX family. Keep them out of the main consonant band,
# and duck the effects (never the voice) during active speech.
by_id = {b['id']:b for b in beats}
plan = [('pop','s0',.38,.20,-32,-17),('whoosh-short','s1',.14,.36,-30,-16),
 ('click','s2',.40,.15,-31,-16),('click-soft','s3',.43,.17,-31,-16),
 ('pop','s4',.49,.20,-31,-16),('pop','s4',.88,.20,-33,-18),
 ('whoosh-short','s5',.10,.35,-30,-16),('click-soft','s6',.36,.17,-32,-17),
 ('pop','s7',.90,.22,-32,-17),('whoosh-short','s8',.12,.39,-28,-14),
 ('click','s9',.43,.16,-30,-16),('click','s10',.48,.16,-30,-16),
 ('click-soft','s11',.42,.17,-30,-16),('whoosh-short','s12',.13,.36,-30,-16),
 ('click','s12',1.78,.16,-29,-15),('whoosh-short','s14',.12,.40,-28,-14)]
fx = np.zeros_like(voice)
envelope = np.sqrt(gaussian_filter1d(speech**2,sigma=480)+1e-12)
duck = 10**(-4*np.clip((envelope-.025)/.07,0,1)/20)
cues = []
for name,scene,offset,cap,target_db,peak_db in plan:
    data = run(['ffmpeg','-v','error','-i',str(ASSETS/'sfx'/f'{name}.mp3'),'-af',
        'highpass=f=150,lowpass=f=8500,equalizer=f=2500:t=q:w=0.75:g=-3',
        '-ar',str(RATE),'-ac','1','-f','f32le','-']).stdout
    x = np.frombuffer(data,dtype='<f4').copy()
    ids = np.flatnonzero(np.abs(x)>np.max(np.abs(x))*.025)
    a = max(0,int(ids[0])-288)
    b = min(len(x),int(ids[-1])+1440,a+round(cap*RATE))
    x = x[a:b].copy()
    n,m = min(96,len(x)//8),min(720,len(x)//6)
    x[:n] *= np.linspace(0,1,n)
    x[-m:] *= np.linspace(1,0,m)
    x *= 10**(target_db/20)/max(np.sqrt(np.mean(x*x)),1e-9)
    ceiling = 10**(peak_db/20)
    x = ceiling*np.tanh(x/ceiling)
    t = by_id[scene]['start']+offset
    a = round(t*RATE); b = min(len(speech),a+len(x))
    x = x[:b-a]*duck[a:b]
    fx[a:b] += x[:,None]
    cues.append({'scene':scene,'time':t,'source':name,'seconds':len(x)/RATE,
                 'rmsDBFS':float(20*np.log10(np.sqrt(np.mean(x*x))+1e-12))})
mix = voice + fx
assert np.max(np.abs(mix)) < .9
write(ASSETS/'final-mix.wav',mix)
final = meter(ASSETS/'final-mix.wav')
assert final['integratedLUFS'] < -19 and final['truePeakDBTP'] < -3
run(['ffmpeg','-v','error','-y','-i',str(ASSETS/'voice-clean.wav'),'-c:a','libmp3lame','-b:a','256k',str(ASSETS/'voice-clean.mp3')])
report = {'voiceReplaced':True,'voice':'ar-SA-HamedNeural','humanRecording':False,
          'pitchProcessing':False,'postSynthesisTimeStretch':False,'denoising':False,'dereverb':False,
          'compression':False,'eq':False,'voiceStaticGainDB':gain,'nativeLoudness':before,
          'voiceLoudness':meter(ASSETS/'voice-clean.wav'),'finalMixLoudness':final,
          'effects':cues,'musicAdded':False,'clippedSamples':int(np.sum(np.abs(mix)>=1)),
          'note':'Fresh authorized Saudi catalog narration. No old recording or voice clone in the output.'}
(ROOT/'reports/audio-revision.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'seconds':len(speech)/RATE,'words':len(words),'scenes':len(beats),'loudness':final}))
