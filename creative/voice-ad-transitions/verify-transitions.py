"""Review ordered transition frames, boundaries and reversible GSAP state."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import json
import subprocess
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
plans=json.loads((ROOT/'transitions.json').read_text())
beats=json.loads((ROOT/'beats.json').read_text())['beats']
phases=[0,.16,.32,.5,.68,.84,1]
out=ROOT/'reports/sequences'
for name in ['a','b']:(out/name).mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        page=browser.new_page(viewport={'width':1080,'height':1920},device_scale_factor=1/3)
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.route('**/*.wav',lambda route:route.abort())
        page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
        page.wait_for_function('Boolean(window.__timelines?.["mdaar-voice"])')
        page.evaluate('document.fonts.ready')
        page.evaluate('''()=>{let e=document.createElement('div');e.id='qa-label';Object.assign(e.style,{position:'absolute',top:'245px',left:'20px',zIndex:'999',font:'28px sans-serif',direction:'ltr',padding:'8px',background:'#121210',color:'#f9f5e9'});document.body.appendChild(e)}''')
        def seek(t):page.evaluate('(t)=>{window.__timelines["mdaar-voice"].seek(t,false);return true}',t)
        def state():
            return page.evaluate('''()=>({scenes:Array.from(document.querySelectorAll('section.scene')).map(e=>{let c=e.querySelector('.scene-camera'),s=getComputedStyle(e),m=getComputedStyle(c);return [e.id,s.opacity,s.clipPath,Number(s.opacity)>.001?m.transform:'hidden',Number(s.opacity)>.001?m.filter:'hidden']}),shutter:Array.from(document.querySelectorAll('.transition-shutter,.shutter-top,.shutter-bottom')).map(e=>{let s=getComputedStyle(e);return [s.opacity,s.transform]})})''')
        checks=[];references=[]
        for i,plan in enumerate(plans):
            b=next(b for b in beats if b['id']==plan['to']);prev=beats[beats.index(b)-1]
            T=b['start']-.28;d=plan['duration'];seek(T-.025)
            assert page.locator('#'+prev['id']).evaluate('e=>Number(getComputedStyle(e).opacity)')>.99
            assert page.locator('#'+prev['id']+' h2').evaluate('e=>Number(getComputedStyle(e).opacity)')>.99
            for j,f in enumerate(phases):
                t=T+d*f;seek(t)
                page.evaluate('(label)=>document.querySelector("#qa-label").textContent=label',f'{prev["id"]} > {b["id"]} / {plan["family"]} / {round(f*100)}%')
                path=out/('a' if i<6 else 'b')/f'frame-{i:02}-{j:02}.png'
                page.screenshot(path=str(path),clip={'x':0,'y':230,'width':1080,'height':1120})
                if j==3:references.append((t,state()))
            seek(T+d+.04)
            assert page.locator('#'+prev['id']).evaluate('e=>Number(getComputedStyle(e).opacity)')<.01
            assert page.locator('#'+b['id']).evaluate('e=>Number(getComputedStyle(e).opacity)')>.99
            assert page.locator('#'+b['id']).evaluate('e=>getComputedStyle(e).clipPath')=='none'
            c=page.locator('#'+b['id']+' .scene-camera').evaluate('e=>({transform:getComputedStyle(e).transform,filter:getComputedStyle(e).filter})')
            checks.append({'from':prev['id'],'to':b['id'],'family':plan['family'],'start':T,'duration':d,'oldFullyVisibleAtStart':True,'settlesToNewScene':True,'orderedFrames':len(phases),'settledCamera':c})
        for t,expected in reversed(references):
            seek(t);actual=state();assert actual==expected,('non-deterministic reverse seek',t,actual,expected)
        assert len(set(p['family'] for p in plans))==5
        assert not errors,errors
        browser.close()
finally:server.shutdown()
for name in ['a','b']:
    rows=6 if name=='a' else 7
    subprocess.run(['ffmpeg','-v','error','-y','-pattern_type','glob','-i',str(out/name/'frame-*.png'),
        '-vf',f'tile=7x{rows}','-frames:v','1',str(ROOT/'reports'/f'transitions-{name}.jpg')],check=True)
report={'ok':True,'distinctFamilies':5,'transitions':checks,'reverseMidpointSeeksIdentical':True,'runtimeErrors':errors,
        'scope':'Ordered moving-phase screenshots and browser state checks; not an audience study.'}
(ROOT/'reports/transitions-browser.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'ok':True,'transitions':len(checks),'families':5,'frames':len(plans)*len(phases)}))
