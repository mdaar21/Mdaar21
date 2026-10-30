from pathlib import Path
import json,urllib.request,hashlib,concurrent.futures
R=Path(__file__).resolve().parent
manifest=json.loads((R/'reports/deliverables.json').read_text());base=manifest['base']
def one(f):
 u=base+f['file'];req=urllib.request.Request(u,headers={'User-Agent':'Mdaar-Ad-Verification/1.0','Cache-Control':'no-cache'})
 with urllib.request.urlopen(req,timeout=40) as resp:
  data=resp.read();status=resp.status;ctype=resp.headers.get('Content-Type')
 digest=hashlib.sha256(data).hexdigest();assert status==200 and digest==f['sha256'],(u,status,digest)
 v={'url':u,'status':status,'bytes':len(data),'sha256':digest,'contentType':ctype}
 if f['file'].endswith('.mp4'):
  with urllib.request.urlopen(urllib.request.Request(u,headers={'Range':'bytes=0-1023'}),timeout=20) as resp:
   d=resp.read();assert resp.status==206 and len(d)==1024
   v.update(rangeStatus=resp.status,rangeBytes=len(d),contentRange=resp.headers.get('Content-Range'))
 return v
with concurrent.futures.ThreadPoolExecutor(3) as pool:results=list(pool.map(one,manifest['files']))
(R/'reports/live.json').write_text(json.dumps({'ok':True,'files':results,'verifiedAt':'2026-10-30','limits':'Reachability and file identity, not human listening, full-motion acting or audience effectiveness.'},indent=2)+'\n');print(json.dumps(results))
