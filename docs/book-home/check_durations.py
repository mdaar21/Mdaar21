#!/usr/bin/env python3
"""Print the length of every video in videos.json. Run it on YOUR computer.

Usage: python3 docs/book-home/check_durations.py [--max 45]

Needs yt-dlp on PATH (pip install yt-dlp). YouTube blocks yt-dlp from cloud
servers, so this only works from a normal home or office connection.
It only reads public metadata and never downloads video files.
Videos longer than --max seconds (default 45) are marked LONG.
"""
import json
import subprocess
import sys
from pathlib import Path

HOME = Path(__file__).resolve().parent
limit = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 45
videos = json.loads((HOME / 'videos.json').read_text(encoding='utf-8'))['videos']
print(f'{"exercise":9} {"version":14} {"seconds":8} status   url')
for v in videos:
    r = subprocess.run(['yt-dlp', '--skip-download', '--no-warnings', '--print', '%(duration)s', v['url']],
                       capture_output=True, text=True, timeout=120)
    out = r.stdout.strip().splitlines()
    sec = int(float(out[0])) if r.returncode == 0 and out and out[0] not in ('NA', 'None') else None
    status = 'ERROR' if sec is None else ('LONG' if sec > limit else 'ok')
    print(f'{v["exerciseId"]:9} {v["version"]:14} {str(sec):8} {status:8} {v["url"]}')
