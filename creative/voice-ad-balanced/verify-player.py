from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import json,re
ROOT=Path(__file__).resolve().parent
PUBLIC=ROOT.parents[1]/'public'
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  file=Path(self.translate_path(self.path))
  if file.suffix not in ['.mp4','.mp3'] or not file.is_file():return super().do_GET()
  size=file.stat().st_size;start=0;end=size-1;status=200
  match=re.fullmatch(r'bytes=(\d+)-(\d*)',self.headers.get('Range',''))
  if match:start=int(match[1]);end=min(int(match[2]) if match[2] else size-1,size-1);status=206
  if start>=size:
   self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.end_headers();return
  self.send_response(status);self.send_header('Content-Type','video/mp4' if file.suffix=='.mp4' else 'audio/mpeg');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
  if status==206:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers()
  try:
   with file.open('rb') as f:
    f.seek(start);remaining=end-start+1
    while remaining:
     chunk=f.read(min(65536,remaining))
     if not chunk:break
     self.wfile.write(chunk);remaining-=len(chunk)
  except (BrokenPipeError,ConnectionResetError):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(PUBLIC)))
Thread(target=server.serve_forever,daemon=True).start();report=[]
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for width in [320,390,1440]:
   p=b.new_page(viewport={'width':width,'height':920});errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   response=p.goto(f'http://127.0.0.1:{server.server_port}/ad/voice-balanced/',wait_until='networkidle')
   p.wait_for_function('()=>document.querySelector("video").readyState>=1')
   assert abs(p.locator('video').evaluate('v=>v.duration')-39.10377)<.07
   p.locator('video').evaluate('v=>{v.muted=true;return v.play()}');p.wait_for_function('()=>document.querySelector("video").currentTime>.15');p.locator('video').evaluate('v=>v.pause()')
   for t in [.5,14.2,27,37.5]:
    p.locator('video').evaluate('(v,t)=>{v.currentTime=t}',t);p.wait_for_function('()=>!document.querySelector("video").seeking&&document.querySelector("video").readyState>=2')
   assert not p.evaluate('document.documentElement.scrollWidth>innerWidth')
   links=p.locator('a[download]');assert links.count()==3
   for a in links.all():
    file=a.get_attribute('href');r=p.request.get(f'http://127.0.0.1:{server.server_port}/ad/voice-balanced/'+file,headers={'Range':'bytes=0-1023'})
    assert r.status==(200 if file.endswith('.srt') else 206)
   assert not errors,errors
   if width==390:p.screenshot(path=str(ROOT/'reports/player-mobile.png'))
   report.append({'width':width,'status':response.status,'nativeVideoDecoded':True,'playPause':True,'seekFourScenes':True,'noHorizontalOverflow':True,'threeDownloadsVerified':True,'runtimeErrors':errors});p.close()
  b.close()
finally:server.shutdown()
(ROOT/'reports/player-browser.json').write_text(json.dumps({'ok':True,'viewports':report},indent=2)+'\n');print(json.dumps({'ok':True,'viewports':len(report)}))
