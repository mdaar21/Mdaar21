from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from functools import partial
import json,re
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parent;PUBLIC=R.parents[1]/'public'
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_GET(self):
  f=Path(self.translate_path(self.path))
  if f.suffix!='.mp4' or not f.is_file():return super().do_GET()
  size=f.stat().st_size;start=0;end=size-1;status=200
  m=re.fullmatch(r'bytes=(\d+)-(\d*)',self.headers.get('Range',''))
  if m:start=int(m[1]);end=min(int(m[2]) if m[2] else end,end);status=206
  if start>=size:self.send_response(416);self.end_headers();return
  self.send_response(status);self.send_header('Content-Type','video/mp4');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
  if status==206:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers()
  try:
   with f.open('rb') as stream:
    stream.seek(start);left=end-start+1
    while left:
     chunk=stream.read(min(left,65536))
     if not chunk:break
     self.wfile.write(chunk);left-=len(chunk)
  except (BrokenPipeError,ConnectionResetError):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(PUBLIC)));Thread(target=s.serve_forever,daemon=True).start()
checks=[]
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for width in [320,390,1440]:
   page=b.new_page(viewport={'width':width,'height':900});errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
   page.goto(f'http://127.0.0.1:{s.server_port}/ad/feud/',wait_until='domcontentloaded')
   page.wait_for_function('()=>document.querySelector("video").readyState>=1')
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   assert page.locator('a[download]').count()==3
   duration=page.locator('video').evaluate('(v)=>v.duration');assert abs(duration-30)<.03
   page.locator('video').evaluate('(v)=>{v.muted=true;return v.play()}');page.wait_for_function('()=>document.querySelector("video").currentTime>.15');page.locator('video').evaluate('(v)=>v.pause()')
   seeked=[]
   for t in [.9,15.5,24.6,29.5]:
    page.locator('video').evaluate('(v,t)=>{v.currentTime=t;return true}',t)
    page.wait_for_function('(t)=>Math.abs(document.querySelector("video").currentTime-t)<.2&&!document.querySelector("video").seeking',arg=t)
    seeked.append(t)
   page.locator('video').evaluate('(v)=>{v.currentTime=0;return v.play()}');page.wait_for_timeout(250)
   assert not page.locator('video').evaluate('(v)=>v.paused')
   page.locator('video').evaluate('(v)=>v.pause()')
   if width==390:page.screenshot(path=str(R/'reports/player-mobile.png'),full_page=True)
   assert not errs,errs
   checks.append({'width':width,'overflow':False,'metadataDuration':duration,'nativePlayPause':True,'seekedSeconds':seeked,'downloadLinks':3,'pageErrors':errs});page.close()
  b.close()
finally:s.shutdown()
(R/'reports/player.json').write_text(json.dumps({'ok':True,'checks':checks},indent=2)+'\n');print(json.dumps(checks))
