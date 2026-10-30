"""Saudi catalog TTS; retain provider timings, no cloned voice or human claim."""
from pathlib import Path
import asyncio,json,hashlib,os
import certifi
certifi.where=lambda:'/etc/ssl/certs/ca-certificates.crt'
import edge_tts
R=Path(__file__).resolve().parent
async def main():
 sem=asyncio.Semaphore(3)
 async def line(v):
  async with sem:
   p=R/'assets/voice'/v['id'];req={**v,'voice':'ar-SA-HamedNeural'}
   digest=hashlib.sha256(json.dumps(req,sort_keys=True).encode()).hexdigest()
   cache=p.with_suffix('.request.json')
   if cache.exists() and json.loads(cache.read_text()).get('sha256')==digest:
    print('Cached',v['id'],flush=True);return
   speech=edge_tts.Communicate(v['text'],voice=req['voice'],rate=v['rate'],pitch=v['pitch'],volume='+0%',boundary='WordBoundary',proxy=os.environ.get('HTTPS_PROXY'))
   await speech.save(str(p.with_suffix('.mp3')),str(p.with_suffix('.jsonl')))
   cache.write_text(json.dumps({'sha256':digest,**req},ensure_ascii=False,indent=2)+'\n')
   print('Generated',v['id'],flush=True)
 await asyncio.gather(*(line(v) for v in json.loads((R/'script.json').read_text())))
 (R/'reports/voice-provider.json').write_text(json.dumps({'provider':'Microsoft Edge online speech catalog','voice':'ar-SA-HamedNeural','humanRecording':False,'voiceCloning':False,'contestantVoices':'3 catalog variations; fourth contestant silent','musicAdded':False,'postTimeStretch':False,'tlsVerification':True},indent=2)+'\n')
asyncio.run(main())
