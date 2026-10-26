"""Record actual playback of all 13 handoffs, with browser timing evidence."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from threading import Thread
import json
import shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
plans=json.loads((ROOT/'transitions.json').read_text())
beats={b['id']:b for b in json.loads((ROOT/'beats.json').read_text())['beats']}
temp=ROOT/'reports/sequences/playback'
temp.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
Thread(target=server.serve_forever,daemon=True).start()
windows=[]
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        context=browser.new_context(viewport={'width':1080,'height':1920},device_scale_factor=1/3,
            record_video_dir=str(temp),record_video_size={'width':360,'height':640})
        page=context.new_page()
        page.route('**/*.wav',lambda route:route.abort())
        page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
        page.wait_for_function('Boolean(window.__timelines?.["mdaar-voice"])')
        page.evaluate('document.fonts.ready')
        page.evaluate('''()=>{window.qaFrames=[];window.qaRecording=false;function frame(t){if(window.qaRecording)window.qaFrames.push({wall:t,timeline:window.__timelines['mdaar-voice'].time()});requestAnimationFrame(frame)}requestAnimationFrame(frame)}''')
        for plan in plans:
            start=beats[plan['to']]['start']-.36
            length=plan['duration']+.24
            page.evaluate('(t)=>{window.__timelines["mdaar-voice"].seek(t,false).play();window.qaRecording=true;return true}',start)
            page.wait_for_timeout(round(length*1000))
            page.evaluate('()=>{window.__timelines["mdaar-voice"].pause();window.qaRecording=false;return true}')
            windows.append({'to':plan['to'],'family':plan['family'],'from':start,'playSeconds':length})
        frames=page.evaluate('window.qaFrames')
        video=page.video
        page.close();context.close()
        path=Path(video.path())
        shutil.copy2(path,ROOT/'reports/motion-playback.webm')
        browser.close()
finally:server.shutdown()
intervals=[b['wall']-a['wall'] for a,b in zip(frames,frames[1:]) if 0<b['wall']-a['wall']<100]
intervals.sort()
report={'ok':True,'windows':windows,'actualBrowserAnimationFrames':len(frames),
    'medianRAFIntervalMS':intervals[len(intervals)//2],
    'p95RAFIntervalMS':intervals[int(len(intervals)*.95)],
    'recording':'reports/motion-playback.webm',
    'note':'Silent QA recording of actual browser playback, one window per handoff. Jumps between windows are intentional QA seeks, not transitions in the final film. RAF evidence is local performance, not a guarantee on all devices.'}
(ROOT/'reports/motion-playback.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'ok':True,'transitionsPlayed':len(windows),'frames':len(frames)}))
