"""Verify exact published V10 files after the Pages deployment succeeds."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT.parents[1] / 'public/ad/voice-original'
BASE = 'https://mdaar21.github.io/Mdaar21/ad/voice-original/'


def check(name):
    with urllib.request.urlopen(BASE + name, timeout=30) as response:
        data = response.read()
        digest = hashlib.sha256(data).hexdigest()
        assert digest == hashlib.sha256((PUBLIC / name).read_bytes()).hexdigest()
        return name, {'status': response.status, 'bytes': len(data), 'sha256': digest,
                      'contentType': response.headers.get('Content-Type')}


names = ['index.html', 'mdaar_tiktok_v10_original_clear.mp4', 'voice-clean.mp3', 'captions.srt', 'poster.jpg']
with ThreadPoolExecutor(max_workers=4) as pool:
    files = dict(pool.map(check, names))
assert 'video/mp4' in files['mdaar_tiktok_v10_original_clear.mp4']['contentType']
request = urllib.request.Request(BASE + 'mdaar_tiktok_v10_original_clear.mp4', headers={'Range': 'bytes=0-1023'})
with urllib.request.urlopen(request, timeout=30) as response:
    data = response.read()
    assert response.status == 206 and len(data) == 1024
    range_check = {'status': response.status, 'bytes': len(data), 'contentRange': response.headers.get('Content-Range')}
pages_commit = subprocess.check_output(['git', '-C', '/workspace/mdaar-ad-pages', 'rev-parse', 'HEAD'], text=True).strip()
report = {'ok': True, 'url': BASE, 'pagesCommit': pages_commit, 'files': files,
          'range': range_check, 'publishedBytesMatchValidatedMaster': True,
          'scope': 'Hosted files only; no TikTok posting or advertising campaign.'}
(ROOT / 'reports/live-verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'ok': True, 'url': BASE, 'files': len(files), 'range': range_check}))
