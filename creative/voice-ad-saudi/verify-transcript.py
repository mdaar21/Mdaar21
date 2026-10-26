"""Independent cached ASR check of the newly assembled Saudi narration."""
from pathlib import Path
import hashlib
import json
import subprocess
import time
import numpy as np
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parent
source = ROOT / 'assets/voice-clean.wav'
started = time.time()
model = WhisperModel('medium',device='cpu',compute_type='int8',cpu_threads=4,
    num_workers=1,download_root='/tmp/mdaar-asr-models',local_files_only=True)
audio = np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(source),
    '-ar','16000','-ac','1','-f','f32le','-']),dtype='<f4')
segments, info = model.transcribe(audio,language='ar',beam_size=5,word_timestamps=True,
    vad_filter=False,condition_on_previous_text=False,
    initial_prompt='مدار. بروتوكول التحول. تمارين. وصفات. سعرات.')
rows = []
for s in segments:
    row = {'start':s.start,'end':s.end,'text':s.text,
           'words':[{'text':w.word,'start':w.start,'end':w.end,'probability':w.probability} for w in (s.words or [])]}
    rows.append(row)
    print(s.text,flush=True)
report = {'engine':'faster-whisper medium multilingual int8','language':info.language,
    'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'durationSeconds':len(audio)/16000,'segments':rows,'runtimeSeconds':time.time()-started,
    'limits':'Automated transcription sanity check, not a human listening test or guarantee of naturalness. Captions use provider native word boundaries, not this approximate ASR.'}
(ROOT/'reports/asr-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Completed',round(time.time()-started,1),flush=True)
