#!/usr/bin/env python3
"""Original cut-out assets for Mdaar's TikTok ad (decision d36).

Everything is drawn here from code: no photos, stock or traced artwork.
Palette (taste-color 60-30-10 with one accent): ink and warm paper neutrals,
gold as the single accent.

Usage: python3 creative/ad-assets/make_ad_assets.py
Writes creative/ad-assets/svg/<name>.svg. PNGs are rendered from these files.
"""
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'svg'
sys.path.insert(0, str(HERE.parents[1] / 'docs/book-home/figures'))
import make_figures as mf  # noqa: E402  (the book's figure renderer, same body style)

# ---- palette -----------------------------------------------------------------
INK, INK2 = '#0d0e0e', '#1b1a16'
CREAM, BEIGE, KRAFT = '#f3ead6', '#e2d3b2', '#c9b48a'
GOLD, GOLD_L, GOLD_D = '#d9ba7b', '#f0dba7', '#a9864a'
EDGE = '#fbf6ea'


def svg(w, h, body, defs=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<defs>{defs}</defs>{body}</svg>\n')


def paper_filter(fid, freq=.9, alpha=.10):
    return (f'<filter id="{fid}" x="-5%" y="-5%" width="110%" height="110%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="2" seed="7" result="n"/>'
            f'<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 {alpha} 0" result="g"/>'
            f'<feComposite in="g" in2="SourceGraphic" operator="in" result="t"/>'
            f'<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="t"/></feMerge></filter>'
            '<filter id="shadow" x="-10%" y="-10%" width="130%" height="130%"><feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#000" flood-opacity=".35"/></filter>')


# ---- torn paper scraps ---------------------------------------------------------
def torn_edge(a, b, rnd, step=9, amp=6):
    (x1, y1), (x2, y2) = a, b
    n = max(2, int(math.hypot(x2 - x1, y2 - y1) / step))
    nx, ny = -(y2 - y1), x2 - x1
    l = math.hypot(nx, ny) or 1
    nx, ny = nx / l, ny / l
    pts = []
    for i in range(n):
        t = i / n
        j = rnd.uniform(-amp, amp)
        pts.append((x1 + (x2 - x1) * t + nx * j, y1 + (y2 - y1) * t + ny * j))
    return pts


def scrap(name, w, h, fill, seed, shape='rect', fiber=EDGE):
    rnd = random.Random(seed)
    m = 26
    if shape == 'rect':
        corners = [(m, m + rnd.uniform(0, 14)), (w - m - rnd.uniform(0, 18), m), (w - m, h - m - rnd.uniform(0, 16)), (m + rnd.uniform(0, 14), h - m)]
    elif shape == 'strip':
        corners = [(m, m + 6), (w - m, m), (w - m - 8, h - m), (m + 4, h - m - 4)]
    elif shape == 'tri':
        corners = [(m, h - m), (w * .55, m), (w - m, h - m * 1.6)]
    else:  # irregular blob of torn edges
        cx, cy, r = w / 2, h / 2, min(w, h) / 2 - m
        corners = [(cx + math.cos(a) * r * rnd.uniform(.75, 1), cy + math.sin(a) * r * rnd.uniform(.75, 1))
                   for a in [k * 2 * math.pi / 7 for k in range(7)]]
    pts = []
    for i in range(len(corners)):
        pts += torn_edge(corners[i], corners[(i + 1) % len(corners)], rnd)
    d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z'
    # the white fibrous rim shows where the paper was torn
    body = (f'<g filter="url(#shadow)"><path d="{d}" fill="{fiber}"/>'
            f'<path d="{d}" fill="{fill}" transform="translate({w * .012:.1f} {h * .012:.1f}) scale(.976)" filter="url(#p)"/></g>')
    return name, svg(w, h, body, paper_filter('p'))


SCRAPS = [
    ('scrap-01-cream-wide', 620, 360, CREAM, 1, 'rect'),
    ('scrap-02-beige-square', 460, 440, BEIGE, 2, 'rect'),
    ('scrap-03-kraft-strip', 700, 200, KRAFT, 3, 'strip'),
    ('scrap-04-ink-card', 560, 380, INK2, 4, 'rect'),
    ('scrap-05-gold-note', 420, 320, GOLD, 5, 'rect'),
    ('scrap-06-cream-triangle', 480, 420, CREAM, 6, 'tri'),
    ('scrap-07-ink-strip', 680, 180, INK, 7, 'strip'),
    ('scrap-08-beige-blob', 460, 460, BEIGE, 8, 'blob'),
    ('scrap-09-gold-strip', 600, 170, GOLD_D, 9, 'strip'),
    ('scrap-10-cream-tall', 360, 620, CREAM, 10, 'rect'),
]


# ---- tape ------------------------------------------------------------------------
def tape(name, w, h, color, opacity, seed):
    rnd = random.Random(seed)
    zz = lambda x0, sign: [(x0 + sign * rnd.uniform(0, 7), 10 + i * (h - 20) / 8) for i in range(9)]
    left, right = zz(14, 1), zz(w - 14, -1)
    pts = left + [(p[0], p[1]) for p in reversed(right)]
    d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z'
    lines = ''.join(f'<path d="M{24 + k * 22} 12 V{h - 12}" stroke="#fff" stroke-opacity=".08" stroke-width="2"/>' for k in range((w - 40) // 22))
    return name, svg(w, h, f'<g opacity="{opacity}"><path d="{d}" fill="{color}"/>{lines}</g>')


TAPES = [('tape-01-cream', 300, 84, CREAM, .78, 11), ('tape-02-gold', 260, 76, GOLD, .72, 12), ('tape-03-kraft', 320, 90, KRAFT, .8, 13)]


# ---- gold shapes -----------------------------------------------------------------
def sparkle(r, cx, cy):
    k = r * .22
    return (f'M{cx} {cy - r} C{cx + k} {cy - k} {cx + k} {cy - k} {cx + r} {cy} C{cx + k} {cy + k} {cx + k} {cy + k} {cx} {cy + r} '
            f'C{cx - k} {cy + k} {cx - k} {cy + k} {cx - r} {cy} C{cx - k} {cy - k} {cx - k} {cy - k} {cx} {cy - r}Z')


GRAD = (f'<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6e7c6"/>'
        f'<stop offset=".55" stop-color="{GOLD}"/><stop offset="1" stop-color="{GOLD_D}"/></linearGradient>')

SHAPES = [
    ('star-01-sparkle', svg(300, 300, f'<path d="{sparkle(130, 150, 150)}" fill="url(#g)"/>', GRAD)),
    ('star-02-cluster', svg(360, 300, f'<path d="{sparkle(95, 140, 160)}" fill="url(#g)"/><path d="{sparkle(42, 280, 70)}" fill="{GOLD_L}"/>'
                         f'<path d="{sparkle(26, 300, 230)}" fill="{GOLD}"/>', GRAD)),
    ('circle-01-ring', svg(320, 320, f'<circle cx="160" cy="160" r="138" fill="none" stroke="url(#g)" stroke-width="10"/>'
                        f'<circle cx="160" cy="160" r="118" fill="none" stroke="{GOLD}" stroke-opacity=".35" stroke-width="2"/>', GRAD)),
    ('circle-02-dots', svg(420, 200, ''.join(f'<circle cx="{40 + i * 85}" cy="{100 + (25 if i % 2 else -25)}" r="{30 - i * 4}" fill="url(#g)"/>' for i in range(5)), GRAD)),
    ('circle-03-orbit', svg(460, 300, f'<ellipse cx="230" cy="150" rx="200" ry="70" fill="none" stroke="url(#g)" stroke-width="8" transform="rotate(-18 230 150)"/>'
                         f'<circle cx="345" cy="84" r="22" fill="url(#g)"/><circle cx="110" cy="220" r="10" fill="{GOLD_L}"/>', GRAD)),
    ('underline-01-gold', svg(520, 90, f'<path d="M20 58 C140 20 300 76 500 34" fill="none" stroke="url(#g)" stroke-width="14" stroke-linecap="round"/>', GRAD)),
    ('arrow-01-gold', svg(300, 240, f'<path d="M30 200 C70 90 150 60 240 70" fill="none" stroke="url(#g)" stroke-width="12" stroke-linecap="round"/>'
                       f'<path d="M210 38 L262 70 L218 112" fill="none" stroke="{GOLD}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>', GRAD)),
]


# ---- objects -----------------------------------------------------------------------
def obj(w, h, body, defs=''):
    return svg(w, h, f'<g filter="url(#shadow)">{body}</g>', defs + paper_filter('p'))


OBJECTS = [
    ('object-01-hand-phone', obj(520, 720,
        # stylised hand (ink with gold rim) holding a phone that shows the book cover tones
        f'<rect x="150" y="70" width="230" height="460" rx="36" fill="{INK}" stroke="{GOLD}" stroke-width="4"/>'
        f'<rect x="166" y="96" width="198" height="408" rx="22" fill="{INK2}"/>'
        f'<path d="{sparkle(34, 265, 220)}" fill="url(#g)"/>'
        f'<rect x="198" y="292" width="134" height="14" rx="7" fill="{GOLD_L}"/><rect x="214" y="320" width="102" height="10" rx="5" fill="{GOLD}" opacity=".7"/>'
        f'<rect x="196" y="420" width="138" height="46" rx="23" fill="url(#g)"/>'
        f'<path d="M118 700 C112 610 104 560 120 500 C132 452 150 430 150 410 L150 360 C150 340 176 336 182 356 L186 420 '
        f'L380 420 C404 420 420 440 416 466 C428 470 440 488 432 510 C446 518 450 540 438 556 C450 566 450 590 432 600 '
        f'C420 640 400 700 400 700 Z" fill="#2c2a25" stroke="{GOLD}" stroke-width="4" stroke-linejoin="round"/>'
        f'<path d="M380 466 H330 M384 512 H330 M382 556 H332" stroke="{GOLD}" stroke-opacity=".55" stroke-width="3" stroke-linecap="round"/>', GRAD)),
    ('object-02-house', obj(420, 380,
        f'<path d="M50 190 L210 50 L370 190" fill="none" stroke="url(#g)" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M90 175 V330 H330 V175" fill="{INK2}" stroke="{GOLD}" stroke-width="10" stroke-linejoin="round"/>'
        f'<rect x="180" y="230" width="60" height="100" rx="6" fill="url(#g)"/><rect x="250" y="80" width="34" height="62" fill="{GOLD_D}"/>', GRAD)),
    ('object-03-dumbbell', obj(520, 240,
        f'<rect x="130" y="104" width="260" height="32" rx="12" fill="#cfc6b3"/>'
        f'<rect x="60" y="40" width="44" height="160" rx="12" fill="{INK2}" stroke="{GOLD}" stroke-width="5"/>'
        f'<rect x="100" y="60" width="36" height="120" rx="10" fill="{INK2}" stroke="{GOLD}" stroke-width="5"/>'
        f'<rect x="416" y="40" width="44" height="160" rx="12" fill="{INK2}" stroke="{GOLD}" stroke-width="5"/>'
        f'<rect x="384" y="60" width="36" height="120" rx="10" fill="{INK2}" stroke="{GOLD}" stroke-width="5"/>')),
    ('object-04-chair', obj(360, 460,
        f'<rect x="80" y="40" width="22" height="380" rx="8" fill="{GOLD_D}"/><rect x="80" y="40" width="200" height="26" rx="10" fill="{GOLD}"/>'
        f'<rect x="80" y="110" width="200" height="18" rx="8" fill="{GOLD_D}"/>'
        f'<rect x="60" y="230" width="250" height="36" rx="12" fill="{INK2}" stroke="{GOLD}" stroke-width="5"/>'
        f'<rect x="276" y="250" width="22" height="170" rx="8" fill="{GOLD_D}"/><rect x="90" y="250" width="22" height="170" rx="8" fill="{GOLD_D}"/>')),
    ('object-05-tape-measure', obj(600, 320,
        f'<circle cx="150" cy="160" r="120" fill="{INK2}" stroke="{GOLD}" stroke-width="10"/><circle cx="150" cy="160" r="38" fill="url(#g)"/>'
        f'<path d="M150 280 H570 V230 H220" fill="{GOLD}" stroke="{GOLD_D}" stroke-width="3"/>'
        + ''.join(f'<path d="M{240 + i * 20} 232 V{246 if i % 5 else 258}" stroke="{INK}" stroke-width="3"/>' for i in range(17)), GRAD)),
]


# ---- exercise icons (book figure style, men only, one pose each) -----------------
def exercise_icon(name, muscles_key, pose_kwargs, weights=()):
    mf.CURRENT = mf.MUSCLES[muscles_key]
    J = mf.pose(**pose_kwargs)
    panel = (0, 0, 220, 220, 204, 190, 190)
    k = mf.fit(J, panel)
    P, s = mf.place(J, panel, 0, None, k * 1.0)
    body = ''.join(mf.figure(P, s, list(weights)))
    return name, svg(220, 220, f'<path d="M14 205 H206" stroke="{GOLD}" stroke-opacity=".6" stroke-width="2"/>{body}')


ICONS = [
    exercise_icon('icon-01-squat', 'e1', dict(t=38, legs=((92, 112), None), arms=((48, 118), (48, 118))), [('db', 'hand_n', 90)]),
    exercise_icon('icon-02-pushup', 'e4', dict(t=72, legs=((-72, 0), None), arms=((4, 0), (4, 0)), foot=(80, 80))),
    exercise_icon('icon-03-row', 'e6', dict(t=68, legs=((30, 34), (-14, 6)), arms=((-128, 128), (28, 0))), [('db', 'hand_n', 90)]),
    exercise_icon('icon-04-press', 'e5', dict(t=0, arms=((176, 0), (176, 0))), [('db', 'hand_f', 90), ('db', 'hand_n', 90)]),
    exercise_icon('icon-05-lunge', 'e3', dict(t=4, legs=((80, 88), (-28, 98)), foot=(0, 70)), [('db', 'hand_f', 0), ('db', 'hand_n', 0)]),
    exercise_icon('icon-06-bridge', 'e9', dict(t=-112, legs=((108, 122), None), arms=((80, 0), (80, 0)))),
]


# ---- full-screen backgrounds (1080x1920) -------------------------------------------
BG = [
    ('bg-01-beige-paper', svg(1080, 1920, f'<rect width="1080" height="1920" fill="{BEIGE}" filter="url(#p)"/>'
                          f'<rect width="1080" height="1920" fill="url(#v)"/>',
                          paper_filter('p', .75, .16) + '<radialGradient id="v" cx=".5" cy=".45" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#5a4728" stop-opacity=".25"/></radialGradient>')),
    ('bg-02-ink-gradient', svg(1080, 1920, f'<rect width="1080" height="1920" fill="url(#k)"/><rect width="1080" height="1920" fill="url(#gl)"/>'
                           f'<circle cx="540" cy="880" r="430" fill="none" stroke="{GOLD}" stroke-opacity=".10" stroke-width="2"/>'
                           f'<circle cx="540" cy="880" r="640" fill="none" stroke="{GOLD}" stroke-opacity=".07" stroke-width="2"/>',
                           f'<linearGradient id="k" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#151411"/><stop offset="1" stop-color="{INK}"/></linearGradient>'
                           f'<radialGradient id="gl" cx=".5" cy=".42" r=".55"><stop offset="0" stop-color="{GOLD}" stop-opacity=".16"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>')),
    ('bg-03-gold', svg(1080, 1920, f'<rect width="1080" height="1920" fill="url(#gg)"/><rect width="1080" height="1920" fill="url(#sh)" filter="url(#p)"/>',
                   f'<linearGradient id="gg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f3dfae"/><stop offset=".5" stop-color="{GOLD}"/><stop offset="1" stop-color="{GOLD_D}"/></linearGradient>'
                   '<linearGradient id="sh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".0"/><stop offset="1" stop-color="#000" stop-opacity=".12"/></linearGradient>'
                   + paper_filter('p', .8, .08))),
]


def all_assets():
    out = [scrap(*s) for s in SCRAPS] + [tape(*t) for t in TAPES] + SHAPES + OBJECTS + ICONS + BG
    return out


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in all_assets():
        (OUT / f'{name}.svg').write_text(data, encoding='utf-8')
    print(len(all_assets()), 'assets ->', OUT)
