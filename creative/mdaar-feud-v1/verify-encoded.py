from pathlib import Path
import subprocess,json,hashlib,struct
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
def run(a):return subprocess.run(a,capture_output=True,check=True)
result=[]
for name,width,height in [('4k',2160,3840),('1080',1080,1920)]:
 p=R/'renders'/f'mdaar_feud_30s_{name}.mp4'
 m=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]).stdout)
 v=next(x for x in m['streams'] if x['codec_type']=='video');a=next(x for x in m['streams'] if x['codec_type']=='audio')
 assert (v['width'],v['height'],v['r_frame_rate'],v['codec_name'])==(width,height,'30/1','h264')
 assert abs(float(m['format']['duration'])-30)<.03 and int(v['nb_frames'])==900
 assert a['codec_name']=='aac' and int(a['sample_rate'])==48000
 warn=run(['ffmpeg','-v','warning','-i',str(p),'-f','null','-']).stderr;assert not warn,warn.decode()
 raw=p.read_bytes();kinds=[];pos=0
 while pos+8<len(raw):
  size,kind=struct.unpack('>I4s',raw[pos:pos+8])
  if size==1:size=struct.unpack('>Q',raw[pos+8:pos+16])[0]
  if not size:size=len(raw)-pos
  kinds.append(kind);pos+=size
 assert kinds.index(b'moov')<kinds.index(b'mdat')
 result.append({'file':p.name,'width':width,'height':height,'fps':30,'frames':900,'seconds':float(m['format']['duration']),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'faststart':True,'decodeWarnings':0})
p=R/'renders/mdaar_feud_30s_1080.mp4'
s=run(['ffmpeg','-hide_banner','-nostats','-i',str(p),'-af','loudnorm=I=-19:TP=-3:LRA=8:print_format=json','-f','null','-']).stderr.decode();loud=json.loads(s[s.rfind('{'):s.rfind('}')+1]);assert float(loud['input_tp'])<-2 and -20<float(loud['input_i'])<-18
def pcm(p):return np.frombuffer(run(['ffmpeg','-v','error','-i',str(p),'-ac','2','-ar','48000','-f','f32le','-']).stdout,dtype='<f4')
a=pcm(p);b=pcm(R/'assets/final-mix.wav');n=min(len(a),len(b));corr=float(np.corrcoef(a[:n],b[:n])[0,1]);assert corr>.995,corr
times=[0,.9,3.7,5.3,8.7,10.4,13.8,15.5,16.3,16.85,17.9,20.5,22.9,24.6,26.3,28.5,29.9]
out=R/'reports/frames';out.mkdir(exist_ok=True);sheet=Image.new('RGB',(1440,3400),'#071226');d=ImageDraw.Draw(sheet)
for i,t in enumerate(times):
 q=out/f'encoded-{i}.jpg';run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(p),'-frames:v','1','-q:v','2',str(q)])
 x=i%4*360;y=i//4*680;sheet.paste(Image.open(q).resize((360,640)),(x,y+35));d.text((x+8,y+10),f'{t:.2f}s encoded',fill='white')
sheet.save(R/'reports/encoded-contact.jpg',quality=91)
report={'ok':True,'outputs':result,'encodedLoudness':loud,'masterAudioCorrelation':corr,'encodedHeroFrames':len(times),'humanListeningVerified':False,'native4kPhotographicFootage':False,'limitations':'Studio photographs animated with camera framing; no full-motion human performance generator available.'}
(R/'reports/encoded-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
