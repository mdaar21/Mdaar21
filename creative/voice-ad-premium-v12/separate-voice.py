"""Local MDX-Net vocal stem extraction from the authorized uploaded video.

Uses downloaded Kim_Vocal_2 ONNX weights, CPU ONNX Runtime and NumPy/SciPy
STFT. Model separation is not a human listening certification.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import time
import numpy as np
from scipy.signal.windows import hann, tukey
import onnxruntime as ort

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
REPORTS = ROOT / 'reports'
ASSETS.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)
SOURCE = Path('/workspace/attachments/8051fcae-5c5d-4373-b62b-ed831a2a8602/smooth_60fps.mp4')
MODEL = Path('/tmp/mdaar-v12-models/Kim_Vocal_2.onnx')
RATE, FFT, HOP, FRAMES, DIMF = 44100, 7680, 1024, 256, 3072
LENGTH = (FRAMES - 1) * HOP
WINDOW = hann(FFT, sym=False).astype(np.float32)


def stft(x):
    padded = np.pad(x, ((0, 0), (FFT // 2, FFT // 2)), mode='reflect')
    framed = np.lib.stride_tricks.sliding_window_view(padded, FFT, axis=-1)[:, ::HOP]
    return np.fft.rfft(framed * WINDOW, axis=-1).transpose(0, 2, 1)


def istft(z):
    frames = np.fft.irfft(z.transpose(0, 2, 1), n=FFT, axis=-1).real * WINDOW
    y = np.zeros((2, HOP * (frames.shape[1] - 1) + FFT), dtype=np.float64)
    norm = np.zeros(y.shape[-1], dtype=np.float64)
    for i in range(frames.shape[1]):
        y[:, i * HOP:i * HOP + FFT] += frames[:, i]
        norm[i * HOP:i * HOP + FFT] += WINDOW ** 2
    y /= np.maximum(norm, 1e-9)
    return y[:, FFT // 2:-FFT // 2]


raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(SOURCE), '-ar', str(RATE), '-ac', '2', '-f', 'f32le', '-'])
audio = np.frombuffer(raw, dtype='<f4').reshape(-1, 2).T.copy()
# Verify the transform preserves the source before any learned separation.
test = audio[:, :LENGTH]
identity_error = float(np.max(np.abs(istft(stft(test)) - test)))
assert identity_error < 1e-5, identity_error
options = ort.SessionOptions()
options.intra_op_num_threads = 4
options.inter_op_num_threads = 1
session = ort.InferenceSession(str(MODEL), sess_options=options, providers=['CPUExecutionProvider'])
stride = LENGTH // 2
pad = FFT
padded = np.pad(audio, ((0, 0), (pad, pad + LENGTH)), mode='reflect')
result = np.zeros_like(padded, dtype=np.float64)
weights = np.zeros(padded.shape[-1], dtype=np.float64)
blend = tukey(LENGTH, alpha=.25).astype(np.float32)
started = time.time()
chunks = 0
for start in range(0, audio.shape[-1] + pad, stride):
    block = padded[:, start:start + LENGTH]
    z = stft(block)
    tensor = np.stack((z.real, z.imag), axis=1).reshape(1, 4, FFT // 2 + 1, FRAMES)[:, :, :DIMF].astype(np.float32)
    tensor[:, :, :3] = 0
    separated = session.run(None, {'input': tensor})[0].reshape(2, 2, DIMF, FRAMES)
    spectrum = np.zeros((2, FFT // 2 + 1, FRAMES), dtype=np.complex64)
    spectrum[:, :DIMF] = separated[:, 0] + 1j * separated[:, 1]
    decoded = istft(spectrum) * 1.009
    result[:, start:start + LENGTH] += decoded * blend
    weights[start:start + LENGTH] += blend
    chunks += 1
    print(json.dumps({'chunk': chunks, 'elapsed': round(time.time() - started, 2)}), flush=True)
result /= np.maximum(weights, 1e-8)
vocals = result[:, pad:pad + audio.shape[-1]].astype(np.float32)
assert np.isfinite(vocals).all()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(RATE), '-ac', '2', '-i', '-', '-c:a', 'pcm_f32le', str(ASSETS / 'source-vocals.wav')], input=vocals.T.astype('<f4').tobytes(), check=True)
report = {'source': str(SOURCE), 'sourceSha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'model': 'Kim_Vocal_2.onnx', 'modelURL': 'https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/Kim_Vocal_2.onnx',
          'modelSha256': hashlib.sha256(MODEL.read_bytes()).hexdigest(), 'metadataUVRHash': '970b3f9492014d18fefeedfe4773cb42',
          'fft': FFT, 'hop': HOP, 'dimF': DIMF, 'frames': FRAMES, 'compensate': 1.009,
          'chunks': chunks, 'seconds': audio.shape[-1] / RATE, 'executionSeconds': time.time() - started,
          'stftIdentityMaxError': identity_error, 'pitchChanged': False, 'timeStretch': False,
          'synthesizedVoice': False, 'humanListening': False,
          'limits': 'A learned vocal estimate removes background content approximately. It does not establish perfect music removal or perceptual naturalness.',
          'sourceRMS': float(np.sqrt(np.mean(audio ** 2))), 'vocalRMS': float(np.sqrt(np.mean(vocals ** 2))),
          'removedRMS': float(np.sqrt(np.mean((audio - vocals) ** 2)))}
(REPORTS / 'voice-separation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report), flush=True)
