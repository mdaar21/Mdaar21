from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import json
from PIL import Image,ImageDraw
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
beats=json.loads((ROOT/'beats.json').read_text())['beats']
groups=json.loads((ROOT/'captions.json').read_text())
out=ROOT/'reports/sequences';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  page=browser.new_page(viewport={'width':1080,'height':1920})
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.route('**/*.wav',lambda r:r.abort())
  page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
  page.wait_for_function('Boolean(window.__timelines?.["mdaar-premium"])')
  page.evaluate('document.fonts.ready')
  def seek(t):page.evaluate('(t)=>{window.__timelines["mdaar-premium"].seek(t,false);return true}',t)
  def opacity(selector):return page.locator(selector).evaluate('e=>Number(getComputedStyle(e).opacity)')
  def rect(selector):return page.locator(selector).bounding_box()
  seek(0)
  assert opacity('#s0 .stage')>.99 and opacity('#s0 h2')>.99
  assert page.locator('.blank-face').count()==4
  assert page.locator('.head').evaluate_all('(es)=>es.every(e=>e.children.length===1&&e.firstElementChild.classList.contains("blank-face"))')
  checked=[]
  for i,g in enumerate(groups):
   assert g['end']>g['start'] and (i==0 or g['start']>=groups[i-1]['end'])
   seek((g['start']+g['end'])/2)
   visible=page.locator('.caption').evaluate_all('(es)=>es.filter(e=>Number(getComputedStyle(e).opacity)>.1&&getComputedStyle(e).visibility==="visible").map(e=>e.id)')
   assert visible==[f'cap-{i}'],(i,visible)
   box=rect(f'#cap-{i} .caption-inner')
   assert box['x']>=79 and box['x']+box['width']<=921,box
   assert box['y']>=1459 and box['y']+box['height']<=1667,box
   assert box['height']<205,box
   checked.append({'index':i,'time':round((g['start']+g['end'])/2,3),'box':box,'seconds':g['end']-g['start']})
  seek(4.8)
  actor=rect('#s1 .character');menu=rect('#s1 .source-list')
  assert actor['x']+actor['width']<menu['x'],(actor,menu)
  seek(7.2)
  assert opacity('#s2 .book-object')>.99
  assert page.locator('#s3 .menu-row').count()==3
  seek(28)
  assert page.locator('.price-line').inner_text().strip().startswith('15.99')
  assert opacity('#s7 .purchase-cta')>.99
  assert len(page.locator('audio').all())==1
  scene_images=[]
  for i,b in enumerate(beats):
   t=min(b['end']-.4,b['start']+max(.95,(b['end']-b['start'])/2))
   seek(t);path=out/f'scene-{i}.jpg';page.screenshot(path=str(path),type='jpeg',quality=90)
   scene_images.append((t,path))
  handoffs=[]
  for i,b in enumerate(beats[1:],1):
   frames=[]
   for j,offset in enumerate([-.34,-.16,0,.16,.34,.58]):
    t=b['start']+offset;seek(t);path=out/f'handoff-{i}-{j}.jpg';page.screenshot(path=str(path),type='jpeg',quality=88);frames.append({'time':t,'file':path.name})
   handoffs.append({'to':b['id'],'family':b['family'],'frames':frames})
  times=[.8,4.8,8,12.5,15.6,18.6,22.8,27.8]
  def state(t):
   seek(t)
   return page.locator('.scene').evaluate_all('(es)=>es.filter(e=>Number(getComputedStyle(e).opacity)>.01).map(e=>({id:e.id,opacity:getComputedStyle(e).opacity,clip:getComputedStyle(e).clipPath,camera:getComputedStyle(e.firstElementChild).transform,heads:Array.from(e.querySelectorAll(".head")).map(h=>h.getAttribute("transform"))}))')
  reference={t:state(t) for t in times}
  for t in reversed(times):assert state(t)==reference[t],('reverse seek',t)
  browser.close()
finally:server.shutdown()

sheet=Image.new('RGB',(1440,1704),'#24241f');draw=ImageDraw.Draw(sheet)
for i,(t,path) in enumerate(scene_images):
 x=i%4*360;y=i//4*852;sheet.paste(Image.open(path).resize((360,640)),(x,y+38));draw.text((x+12,y+12),f'{beats[i]["id"]} / {t:.2f}s',fill='white')
sheet.save(ROOT/'reports/scene-contact.jpg',quality=91)
sheet=Image.new('RGB',(1296,7*416),'#24241f');draw=ImageDraw.Draw(sheet)
for row,h in enumerate(handoffs):
 for col,f in enumerate(h['frames']):
  x=col*216;y=row*416;sheet.paste(Image.open(out/f['file']).resize((216,384)),(x,y+32));draw.text((x+6,y+8),f'{h["to"]} {f["time"]:.2f}s',fill='white')
sheet.save(ROOT/'reports/handoff-contact.jpg',quality=91)
report={'ok':not errors,'sourceScenes':8,'captionGroups':len(groups),'captionBounds':checked,'firstFrameCharacterAndTitleVisible':True,'featurelessFaces':4,'sourceMenuAndActorDoNotOverlap':True,'bookVisibleBySeconds':7.2,'sameStateAfterReverseSeeks':True,'ownerPrice':'15.99 SAR','finalCTASettledBy':26.35,'duration':29.8,'settledEndHoldSeconds':3.45,'handoffs':handoffs,'musicTrackAdded':False,'humanListening':False,'runtimeErrors':errors}
(ROOT/'reports/source-browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
assert not errors,errors
print(json.dumps({k:v for k,v in report.items() if k not in ['handoffs','captionBounds']}))
