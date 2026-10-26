from pathlib import Path
import subprocess,json,numpy as np,re
from scipy import signal
root=Path('/workspace/Mdaar21-new');out=root/'creative/voice-ad-smooth/reports'
files={'v6_pcm_before_filters':root/'creative/voice-ad/assets/voice-edited.wav','v6_final_voice':root/'creative/voice-ad/assets/voice-clean.wav','v7_pcm_before_filters':root/'creative/voice-ad-smooth/assets/voice-edited.wav','v7_final_voice':root/'creative/voice-ad-smooth/assets/voice-clean.wav'}
results={}
for name,file in files.items():
 x=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(file),'-ac','1','-ar','48000','-f','f32le','-']),dtype='<f4')
 f,p=signal.welch(x,48000,nperseg=4096)
 def power(lo,hi):
  ix=(f>=lo)&(f<hi);return float(np.trapezoid(p[ix],f[ix]))
 results[name]={'peak':float(np.max(np.abs(x))),'samplesAtFullScale':int(np.sum(np.abs(x)>.9999)),'rmsDbFS':float(20*np.log10(np.sqrt(np.mean(x*x)))),'presenceToLowMidDB':float(10*np.log10(power(2000,4500)/power(150,1000)))}
for name,file in [('v6_mix',root/'creative/voice-ad/assets/final-mix.wav'),('v7_mix',root/'creative/voice-ad-smooth/assets/final-mix.wav')]:
 r=subprocess.run(['ffmpeg','-hide_banner','-i',str(file),'-af','loudnorm=I=-14:TP=-1.5:LRA=8:print_format=json','-f','null','-'],capture_output=True,check=True)
 s=r.stderr.decode();v=json.loads(s[s.rfind('{'):s.rfind('}')+1]);results[name]={'integratedLUFS':float(v['input_i']),'truePeakDBTP':float(v['input_tp']),'loudnessRangeLU':float(v['input_lra'])}
assert results['v7_pcm_before_filters']['samplesAtFullScale']==0
assert results['v7_final_voice']['presenceToLowMidDB']>results['v6_final_voice']['presenceToLowMidDB']
report={'measurements':results,'method':'FFmpeg float decode, PCM sample counts, Welch energy ratio and EBU loudnorm measurements. Baseline and candidate from the same original recording.','limits':'Objective signal checks; does not certify perceived quality, restore lost speech, or substitute for a human listening test.'}
(out/'audio-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
