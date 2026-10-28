from pathlib import Path
import json,hashlib,subprocess,struct
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
VIDEO=ROOT/'renders/mdaar_tiktok_v12_premium.mp4'
def run(args):return subprocess.run(args,capture_output=True,check=True)
meta=json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(VIDEO)]).stdout)
v=next(x for x in meta['streams'] if x['codec_type']=='video');a=next(x for x in meta['streams'] if x['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'],v['avg_frame_rate'])==(1080,1920,'60/1','60/1')
assert v['codec_name']=='h264' and a['codec_name']=='aac' and int(a['sample_rate'])==48000
assert abs(float(meta['format']['duration'])-29.8)<.03
assert int(v['nb_frames'])==1788
frames=json.loads(run(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(VIDEO)]).stdout)['frames']
pts=np.array([float(f['best_effort_timestamp_time']) for f in frames]);gaps=np.diff(pts)
assert np.max(np.abs(gaps-1/60))<2e-6
movement=np.frombuffer(run(['ffmpeg','-v','error','-ss','0.35','-i',str(VIDEO),'-t','0.6','-vf','crop=840:900:80:400,scale=210:225,format=gray','-f','rawvideo','-']).stdout,dtype=np.uint8).reshape(-1,225,210)
diff=np.mean(np.abs(np.diff(movement.astype(np.float32),axis=0)),axis=(1,2))
assert float(np.mean(diff==0))<.15,('duplicated moving frames',diff.tolist())
def decode(path):return np.frombuffer(run(['ffmpeg','-v','error','-i',str(path),'-ar','48000','-ac','2','-f','f32le','-']).stdout,dtype='<f4')
master=decode(ROOT/'assets/final-mix.wav');encoded=decode(VIDEO);n=min(len(master),len(encoded))
corr=float(np.corrcoef(master[:n],encoded[:n])[0,1]);assert corr>.995,corr
meter=run(['ffmpeg','-hide_banner','-nostats','-i',str(VIDEO),'-af','loudnorm=I=-18.5:TP=-2.5:LRA=8:print_format=json','-f','null','-']).stderr.decode();loud=json.loads(meter[meter.rfind('{'):meter.rfind('}')+1]);assert float(loud['input_tp'])<-1.5
assert -20<float(loud['input_i'])<-18
decoded=run(['ffmpeg','-v','warning','-i',str(VIDEO),'-f','null','-'])
assert not decoded.stderr,decoded.stderr.decode()
atoms=[];data=VIDEO.read_bytes();offset=0
while offset+8<=len(data):
 size,kind=struct.unpack('>I4s',data[offset:offset+8])
 if size==1:size=struct.unpack('>Q',data[offset+8:offset+16])[0]
 if size==0:size=len(data)-offset
 atoms.append((kind.decode('ascii','replace'),offset,size));offset+=size
names=[x[0] for x in atoms];assert names.index('moov')<names.index('mdat')
out=ROOT/'reports/encoded-frames';out.mkdir(parents=True,exist_ok=True)
beats=json.loads((ROOT/'beats.json').read_text())['beats']
times=[0]+[round((x['start']+x['end'])/2,3) for x in beats]+[29.7]
images=[]
for i,t in enumerate(times):
 p=out/f'hero-{i}.jpg';run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(VIDEO),'-frames:v','1','-q:v','2',str(p)]);images.append((t,p))
sheet=Image.new('RGB',(1440,2034),'#24241f');draw=ImageDraw.Draw(sheet)
for i,(t,p) in enumerate(images):
 x=i%4*360;y=i//4*678;sheet.paste(Image.open(p).resize((360,640)),(x,y+38));draw.text((x+10,y+10),f'{t:.3f}s encoded',fill='white')
sheet.save(ROOT/'reports/encoded-contact.jpg',quality=91)
handoffs=[]
for i,b in enumerate(beats[1:]):
 for j,dt in enumerate([-.18,0,.18,.36,.58]):
  t=b['start']+dt;p=out/f'cut-{i}-{j}.jpg';run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(VIDEO),'-frames:v','1','-q:v','2',str(p)]);handoffs.append({'scene':b['id'],'t':t,'file':p.name})
sheet=Image.new('RGB',(1350,7*510),'#24241f');draw=ImageDraw.Draw(sheet)
for i,h in enumerate(handoffs):
 x=i%5*270;y=i//5*510;sheet.paste(Image.open(out/h['file']).resize((270,480)),(x,y+30));draw.text((x+8,y+8),f'{h["scene"]} {h["t"]:.3f}s',fill='white')
sheet.save(ROOT/'reports/encoded-handoffs.jpg',quality=91)
report={'ok':True,'file':str(VIDEO),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'seconds':float(meta['format']['duration']),'width':1080,'height':1920,'fps':'60/1','frames':1788,'maxFrameCadenceErrorSeconds':float(np.max(np.abs(gaps-1/60))),'sampledMovingFrames':len(movement),'adjacentMovingFrameIdenticalFraction':float(np.mean(diff==0)),'movingFrameDifferenceMin':float(diff.min()),'fastStartMoovBeforeMdat':True,'audioCorrelationWithMaster':corr,'encodedLoudness':loud,'decodeExit':0,'decodeWarnings':0,'encodedHeroFrames':len(images),'encodedHandoffFrames':len(handoffs),'limits':'Local file evidence, not human listening or audience marketing performance. Image timings are seek requests within one source frame.'}
(ROOT/'reports/encoded-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
