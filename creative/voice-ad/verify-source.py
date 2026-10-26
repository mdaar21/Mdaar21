from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
groups=json.loads((ROOT/'captions.json').read_text())
beats=json.loads((ROOT/'beats.json').read_text())
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        page=browser.new_page(viewport={'width':1080,'height':1920})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.route('**/*.wav',lambda route:route.abort())
        page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
        page.wait_for_timeout(600)
        page.wait_for_function('Boolean(window.__timelines && window.__timelines["mdaar-voice"])',timeout=5000)
        page.evaluate('document.fonts.ready')
        def seek(t):page.evaluate('(t)=>{window.__timelines["mdaar-voice"].seek(t,false);return true}',t)
        caption_results=[]
        for i,g in enumerate(groups):
            t=(g['start']+g['end'])/2;seek(t)
            visible=page.evaluate('''()=>Array.from(document.querySelectorAll('.caption')).filter(e=>getComputedStyle(e).visibility==='visible'&&Number(getComputedStyle(e).opacity)>.1).map(e=>e.id)''')
            assert visible==[f'cap-{i}'],(i,visible)
            box=page.locator(f'#cap-{i} .caption-inner').bounding_box()
            assert box['x']>=65 and box['x']+box['width']<=940,box
            assert box['y']>=1310 and box['y']+box['height']<=1585,box
            assert box['height']<=215,box
            caption_results.append({'group':i,'time':t,'exactlyOneVisible':True,'safeArea':True,'height':round(box['height'],2)})
        scenes=[]
        for b in beats['beats']:
            seek((b['start']+b['end'])/2)
            active=page.evaluate('''()=>Array.from(document.querySelectorAll('section.scene')).filter(e=>{let r=e.getBoundingClientRect();return Number(getComputedStyle(e).opacity)>.99&&Math.abs(r.x)<1&&Math.abs(r.y)<1}).map(e=>e.id)''')
            assert active==[b['id']],(b,active)
            scenes.append({'id':b['id'],'correctVisibleScene':True})
        def state(t):
            seek(t)
            return page.evaluate('''()=>({visible:Array.from(document.querySelectorAll('.caption')).filter(e=>getComputedStyle(e).visibility==='visible'&&Number(getComputedStyle(e).opacity)>.1).map(e=>e.id),arm:document.querySelector('#s1 .fore-r').getAttribute('transform'),head:document.querySelector('#s7 .head').getAttribute('transform')})''')
        sample_times=[.8,3.2,16.2,23,31.8,36.1]
        reference={t:state(t) for t in sample_times}
        for t in reversed(sample_times):assert state(t)==reference[t],('seek-order',t)
        seek((beats['beats'][6]['start']+beats['beats'][6]['end'])/2)
        heads=page.locator('#s6 .head').all();a,b=[e.bounding_box() for e in heads]
        assert a['x']+a['width']<b['x'] or b['x']+b['width']<a['x'],('coach-head-overlap',a,b)
        seek(36.1)
        assert page.locator('#s14 .character').evaluate('e=>Number(getComputedStyle(e).opacity)')>.99
        faces=page.evaluate('''()=>Array.from(document.querySelectorAll('.head')).map(h=>({parts:h.children.length,face:h.querySelectorAll('.face').length,hair:h.querySelectorAll('.hair').length}))''')
        assert all(h=={'parts':2,'face':1,'hair':1} for h in faces)
        audio=page.locator('audio').all();assert len(audio)==1 and audio[0].get_attribute('src')=='assets/final-mix.wav'
        animation=page.evaluate('''()=>window.__timelines['mdaar-voice'].getChildren(false,true,false).map(x=>({start:x.startTime(),end:x.endTime(),duration:x.duration(),targets:x.targets().map(e=>e.id||e.getAttribute?.('class')||'object'),properties:Object.keys(x.vars).filter(k=>!['duration','ease','parent','overwrite','delay','immediateRender'].includes(k))}))''')
        (ROOT/'reports/animation-map.json').write_text(json.dumps({'duration':beats['duration'],'tweens':animation,'note':'Finite deterministic action, transitions between all scenes, no pre-transition scene-content exits. Caption groups have explicit hard kills.'},ensure_ascii=False,indent=2)+'\n')
        report={'ok':True,'scenes':scenes,'captionGroups':caption_results,'words':len(json.loads((ROOT/'words-final.json').read_text())),'blankCharacterFaces':len(faces),'sameResultAfterReverseSeeks':True,'coachFacesSeparated':True,'oneCombinedVoiceAndEffectsTrack':True,'musicAdded':False,'runtimeErrors':errors}
        assert not errors,errors
        (ROOT/'reports/source-browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'ok':True,'scenes':len(scenes),'captionGroups':len(groups),'words':report['words'],'blankCharacterFaces':len(faces),'reverseSeeking':'PASS'}))
        browser.close()
finally:server.shutdown()
