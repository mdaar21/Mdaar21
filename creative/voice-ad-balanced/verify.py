"""Validate delivered bytes, retained visuals, audio timing and mix safety."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess

import numpy as np
from scipy.signal import correlate, correlation_lags, welch
from scipy.ndimage import gaussian_filter1d

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'voice-ad-smooth'
PUBLIC = ROOT.parents[1] / 'public/ad/voice-balanced'
MOVIE = PUBLIC / 'mdaar_tiktok_v8_balanced.mp4'
RATE = 16000


def run(args):
    return subprocess.run(args, capture_output=True, check=True)


def decode(path):
    return np.frombuffer(run(['ffmpeg', '-v', 'error', '-i', str(path), '-ac', '1',
                             '-ar', str(RATE), '-f', 'f32le', '-']).stdout, dtype='<f4').copy()


def video_hash(path):
    return run(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:v:0',
                '-c:v', 'copy', '-f', 'hash', '-hash', 'sha256', '-']).stdout.decode().strip()


def meter(path):
    s = run(['ffmpeg', '-hide_banner', '-i', str(path), '-af',
             'loudnorm=I=-19.5:TP=-3:LRA=7:print_format=json', '-f', 'null', '-']).stderr.decode()
    d = json.loads(s[s.rfind('{'):s.rfind('}') + 1])
    return {'integratedLUFS': float(d['input_i']), 'truePeakDBTP': float(d['input_tp'])}


info = json.loads(run(['ffprobe', '-v', 'error', '-show_entries',
    'format=duration,size:stream=codec_name,width,height,r_frame_rate,sample_rate,channels,duration',
    '-of', 'json', str(MOVIE)]).stdout)
assert info['streams'][0]['width'] == 1080
assert info['streams'][0]['height'] == 1920
assert info['streams'][0]['r_frame_rate'] == '60/1'
assert info['streams'][1]['channels'] == 2
assert abs(float(info['format']['duration']) - 39.116667) < .025
assert MOVIE.stat().st_size < 40 * 1024 * 1024

baseline = BASE / 'renders/mdaar_tiktok_v7_60fps.mp4'
if not baseline.exists():
    baseline = ROOT.parents[1] / 'public/ad/voice-smooth/mdaar_tiktok_v7_60fps.mp4'
hashes = [video_hash(p) for p in [baseline, MOVIE]]
assert hashes[0] == hashes[1], 'V7 video bitstream must be preserved exactly.'
for name in ['words-final.json', 'beats.json', 'captions.srt']:
    assert (ROOT / name).read_bytes() == (BASE / name).read_bytes()
assert (PUBLIC / 'captions.srt').read_bytes() == (BASE / 'captions.srt').read_bytes()

master = decode(ROOT / 'assets/final-mix.wav')
encoded = decode(MOVIE)
n = min(len(master), len(encoded))
corr = float(np.corrcoef(master[:n], encoded[:n])[0, 1])
assert corr > .985
assert abs(len(master) - len(encoded)) / RATE < .04
mix_meter = meter(MOVIE)
v7_meter = meter(baseline)
assert v7_meter['integratedLUFS'] - mix_meter['integratedLUFS'] >= 5
assert mix_meter['truePeakDBTP'] < -3
assert np.max(np.abs(encoded)) < .9

voice = decode(ROOT / 'assets/voice-clean.wav')
previous = decode(BASE / 'assets/voice-clean.mp3')
assert len(previous) == len(voice)
def presence_ratio(samples):
    f, s = welch(samples, RATE, nperseg=2048)
    return float(10 * np.log10(sum(s[(f > 2000) & (f < 7000)]) / sum(s[(f > 150) & (f < 700)])))
bands = {'v7PresenceToLowMidDB': presence_ratio(previous), 'v8PresenceToLowMidDB': presence_ratio(voice)}
assert bands['v8PresenceToLowMidDB'] > bands['v7PresenceToLowMidDB'] + 2

# Intensity envelope alignment checks for drift or a pitch-shifter latency.
# Timbre and pitch differ deliberately, so don't require sample-phase equality.
envelopes = [np.sqrt(gaussian_filter1d(x ** 2, sigma=80))[::16] for x in [previous, voice]]
sync = []
for start in [0, 7, 14, 21, 28, 34]:
    a, b = [x[round(start * 1000):round(min(start + 5, len(voice) / RATE) * 1000)] for x in envelopes]
    a = a - np.mean(a)
    b = b - np.mean(b)
    c = correlate(b, a)
    lags = correlation_lags(len(b), len(a))
    selected = np.abs(lags) < 120
    lag = int(lags[selected][np.argmax(c[selected])])
    assert abs(lag) <= 30, (start, lag)
    sync.append({'startSeconds': start, 'envelopeLagMs': lag})

fx = decode(ROOT / 'assets/sfx-only.wav')
audio = json.loads((ROOT / 'reports/audio-revision.json').read_text())
assert len(audio['effects']) == 16
assert not audio['musicAdded'] and not audio['reverbAdded']
assert audio['clippedSamples'] == 0
fx_active = []
for cue in audio['effects']:
    a = round(cue['time'] * RATE)
    b = round((cue['time'] + cue['seconds']) * RATE)
    fx_active.append({'scene': cue['scene'], 'rmsDBFS': float(20 * np.log10(np.sqrt(np.mean(fx[a:b] ** 2)) + 1e-12))})
assert max(x['rmsDBFS'] for x in fx_active) > -31

raw = MOVIE.read_bytes()
pos = 0
atoms = []
while pos + 8 <= len(raw):
    length, kind = struct.unpack('>I4s', raw[pos:pos + 8])
    if length == 1:
        length = struct.unpack('>Q', raw[pos + 8:pos + 16])[0]
    length = length or len(raw) - pos
    atoms.append(kind.decode(errors='replace'))
    pos += length
assert atoms.index('moov') < atoms.index('mdat')

report = {'ok': True, 'metadata': info, 'fileSha256': hashlib.sha256(raw).hexdigest(),
    'videoElementaryStreamHashes': hashes, 'visualsIdenticalToV7': True,
    'captionsAndWordTimingsUnchanged': True, 'encodedAudioCorrelationWithMaster': corr,
    'v7EncodedLoudness': v7_meter, 'v8EncodedLoudness': mix_meter,
    'levelReductionLU': v7_meter['integratedLUFS'] - mix_meter['integratedLUFS'],
    'bandEnergy': bands, 'timingChecks': sync, 'effects': fx_active,
    'clippedSamples': 0, 'faststart': True, 'musicAdded': False,
    'limits': 'Signal and delivery checks; no human listening certification, clinical intelligibility test or campaign validation.'}
(ROOT / 'reports/validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'ok': True, 'encodedLoudness': mix_meter, 'bandEnergy': bands, 'sync': sync}))
