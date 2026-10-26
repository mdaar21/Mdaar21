"""New authorized Saudi narrator, with original provider word boundaries."""
from pathlib import Path
import asyncio
import hashlib
import json
import os

# Use the execution environment's trusted CA bundle, keeping TLS verification on.
import certifi
if Path('/etc/ssl/certs/ca-certificates.crt').exists():
    certifi.where = lambda: '/etc/ssl/certs/ca-certificates.crt'
import edge_tts

ROOT = Path(__file__).resolve().parent
VOICE = 'ar-SA-HamedNeural'
RATE = '+10%'


async def main():
    script = json.loads((ROOT / 'script.json').read_text())
    semaphore = asyncio.Semaphore(2)
    async def line(item):
        async with semaphore:
            identity = dict(item, voice=VOICE, rate=RATE, pitch='+0Hz', volume='+0%')
            digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
            path = ROOT / 'assets/voice' / (item['id'] + '.mp3')
            words = ROOT / 'assets/voice' / (item['id'] + '.jsonl')
            cache = path.with_suffix('.request.json')
            if path.exists() and words.exists() and cache.exists() and json.loads(cache.read_text()).get('sha256') == digest:
                print('Cached ' + item['id'], flush=True)
                return
            request = edge_tts.Communicate(item['text'], voice=VOICE, rate=RATE,
                volume='+0%', pitch='+0Hz', boundary='WordBoundary',
                proxy=os.environ.get('HTTPS_PROXY'))
            await request.save(str(path), str(words))
            assert path.stat().st_size > 1000 and words.stat().st_size > 0
            cache.write_text(json.dumps({'sha256': digest, **identity}, ensure_ascii=False, indent=2) + '\n')
            print('Generated ' + item['id'], flush=True)
    await asyncio.gather(*(line(item) for item in script))
    (ROOT / 'reports/voice-provider.json').write_text(json.dumps({
        'provider': 'Microsoft Edge online speech catalog', 'voice': VOICE, 'locale': 'ar-SA',
        'rate': RATE, 'pitch': '+0Hz', 'clips': len(script), 'boundary': 'WordBoundary',
        'ownerSelectedNewNarrator': True, 'humanRecording': False, 'voiceCloning': False,
        'reason': 'Owner requested a different Saudi narrator. No HeyGen/ElevenLabs credentials configured; Arabic is unsupported by local Kokoro. Online Saudi catalog voice selected explicitly for locale; no silent local fallback.',
        'tlsVerification': True}, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    asyncio.run(main())
