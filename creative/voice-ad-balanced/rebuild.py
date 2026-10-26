"""V8 audio-only revision. Input: original upload; visuals: exact V7 bitstream."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess

# Small deterministic CPU workload; avoid large BLAS thread pools for WPE.
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import butter, sosfilt
from nara_wpe.utils import stft, istft
from nara_wpe.wpe import wpe_v7

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'voice-ad-smooth'
RATE = 48000
ASSETS = ROOT / 'assets'
WORK = ASSETS / 'work'
REPORTS = ROOT / 'reports'
for d in [ASSETS, WORK, REPORTS, ROOT / 'renders']:
    d.mkdir(parents=True, exist_ok=True)


def run(args, data=None):
    return subprocess.run(args, input=data, capture_output=True, check=True)


def decode(path, stereo=False):
    channels = 2 if stereo else 1
    out = run(['ffmpeg', '-v', 'error', '-i', str(path), '-ac', str(channels),
               '-ar', str(RATE), '-f', 'f32le', '-']).stdout
    return np.frombuffer(out, dtype='<f4').copy().reshape(-1, channels)


def write(path, samples):
    samples = np.asarray(samples).reshape(len(samples), -1)
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(RATE),
         '-ac', str(samples.shape[1]), '-i', '-', '-c:a', 'pcm_s24le', str(path)],
        samples.astype('<f4').tobytes())


def meter(path):
    log = run(['ffmpeg', '-hide_banner', '-i', str(path), '-af',
               'loudnorm=I=-19.5:TP=-3:LRA=7:print_format=json', '-f', 'null', '-']).stderr.decode()
    data = json.loads(log[log.rfind('{'):log.rfind('}') + 1])
    return {k: float(data[v]) for k, v in
            [('integratedLUFS', 'input_i'), ('truePeakDBTP', 'input_tp'), ('loudnessRangeLU', 'input_lra')]}


def normalize(samples, target, path, peak_ceiling=-4):
    write(path, samples)
    before = meter(path)
    gain = min(target - before['integratedLUFS'], peak_ceiling - before['truePeakDBTP'])
    samples = samples * 10 ** (gain / 20)
    write(path, samples)
    return samples, {'before': before, 'gainDB': gain, 'after': meter(path)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    original = decode(args.source, stereo=True).mean(axis=1) * .60
    original_hash = hashlib.sha256(args.source.read_bytes()).hexdigest()
    edit = json.loads((BASE / 'reports/audio-edit.json').read_text())
    assert original_hash == edit['sourceSha256'], 'Use the unchanged original upload.'

    # Estimate late reflections before the timeline is cut, then blend modestly.
    # No hard noise gate or FFT subtraction: avoid watery consonant artifacts.
    spectrum = stft(original, size=1536, shift=384)
    reconstructed = istft(spectrum, size=1536, shift=384)[:len(original)]
    assert np.max(np.abs(reconstructed - original)) < 1e-5
    result = wpe_v7(spectrum.T[:, None, :], taps=10, delay=4, iterations=3)
    dereverb = istft(result[:, 0, :].T, size=1536, shift=384)[:len(original)]
    assert np.isfinite(dereverb).all()
    cleaned = .70 * original + .30 * dereverb
    parts = []
    for s in edit['keptSegments']:
        part = cleaned[round(s['sourceStart'] * RATE):round(s['sourceEnd'] * RATE)].copy()
        fade = min(288, len(part) // 4)
        part[:fade] *= np.linspace(0, 1, fade)
        part[-fade:] *= np.linspace(1, 0, fade)
        parts.append(part)
    speech = np.concatenate(parts)
    assert len(speech) == round(edit['editedSeconds'] * RATE)
    write(WORK / 'dry.wav', speech)

    # A small timbre change, not another speaker; no change of playback rate.
    pitch = 2 ** (.35 / 12)
    chain = ','.join([
        'highpass=f=95',
        'equalizer=f=190:t=q:w=0.8:g=-2.5',
        'equalizer=f=430:t=q:w=0.75:g=-3.5',
        'equalizer=f=1300:t=q:w=1.2:g=1.0',
        'equalizer=f=2800:t=q:w=0.85:g=2.0',
        'highshelf=f=4200:g=3.5',
        'lowpass=f=14000',
        f'rubberband=tempo=1:pitch={pitch:.10f}:transients=smooth:detector=soft:phase=laminar:formant=preserved:pitchq=quality',
        'deesser=i=0.12:m=0.18:f=0.55',
        'acompressor=threshold=0.10:ratio=2.2:attack=4:release=100:knee=2.8:makeup=1',
    ])
    processed = run(['ffmpeg', '-v', 'error', '-i', str(WORK / 'dry.wav'), '-af', chain,
                     '-ar', str(RATE), '-ac', '1', '-f', 'f32le', '-']).stdout
    speech = np.frombuffer(processed, dtype='<f4').copy()
    speech = np.pad(speech, (0, max(0, round(edit['editedSeconds'] * RATE) - len(speech))))[:round(edit['editedSeconds'] * RATE)]

    # Smooth phrase-level ride, bounded to +/-1.8 dB. No pumping in silences.
    block = 480
    centers = np.arange(0, len(speech), block)
    rms = np.array([np.sqrt(np.mean(speech[a:min(a + 24000, len(speech))] ** 2) + 1e-12) for a in centers])
    active = rms > .025
    target = np.median(rms[active])
    gain_db = np.clip(20 * np.log10(target / np.maximum(rms, .01)), -1.8, 1.8)
    gain_db[~active] = 0
    gain_db = gaussian_filter1d(gain_db, sigma=16)
    speech *= 10 ** (np.interp(np.arange(len(speech)), centers, gain_db) / 20)
    # Explicit identical channels: FFmpeg's default equal-power mono upmix would
    # change the gain by 3 dB. Measure the actual delivery format instead.
    voice = np.repeat(speech[:, None], 2, axis=1)
    voice, voice_meter = normalize(voice, -19.5, ASSETS / 'voice-clean.wav', peak_ceiling=-5)
    speech = voice[:, 0]

    beats = {b['id']: b for b in json.loads((BASE / 'beats.json').read_text())['beats']}
    # name, scene, offset, duration cap, target active RMS, peak cap, stereo pan.
    # Existing licensed library only. No risers, melodic bed or music.
    plan = [
        ('pop', 's0', .38, .20, -32, -17, -.12),
        ('whoosh-short', 's1', .14, .36, -30, -16, .15),
        ('click', 's2', .40, .15, -31, -16, 0),
        ('click-soft', 's3', .43, .17, -31, -16, -.12),
        ('pop', 's4', .49, .20, -31, -16, .14),
        ('pop', 's4', .88, .20, -33, -18, -.14),
        ('whoosh-short', 's5', .10, .35, -30, -16, -.12),
        ('click-soft', 's6', .36, .17, -32, -17, .10),
        ('pop', 's7', .90, .22, -32, -17, 0),
        ('whoosh-short', 's8', .12, .39, -28, -14, 0),
        ('click', 's9', .43, .16, -30, -16, -.14),
        ('click', 's10', .48, .16, -30, -16, .14),
        ('click-soft', 's11', .42, .17, -30, -16, -.10),
        ('whoosh-short', 's12', .13, .36, -30, -16, .12),
        ('click', 's12', 1.78, .16, -29, -15, 0),
        ('whoosh-short', 's14', .12, .40, -28, -14, 0),
    ]
    effects = np.zeros_like(voice)
    envelope = np.sqrt(gaussian_filter1d(speech ** 2, sigma=480) + 1e-12)
    # Smooth speech-aware reduction up to 3 dB on the FX only.
    duck = 10 ** (-3 * np.clip((envelope - .025) / .07, 0, 1) / 20)
    cues = []
    for name, scene, offset, cap, target_db, peak_db, pan in plan:
        x = decode(ASSETS / 'sfx' / f'{name}.mp3').mean(axis=1)
        x = sosfilt(butter(2, [150, 8500], btype='bandpass', fs=RATE, output='sos'), x)
        # Carve a little of the intelligibility band out of effects, not speech.
        write(WORK / 'effect.wav', x)
        x = np.frombuffer(run(['ffmpeg', '-v', 'error', '-i', str(WORK / 'effect.wav'),
                '-af', 'equalizer=f=2500:t=q:w=0.75:g=-3', '-f', 'f32le', '-']).stdout, dtype='<f4').copy()
        ids = np.flatnonzero(np.abs(x) > np.max(np.abs(x)) * .025)
        first = max(0, int(ids[0]) - 288)
        last = min(len(x), int(ids[-1]) + 1440, first + round(cap * RATE))
        x = x[first:last].copy()
        fade_in = min(96, len(x) // 8)
        fade_out = min(720, len(x) // 6)
        x[:fade_in] *= np.linspace(0, 1, fade_in)
        x[-fade_out:] *= np.linspace(1, 0, fade_out)
        x *= 10 ** (target_db / 20) / max(np.sqrt(np.mean(x ** 2)), 1e-9)
        # Soft transient control on effects only; normalize AFTER fades so the
        # click attack remains audible. Keep the specified cap even in gaps.
        ceiling = 10 ** (peak_db / 20)
        x = ceiling * np.tanh(x / ceiling)
        cue_time = beats[scene]['start'] + offset
        a = round(cue_time * RATE)
        b = min(len(speech), a + len(x))
        x = x[:b - a] * duck[a:b]
        cue_stereo = x[:, None] * np.array([1 - pan, 1 + pan])[None, :]
        effects[a:b] += cue_stereo
        cues.append({'scene': scene, 'time': cue_time, 'file': name,
            'seconds': len(x) / RATE, 'pan': pan,
            'actualRmsDBFS': float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)),
            'actualPeakDBFS': float(20 * np.log10(np.max(np.abs(x)) + 1e-12))})

    write(ASSETS / 'sfx-only.wav', effects)
    # Never raise the master to chase the old social-loudness target.
    mix = voice + effects
    write(ASSETS / 'final-mix.wav', mix)
    final_meter = meter(ASSETS / 'final-mix.wav')
    assert final_meter['integratedLUFS'] <= -19.0, final_meter
    assert final_meter['truePeakDBTP'] < -3, final_meter
    assert np.max(np.abs(mix)) < .9
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(ASSETS / 'voice-clean.wav'),
         '-c:a', 'libmp3lame', '-b:a', '256k', str(ASSETS / 'voice-clean.mp3')])

    # No video re-render: guarantee v7 motion, frame timing and captions stay exact.
    video = BASE / 'renders/mdaar_tiktok_v7_60fps.mp4'
    if not video.exists():
        video = ROOT.parents[1] / 'public/ad/voice-smooth/mdaar_tiktok_v7_60fps.mp4'
    output = ROOT / 'renders/mdaar_tiktok_v8_balanced.mp4'
    run(['ffmpeg', '-v', 'error', '-y', '-i', str(video), '-i', str(ASSETS / 'final-mix.wav'),
         '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k',
         '-ar', str(RATE), '-movflags', '+faststart', str(output)])
    report = {'sourceSha256': original_hash, 'visualMasterSha256': hashlib.sha256(video.read_bytes()).hexdigest(),
        'sourceUnchanged': True, 'timelineCopiedFrom': '../voice-ad-smooth/reports/audio-edit.json',
        'seconds': len(speech) / RATE, 'speechSpeedChanged': False, 'voiceReplaced': False,
        'pitchSemitones': .35, 'formantsPreserved': True,
        'dereverb': {'engine': 'nara-wpe 0.0.11', 'wetFraction': .30, 'taps': 10, 'delay': 4,
                     'fftSize': 1536, 'hop': 384, 'iterations': 3},
        'filters': chain, 'phraseRideMaxDB': 1.8, 'voiceLoudness': voice_meter,
        'finalMixLoudness': final_meter, 'v7Loudness': meter(BASE / 'assets/final-mix.wav'),
        'musicAdded': False, 'reverbAdded': False, 'effects': cues,
        'peakPCM': float(np.max(np.abs(mix))), 'clippedSamples': int(np.sum(np.abs(mix) >= 1)),
        'note': 'Signal validation, not human listening certification. No speech synthesis or claimed recovery of lost source details.'}
    (REPORTS / 'audio-revision.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'voice': voice_meter['after'], 'mix': final_meter, 'effects': len(cues), 'output': str(output)}))


if __name__ == '__main__':
    main()
