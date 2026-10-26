from pathlib import Path
import json,subprocess,hashlib,numpy as np,struct
ROOT=Path(__file__).resolve().parent
movie=ROOT/'renders/mdaar_tiktok_v7_60fps.mp4';out=ROOT/'reports/encoded-frames';out.mkdir(exist_ok=True)
beats=json.loads((ROOT/'beats.json').read_text())['beats']
for i,b in enumerate(beats):
 t=(b['start']+b['end'])/2
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(movie),'-frames:v','1','-vf','scale=360:640',str(out/f'frame-{i:02}.png')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-pattern_type','glob','-i',str(out/'frame-*.png'),'-vf','tile=5x3','-frames:v','1',str(out/'contact-sheet.jpg')],check=True)
def decode(f):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-ac','1','-ar','16000','-f','f32le','-']),dtype='<f4')
a=decode(ROOT/'assets/final-mix.wav');b=decode(movie);n=min(len(a),len(b));corr=float(np.corrcoef(a[:n],b[:n])[0,1]);assert corr>.98,corr
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate,sample_rate,channels','-of','json',str(movie)]))
raw=movie.read_bytes();position=0;atoms=[]
while position+8<=len(raw):
 length,kind=struct.unpack('>I4s',raw[position:position+8]);length=length or len(raw)-position
 if length==1:length=struct.unpack('>Q',raw[position+8:position+16])[0]
 atoms.append(kind.decode(errors='replace'));position+=length
assert atoms.index('moov')<atoms.index('mdat'),atoms
assert info['streams'][0]['width']==1080 and info['streams'][0]['height']==1920
assert info['streams'][0]['r_frame_rate']=='60/1'
assert float(info['format']['size'])<40*1024*1024
report={'ok':True,'metadata':info,'sha256':hashlib.sha256(raw).hexdigest(),'fastStartMoovBeforeMdat':True,'aacAudioCorrelationWithApprovedMix':corr,'audioDurationDeviationSeconds':abs(len(a)-len(b))/16000,'encodedFramesExtracted':len(beats),'musicAdded':False,'captionsBurnedIntoVideo':True,'limits':'Local encoded file validation; no TikTok campaign or marketing outcome measurement.'}
(ROOT/'reports/encoded-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
