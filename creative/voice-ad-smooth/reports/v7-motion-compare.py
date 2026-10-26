from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import json
root=Path('/workspace/Mdaar21-new/creative')
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root)));Thread(target=server.serve_forever,daemon=True).start();results={}
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for folder in ['voice-ad','voice-ad-smooth']:
   p=b.new_page(viewport={'width':1080,'height':1920});p.route('**/*.wav',lambda r:r.abort());p.goto(f'http://127.0.0.1:{server.server_port}/{folder}/',wait_until='domcontentloaded');p.wait_for_function('()=>Boolean(window.__timelines?.["mdaar-voice"])');values=[]
   beats=json.loads((root/folder/'beats.json').read_text())['beats']
   for beat in beats[1:]:
    p.evaluate('(t)=>{window.__timelines["mdaar-voice"].seek(t,false)}',beat['start']+.05)
    alpha=p.locator('#'+beat['id']+' h2').evaluate('e=>Number(getComputedStyle(e).opacity)')
    values.append({'scene':beat['id'],'time':beat['start']+.05,'headingOpacity':alpha,'flashedBeforeEntrance':alpha>.05})
   results[folder]={'scenesChecked':len(values),'prematurelyVisibleHeadings':sum(v['flashedBeforeEntrance'] for v in values),'details':values};p.close()
  b.close()
finally:server.shutdown()
assert results['voice-ad']['prematurelyVisibleHeadings']>0
assert results['voice-ad-smooth']['prematurelyVisibleHeadings']==0
report={'measurements':results,'scope':'Same early reveal timestamp (+50 ms from each scene start), actual GSAP browser state; not a viewer perception or campaign test.'}
(root/'voice-ad-smooth/reports/motion-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:{a:v for a,v in x.items() if a!='details'} for k,x in results.items()})
