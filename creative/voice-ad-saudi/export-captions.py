from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
groups = json.loads((ROOT/'captions.json').read_text())
def stamp(t):
    n = round(t*1000)
    return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
(ROOT/'captions.srt').write_text((''.join(f'{i+1}\n{stamp(g["start"])} --> {stamp(g["end"])}\n'
    +' '.join(w['text'] for w in g['words'])+'\n\n' for i,g in enumerate(groups))).rstrip()+'\n')
