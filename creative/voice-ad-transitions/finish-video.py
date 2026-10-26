"""Retain the exact accepted V10 AAC stream after rendering new visuals."""
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np

ROOT=Path(__file__).resolve().parent
original=ROOT.parents[1]/'public/ad/voice-original/mdaar_tiktok_v10_original_clear.mp4'
render=ROOT/'renders/mdaar_transitions_render.mp4'
output=ROOT/'renders/mdaar_tiktok_v11_transitions.mp4'
def run(args):return subprocess.run(args,capture_output=True,check=True)
def packet_hash(path):
    return run(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-']).stdout.decode().strip()
def decoded(path):
    return np.frombuffer(run(['ffmpeg','-v','error','-i',str(path),'-ar','48000','-ac','2','-f','f32le','-']).stdout,dtype='<f4')
run(['ffmpeg','-v','error','-y','-i',str(render),'-i',str(original),'-map','0:v:0','-map','1:a:0',
     '-c','copy','-movflags','+faststart',str(output)])
hashes=[packet_hash(p) for p in [original,output]]
assert hashes[0]==hashes[1]
before,after=decoded(original),decoded(output)
assert np.array_equal(before,after),'Audio samples or priming changed during remux.'
voice=ROOT/'assets/final-mix.wav'
accepted=ROOT.parent/'voice-ad-original-clear/assets/final-mix.wav'
assert voice.read_bytes()==accepted.read_bytes()
report={'ok':True,'acceptedAudioFrom':'../../public/ad/voice-original/mdaar_tiktok_v10_original_clear.mp4',
        'aacPacketHashes':hashes,'decodedStereo48kSamplesIdentical':True,'decodedSamples':len(before)//2,
        'audioReencoded':False,'audioProcessingChanged':False,'musicAdded':False,
        'acceptedMasterWavSha256':hashlib.sha256(voice.read_bytes()).hexdigest()}
(ROOT/'reports/audio-unchanged.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'ok':True,'audioIdenticalToV10':True,'file':str(output)}))
