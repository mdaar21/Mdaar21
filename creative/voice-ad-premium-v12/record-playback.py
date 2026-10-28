from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from threading import Thread
import json,shutil
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
out=ROOT/'reports/sequences/playback';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  context=browser.new_context(viewport={'width':1080,'height':1920},device_scale_factor=1/3,record_video_dir=str(out),record_video_size={'width':360,'height':640})
  page=context.new_page();page.route('**/*.wav',lambda r:r.abort())
  page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded');page.wait_for_function('Boolean(window.__timelines?.["mdaar-premium"])');page.evaluate('document.fonts.ready')
  page.evaluate('''()=>{window.raf=[];window.recording=true;function frame(t){if(window.recording)window.raf.push({wall:t,time:window.__timelines['mdaar-premium'].time()});requestAnimationFrame(frame)}requestAnimationFrame(frame);window.__timelines['mdaar-premium'].seek(0,false).play()}''')
  page.wait_for_timeout(30100)
  frames=page.evaluate('()=>{window.recording=false;window.__timelines["mdaar-premium"].pause();return window.raf}')
  video=page.video;page.close();context.close();shutil.copy2(Path(video.path()),ROOT/'reports/motion-playback.webm');browser.close()
finally:server.shutdown()
intervals=sorted(b['wall']-a['wall'] for a,b in zip(frames,frames[1:]) if 0<b['wall']-a['wall']<200)
report={'ok':True,'continuousTimelineSeconds':29.8,'actualBrowserFrames':len(frames),'timelineFirst':frames[0]['time'],'timelineLast':frames[-1]['time'],'medianRAFMS':intervals[len(intervals)//2],'p95RAFMS':intervals[int(len(intervals)*.95)],'recording':'reports/motion-playback.webm','audioInQARecording':False,'note':'Actual local continuous browser animation. Software preview cadence is measured separately from offline 60fps frame sampling. Not human perceptual playback or listening.'}
assert report['timelineLast']>=29.79
(ROOT/'reports/motion-playback.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
