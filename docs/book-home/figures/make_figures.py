#!/usr/bin/env python3
"""Draw the original exercise figures for «بروتوكول التحول: نسخة البيت».

Every figure is drawn from scratch here (no photos, thumbnails or traced
frames): a simple side-view man in two poses, start (1) and end (2), gold
lines on the dark book background, a dumbbell only in the dumbbell version,
and arrows that show the direction of the movement.

Usage: python3 docs/book-home/figures/make_figures.py
Writes docs/book-home/figures/<exerciseId>-<with|without>.svg (22 files).
The exercise ids match docs/book-home/videos.json (e1 … e11).
"""
from math import sin, cos, radians
from pathlib import Path

OUT = Path(__file__).resolve().parent

# ---- identity (same tokens as docs/book/book.css) ------------------------
BG, FRAME = '#12120f', '#b6955040'
NEAR, FAR = '#e3c584', '#8f7a4f'
HEAD, ACCENT = '#f0dba7', '#f0dba7'
FLOOR, PROP = '#b69550', '#6f6046'

W, H = 200, 150             # whole image (4:3)
PW = W / 2                  # one panel per pose (side by side)
FLOOR_Y = 136               # floor of the current panel (set per panel)
# panels: (x, y, width, height, floor y, max figure box w, h)
SIDE = [(100, 0, 100, 150, 136, 86, 112), (0, 0, 100, 150, 136, 86, 112)]      # 1 right, 2 left
STACK = [(0, 0, 200, 75, 66, 150, 46), (0, 75, 200, 75, 141, 150, 46)]          # 1 top, 2 bottom
# moves done lying or on all fours read better with the two poses stacked
STACKED = {'e4-with', 'e4-without', 'e6-without', 'e8-without', 'e9-with', 'e9-without', 'e11-without'}

# segment lengths of the figure (one unit system for every pose)
TORSO, NECK, HEAD_R = 36, 9, 6.5
THIGH, SHIN, FOOT = 25, 25, 8
UPPER, FORE = 17, 16


def vec(angle, length):
    """Angle in degrees from straight down, positive turns toward +x."""
    a = radians(angle)
    return (sin(a) * length, cos(a) * length)


def add(p, v):
    return (p[0] + v[0], p[1] + v[1])


def limb_leg(hip, th, kn, fa):
    knee = add(hip, vec(th, THIGH))
    ankle = add(knee, vec(th - kn, SHIN))
    toe = add(ankle, (cos(radians(fa)) * FOOT, sin(radians(fa)) * FOOT))
    return knee, ankle, toe


def limb_arm(shoulder, s, e):
    elbow = add(shoulder, vec(s, UPPER))
    hand = add(elbow, vec(s + e, FORE))
    return elbow, hand


def pose(t=0, legs=((0, 0), None), arms=((8, 6), (-6, 6)), foot=(0, None), head=0):
    """Build joint coordinates around hip=(0,0).

    t: torso lean from vertical (+ forward, -90 lying on the back, head to -x).
    legs/arms: (near, far) pairs of (angle, bend); far=None copies near.
    """
    hip = (0.0, 0.0)
    up = (sin(radians(t)), -cos(radians(t)))
    neck = (up[0] * TORSO, up[1] * TORSO)
    h = radians(t + head)
    head_c = add(neck, (sin(h) * (NECK + HEAD_R * .3), -cos(h) * (NECK + HEAD_R * .3)))
    near_leg, far_leg = legs[0], legs[1] or legs[0]
    near_arm, far_arm = arms[0], arms[1] or arms[0]
    fa_near, fa_far = foot[0], foot[1] if foot[1] is not None else foot[0]
    J = {'hip': hip, 'neck': neck, 'head': head_c}
    J['knee_n'], J['ankle_n'], J['toe_n'] = limb_leg(hip, *near_leg, fa_near)
    J['knee_f'], J['ankle_f'], J['toe_f'] = limb_leg(hip, *far_leg, fa_far)
    J['elbow_n'], J['hand_n'] = limb_arm(neck, *near_arm)
    J['elbow_f'], J['hand_f'] = limb_arm(neck, *far_arm)
    return J


def fit(J, panel):
    bw, bh = panel[5], panel[6]
    xs = [p[0] for p in J.values()]
    ys = [p[1] for p in J.values()]
    return min(1.6, bw / (max(xs) - min(xs) + 2 * HEAD_R), bh / (max(ys) - min(ys) + 2 * HEAD_R))


def place(J, panel, ground=0.0, anchor=None, scale=1.0):
    """Scale the pose and stand it on the floor of its panel."""
    x0, _, pw, _, floor = panel[:5]
    xs = [p[0] for p in J.values()]
    ys = [p[1] for p in J.values()]
    s = scale
    cx = (max(xs) + min(xs)) / 2
    bottom = J[anchor][1] if anchor else max(max(ys), J['head'][1] + HEAD_R)
    ox = x0 + pw / 2
    return {k: (ox + (p[0] - cx) * s, floor - ground - (bottom - p[1]) * s) for k, p in J.items()}, s


def line(points, color, width, opacity=1.0):
    d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in points)
    op = '' if opacity == 1 else f' stroke-opacity="{opacity}"'
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{op}/>'


def dumbbell(c, s, angle=0, color=NEAR):
    """A dumbbell seen from the side: handle with two plates."""
    x, y = c
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({angle}) scale({s:.2f})">'
            f'<g stroke="#12120f" stroke-width=".9"><rect x="-7" y="-1.3" width="14" height="2.6" rx="1" fill="{color}"/>'
            f'<rect x="-9.8" y="-5.2" width="4.2" height="10.4" rx="1.4" fill="{color}"/>'
            f'<rect x="5.6" y="-5.2" width="4.2" height="10.4" rx="1.4" fill="{color}"/></g></g>')


def backpack(c, s):
    x, y = c
    return (f'<g transform="translate({x:.1f} {y + 7 * s:.1f}) scale({s:.2f})">'
            f'<path d="M-3 -9 Q0 -13 3 -9" fill="none" stroke="{METAL}" stroke-width="1.6"/>'
            f'<rect x="-6" y="-9" width="12" height="15" rx="3.5" fill="#3a352c" stroke="{METAL}" stroke-width="1.8"/>'
            f'<path d="M-3.5 -1 H3.5" stroke="{METAL}" stroke-width="1.6" stroke-linecap="round"/></g>')


# ---- volumetric body (style of the first book's anatomy diagram) -----------
BODY, BODY_EDGE = '#2c2a25', '#5b5346'          # near side
BODY_FAR, EDGE_FAR = '#1d1c19', '#3b372f'        # far side
GOLD, GOLD_FAR = '#d9ba7b', '#9c7d47'           # target muscles
METAL, METAL_EDGE = '#e9e2d2', '#12120f'         # dumbbells: ivory, never gold

# target muscles per exercise (drawn gold): thigh, shin, glute, chest, abs,
# upper_back, lower_back, shoulder, upper_arm
MUSCLES = {
    'e1': {'thigh', 'glute'}, 'e2': {'thigh', 'glute', 'lower_back'}, 'e3': {'thigh', 'glute'},
    'e4': {'chest', 'upper_arm', 'shoulder'}, 'e5': {'shoulder', 'upper_arm'}, 'e6': {'upper_back', 'upper_arm'},
    'e7': {'upper_arm'}, 'e8': {'upper_arm'}, 'e9': {'glute', 'thigh'}, 'e10': {'shin'}, 'e11': {'abs'},
}
CURRENT = set()


def norm(v):
    l = (v[0] ** 2 + v[1] ** 2) ** .5 or 1
    return (v[0] / l, v[1] / l)


def capsule(a, b, wa, wb, fill, edge, ew=.9):
    """Tapered limb segment with round ends."""
    d = norm((b[0] - a[0], b[1] - a[1]))
    n = (-d[1], d[0])
    pts = [(a[0] + n[0] * wa / 2, a[1] + n[1] * wa / 2), (b[0] + n[0] * wb / 2, b[1] + n[1] * wb / 2),
           (b[0] - n[0] * wb / 2, b[1] - n[1] * wb / 2), (a[0] - n[0] * wa / 2, a[1] - n[1] * wa / 2)]
    poly = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    return (f'<g fill="{fill}" stroke="{edge}" stroke-width="{ew}"><circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="{wa / 2:.1f}"/>'
            f'<circle cx="{b[0]:.1f}" cy="{b[1]:.1f}" r="{wb / 2:.1f}"/><polygon points="{poly}"/>'
            f'<polygon points="{poly}" stroke="none"/></g>')


def poly(points, fill, edge='none', ew=.8):
    return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in points)}" fill="{fill}" stroke="{edge}" stroke-width="{ew}" stroke-linejoin="round"/>'


def figure(P, s, weights=None):
    """Far limbs first and darker, then torso, near limbs and head."""
    k = s
    hip, neck = P['hip'], P['neck']
    u = norm((neck[0] - hip[0], neck[1] - hip[1]))      # up the spine
    f = (-u[1], u[0])                                    # toward the chest
    at = lambda base, du, df: (base[0] + u[0] * du * k + f[0] * df * k, base[1] + u[1] * du * k + f[1] * df * k)
    sh = at(neck, -3, 0)                                 # shoulder joint
    off = (-2.2 * k, -1.2 * k)
    F = lambda j: add(P[j], off)
    sh_f = add(sh, off)
    out = []

    def leg(knee, ankle, toe, near):
        fill, edge = (BODY, BODY_EDGE) if near else (BODY_FAR, EDGE_FAR)
        g = GOLD if near else GOLD_FAR
        h = hip if near else add(hip, off)
        res = [capsule(h, knee, 10 * k, 7 * k, g if 'thigh' in CURRENT else fill, edge),
               capsule(knee, ankle, 6.6 * k, 4.4 * k, g if 'shin' in CURRENT else fill, edge),
               capsule(ankle, toe, 4.2 * k, 3.2 * k, fill, edge)]
        return res

    def arm(shoulder, elbow, hand, near):
        fill, edge = (BODY, BODY_EDGE) if near else (BODY_FAR, EDGE_FAR)
        g = GOLD if near else GOLD_FAR
        res = [capsule(shoulder, elbow, 6.4 * k, 5 * k, g if 'upper_arm' in CURRENT else fill, edge),
               capsule(elbow, hand, 4.8 * k, 3.6 * k, fill, edge)]
        if 'shoulder' in CURRENT:
            res.append(f'<circle cx="{shoulder[0]:.1f}" cy="{shoulder[1]:.1f}" r="{4 * k:.1f}" fill="{g}" stroke="{edge}" stroke-width=".8"/>')
        return res

    out += arm(sh_f, F('elbow_f'), F('hand_f'), False)
    out += leg(F('knee_f'), F('ankle_f'), F('toe_f'), False)
    # torso: side view, deeper at the chest than at the waist
    mid = at(hip, 17, 0)
    torso = [at(hip, -2, -5.5), at(hip, -2, 5), at(mid, 0, 4.6), at(neck, -9, 7), at(neck, 0, 4.5),
             at(neck, 1, -4.5), at(neck, -10, -6.4), at(mid, 0, -5.2)]
    out.append(poly(torso, BODY, BODY_EDGE, 1))
    if 'chest' in CURRENT:
        out.append(poly([at(neck, -2.5, 4.4), at(neck, -9, 7), at(neck, -15, 5.6), at(neck, -14, 1.5), at(neck, -3, 1.2)], GOLD))
    if 'abs' in CURRENT:
        out.append(poly([at(neck, -16, 5.4), at(mid, 0, 4.6), at(hip, 2, 5), at(hip, 3, 1.4), at(neck, -16, 1.6)], GOLD))
    if 'upper_back' in CURRENT:
        out.append(poly([at(neck, 0, -4.4), at(neck, -10, -6.4), at(neck, -19, -5.6), at(neck, -18, -1.6), at(neck, -1, -1.4)], GOLD))
    if 'lower_back' in CURRENT:
        out.append(poly([at(mid, 2, -5.3), at(hip, 3, -5.6), at(hip, 3, -2.6), at(mid, 2, -2.4)], GOLD))
    if 'glute' in CURRENT:
        c = at(hip, -.5, -3.2)
        out.append(f'<ellipse cx="{c[0]:.1f}" cy="{c[1]:.1f}" rx="{5.6 * k:.1f}" ry="{5.6 * k:.1f}" fill="{GOLD}"/>')
    out += leg(P['knee_n'], P['ankle_n'], P['toe_n'], True)
    # neck and head
    out.append(capsule(at(neck, -1, .5), P['head'], 4.2 * k, 4.2 * k, BODY, BODY_EDGE))
    out.append(f'<circle cx="{P["head"][0]:.1f}" cy="{P["head"][1]:.1f}" r="{HEAD_R * k:.1f}" fill="{BODY}" stroke="{BODY_EDGE}" stroke-width="1"/>')
    out += arm(sh, P['elbow_n'], P['hand_n'], True)
    for kind, joint, ang in (weights or []):
        if kind == 'db':
            pos = F(joint) if joint.endswith('_f') else P[joint]
            item = dumbbell(pos, k * .9, ang, METAL)
            if joint.endswith('_f'):
                out.insert(2, item)
            else:
                out.append(item)
        elif kind == 'bag':
            out.append(backpack(P[joint], k))
    return out


def arrow(a, b, curve=0.0):
    """Straight or curved arrow from a to b (screen coordinates)."""
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dx, dy = b[0] - a[0], b[1] - a[1]
    cx, cy = mx - dy * curve, my + dx * curve
    return (f'<path d="M{a[0]:.1f} {a[1]:.1f} Q{cx:.1f} {cy:.1f} {b[0]:.1f} {b[1]:.1f}" fill="none" '
            f'stroke="{ACCENT}" stroke-width="2" stroke-linecap="round" marker-end="url(#ah)"/>')


def badge(panel, n):
    x, y = panel[0] + panel[2] - 12, panel[1] + 13
    return (f'<circle cx="{x}" cy="{y}" r="7" fill="none" stroke="{FLOOR}" stroke-width="1.2"/>'
            f'<text x="{x}" y="{y + 3.6}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" '
            f'font-size="10" font-weight="700" fill="{HEAD}">{n}</text>')


# ---- props -----------------------------------------------------------------
def chair(x, seat_y, facing=1):
    top = FLOOR_Y
    back = x - 9 * facing
    return line([(x - 10, seat_y), (x + 10, seat_y)], PROP, 2.4) + \
        line([(x - 9, seat_y), (x - 9, top)], PROP, 2) + line([(x + 9, seat_y), (x + 9, top)], PROP, 2) + \
        line([(back, seat_y), (back, seat_y - 22)], PROP, 2)


def table(x1, x2, top_y):
    return line([(x1, top_y), (x2, top_y)], PROP, 3) + \
        line([(x1 + 3, top_y), (x1 + 3, FLOOR_Y)], PROP, 2.2) + line([(x2 - 3, top_y), (x2 - 3, FLOOR_Y)], PROP, 2.2)


def step(x1, x2, h):
    return f'<rect x="{x1:.1f}" y="{FLOOR_Y - h:.1f}" width="{x2 - x1:.1f}" height="{h:.1f}" rx="1.5" fill="none" stroke="{PROP}" stroke-width="2"/>'


def diamond(c):
    x, y = c
    return f'<path d="M{x:.1f} {y - 4:.1f} L{x + 4:.1f} {y:.1f} L{x:.1f} {y + 4:.1f} L{x - 4:.1f} {y:.1f} Z" fill="none" stroke="{ACCENT}" stroke-width="1.4"/>'


# ---- the 22 figures ----------------------------------------------------------
# Each entry: (start pose kwargs, end pose kwargs, extras(start P, end P, s) -> svg parts)
STAND = dict(t=0, legs=((0, 0), (0, 0)), arms=((0, 0), (0, 0)))
SQUAT_LEGS = ((92, 112), None)
SUPINE_KNEES = ((140, 128), None)


def up_arrow(P, joint, dy=-18, dx=0, off=(10, 0)):
    a = add(P[joint], off)
    return arrow(a, (a[0] + dx, a[1] + dy))


def down_arrow(P, joint, dy=18, dx=0, off=(10, 0)):
    a = add(P[joint], off)
    return arrow(a, (a[0] + dx, a[1] + dy))


FIGS = {
    # 1. Squat
    'e1-with': (
        dict(t=0, arms=((18, 128), (18, 128))),
        dict(t=38, legs=SQUAT_LEGS, arms=((48, 118), (48, 118))),
        lambda A, B, s: [down_arrow(B, 'hip', off=(-16, -22))],
        [('db', 'hand_n', 90)]),
    'e1-without': (
        dict(t=0),
        dict(t=38, legs=SQUAT_LEGS, arms=((88, 0), (88, 0))),
        lambda A, B, s: [down_arrow(B, 'hip', off=(-16, -22))],
        []),
    # 2. Hip hinge
    'e2-with': (
        dict(t=0, legs=((0, 4), None)),
        dict(t=72, legs=((-6, 14), None), arms=((-4, 0), (-4, 0))),
        lambda A, B, s: [arrow(add(B['neck'], (-6, -16)), add(B['neck'], (8, -4)), .35)],
        [('db', 'hand_f', 0), ('db', 'hand_n', 0)]),
    'e2-without': (
        dict(t=0, legs=((0, 4), (0, 4))),
        dict(t=82, legs=((-4, 12), (-92, 0)), arms=((-2, 0), (-2, 0))),
        lambda A, B, s: [arrow(add(B['neck'], (-6, -16)), add(B['neck'], (8, -4)), .35),
                         arrow(add(B['toe_f'], (16, 14)), add(B['toe_f'], (4, -6)), -.3)],
        []),
    # 3. Reverse lunge
    'e3-with': (
        dict(t=0),
        dict(t=4, legs=((80, 88), (-28, 98)), foot=(0, 70)),
        lambda A, B, s: [down_arrow(B, 'hip', off=(-14, -22)), arrow(add(B['knee_f'], (6, 10)), add(B['knee_f'], (-12, 10)))],
        [('db', 'hand_f', 0), ('db', 'hand_n', 0)]),
    'e3-without': (
        dict(t=0, arms=((-32, 52), (-32, 52))),
        dict(t=4, legs=((80, 88), (-28, 98)), arms=((-32, 52), (-32, 52)), foot=(0, 70)),
        lambda A, B, s: [down_arrow(B, 'hip', off=(-14, -22)), arrow(add(B['knee_f'], (6, 10)), add(B['knee_f'], (-12, 10)))],
        []),
    # 4. Chest press
    'e4-with': (
        dict(t=-90, legs=SUPINE_KNEES, arms=((94, 80), (94, 80))),
        dict(t=-90, legs=SUPINE_KNEES, arms=((178, 0), (178, 0))),
        lambda A, B, s: [up_arrow(B, 'hand_n', dy=-14, off=(9, 18))],
        [('db', 'hand_f', 90), ('db', 'hand_n', 90)]),
    'e4-without': (
        dict(t=84, legs=((-84, 0), None), arms=((-62, 62), (-62, 62)), foot=(80, 80)),
        dict(t=72, legs=((-72, 0), None), arms=((4, 0), (4, 0)), foot=(80, 80)),
        lambda A, B, s: [up_arrow(B, 'neck', dy=-14, off=(-8, -6))],
        []),
    # 5. Shoulder press
    'e5-with': (  # seated on a chair, as in the video and the book text («جالس»)
        dict(t=-6, legs=((88, 88), (84, 84)), arms=((28, 152), (28, 152))),
        dict(t=-6, legs=((88, 88), (84, 84)), arms=((176, 0), (176, 0))),
        lambda A, B, s: [up_arrow(B, 'elbow_n', dy=-16, off=(12, 4))],
        [('db', 'hand_f', 90), ('db', 'hand_n', 90)]),
    'e5-without': (
        dict(t=128, legs=((-34, 0), None), arms=((-6, 0), (-6, 0)), foot=(10, 10), head=10),
        dict(t=128, legs=((-34, 0), None), arms=((-40, 58), (-40, 58)), foot=(10, 10), head=10),
        lambda A, B, s: [down_arrow(B, 'head', dy=14, off=(10, -6))],
        []),
    # 6. Row
    'e6-with': (
        dict(t=68, legs=((30, 34), (-14, 6)), arms=((2, 0), (28, 0))),
        dict(t=68, legs=((30, 34), (-14, 6)), arms=((-128, 128), (28, 0))),
        lambda A, B, s: [up_arrow(B, 'elbow_n', dy=-14, off=(-6, -4))],
        [('db', 'hand_n', 90)]),
    'e6-without': (
        dict(t=-78, legs=((78, 0), None), arms=((168, 0), (168, 0)), foot=(-80, -80)),
        dict(t=-72, legs=((72, 0), None), arms=((120, 74), (120, 74)), foot=(-80, -80)),
        lambda A, B, s: [up_arrow(B, 'neck', dy=-12, off=(4, -2))],
        [('anchor', 'ankle_n')]),
    # 7. Biceps curl
    'e7-with': (
        dict(t=0, arms=((4, 0), (4, 0))),
        dict(t=0, arms=((4, 138), (4, 138))),
        lambda A, B, s: [arrow(add(B['elbow_n'], (14, 6)), add(B['elbow_n'], (12, -16)), -.45)],
        [('db', 'hand_f', 90), ('db', 'hand_n', 90)]),
    'e7-without': (
        dict(t=0, arms=((4, 0), (4, 0))),
        dict(t=0, arms=((4, 138), (4, 138))),
        lambda A, B, s: [arrow(add(B['elbow_n'], (14, 6)), add(B['elbow_n'], (12, -16)), -.45)],
        [('bag', 'hand_n', 0)]),
    # 8. Triceps
    'e8-with': (
        dict(t=0, arms=((168, -186), (168, -186))),
        dict(t=0, arms=((172, 0), (172, 0))),
        lambda A, B, s: [up_arrow(B, 'hand_n', dy=-12, off=(9, 14))],
        [('db', 'hand_n', 0)]),
    'e8-without': (
        dict(t=84, legs=((-84, 0), None), arms=((-30, 30), (-30, 30)), foot=(80, 80)),
        dict(t=72, legs=((-72, 0), None), arms=((4, 0), (4, 0)), foot=(80, 80)),
        lambda A, B, s: [up_arrow(B, 'neck', dy=-14, off=(-8, -6))],
        [('diamond', 'hand_n', 0)]),
    # 9. Glute bridge
    'e9-with': (
        dict(t=-90, legs=SUPINE_KNEES, arms=((92, 0), (92, 0))),
        dict(t=-112, legs=((108, 122), None), arms=((80, 0), (80, 0))),
        lambda A, B, s: [up_arrow(B, 'hip', dy=-14, off=(0, -10))],
        [('db', 'hip', 0)]),
    'e9-without': (
        dict(t=-90, legs=SUPINE_KNEES, arms=((92, 0), (92, 0))),
        dict(t=-112, legs=((108, 122), None), arms=((80, 0), (80, 0))),
        lambda A, B, s: [up_arrow(B, 'hip', dy=-14, off=(0, -8))],
        []),
    # 10. Calf raise
    'e10-with': (
        dict(t=0),
        dict(t=0, foot=(42, 42)),
        lambda A, B, s: [up_arrow(B, 'head', dy=-12, off=(14, 6))],
        [('db', 'hand_f', 90), ('db', 'hand_n', 90)]),
    'e10-without': (
        dict(t=0, legs=((0, 0), (-8, 78)), arms=((64, 0), (-6, 6)), foot=(-14, 0)),
        dict(t=0, legs=((0, 0), (-8, 78)), arms=((64, 0), (-6, 6)), foot=(42, 0)),
        lambda A, B, s: [up_arrow(B, 'head', dy=-12, off=(14, 6))],
        ['step']),
    # 11. Core
    'e11-with': (
        dict(t=-38, legs=((128, 112), None), arms=((70, 40), (70, 40)), foot=(30, 30)),
        dict(t=-38, legs=((128, 112), None), arms=((70, 40), (70, 40)), foot=(30, 30)),
        None,
        ['twist']),
    'e11-without': (
        dict(t=-90, legs=((180, 90), None), arms=((180, 0), (180, 0))),
        dict(t=-90, legs=((180, 90), (96, 0)), arms=((-104, 0), (180, 0))),
        lambda A, B, s: [arrow(add(B['hand_n'], (14, -14)), add(B['hand_n'], (2, -4)), .3),
                         arrow(add(B['ankle_f'], (-18, -16)), add(B['ankle_f'], (-4, -6)), -.3)],
        []),
}


def build(name, start, end, extra, weights):
    global FLOOR_Y, CURRENT
    CURRENT = MUSCLES[name.split('-')[0]]
    stacked = name in STACKED
    P1, P2 = STACK if stacked else SIDE
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img">',
             '<defs><marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
             f'<path d="M0 0 L10 5 L0 10 Z" fill="{ACCENT}"/></marker></defs>',
             f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="8" fill="{BG}" stroke="{FRAME}"/>']
    if stacked:
        parts += [line([(10, P1[4]), (W - 10, P1[4])], FLOOR, 1.2, .55), line([(10, P2[4]), (W - 10, P2[4])], FLOOR, 1.2, .55),
                  f'<path d="M14 75 H{W - 14}" stroke="{FRAME}" stroke-dasharray="3 4"/>']
    else:
        parts += [line([(10, FLOOR_Y), (W - 10, FLOOR_Y)], FLOOR, 1.2, .55),
                  f'<path d="M{PW} 24 V{FLOOR_Y - 8}" stroke="{FRAME}" stroke-dasharray="3 4"/>']
    # Start pose (1) is read first: right panel in Arabic, or the top one when stacked.
    ground = 12 if 'step' in weights else 0
    anchor = next((x[1] for x in weights if isinstance(x, tuple) and x[0] == 'anchor'), None)
    JA, JB = pose(**start), pose(**end)
    k = min(fit(JA, P1), fit(JB, P2))  # one scale for both poses
    A, sa = place(JA, P1, ground, anchor, k)
    B, sb = place(JB, P2, ground, anchor, k)
    for P, panel in ((A, P1), (B, P2)):
        FLOOR_Y = panel[4]
        if 'step' in weights:
            parts.append(step(P['toe_n'][0] - 9, P['toe_n'][0] + 7, ground))
            parts.append(line([(P['hand_n'][0] + 3, 30), (P['hand_n'][0] + 3, FLOOR_Y)], PROP, 1.8, .8))
        if name == 'e6-with':
            parts.append(chair(P['hand_f'][0], P['hand_f'][1] + 1))
        if name == 'e5-with':
            parts.append(chair(P['hip'][0] + 5, P['hip'][1] + 3))
        if name == 'e6-without':
            parts.append(table(P['hand_n'][0] - 16, P['hand_n'][0] + 14, P['hand_n'][1] - 1))
    FLOOR_Y = 136
    w = [x for x in weights if isinstance(x, tuple) and x[0] in ('db', 'bag')]
    for P, s in ((A, sa), (B, sb)):
        parts += figure(P, s, w)
        if any(isinstance(x, tuple) and x[0] == 'diamond' for x in weights):
            parts.append(diamond(add(P["hand_n"], (0, -4))))
    if 'twist' in weights:
        # Dumbbell held in front, moved from the near side (1) to the far side (2).
        parts.append(dumbbell(add(A['hand_n'], (2, 6)), sa * .82, 90, NEAR))
        parts.append(dumbbell(add(B['hand_n'], (-10, -6)), sb * .82, 90, FAR))
        hx, hy = B['neck']
        parts.append(f'<path d="M{hx + 30:.1f} {hy + 10:.1f} A20 7 0 1 1 {hx - 4:.1f} {hy + 2:.1f}" fill="none" stroke="{ACCENT}" '
                     f'stroke-width="2" stroke-linecap="round" marker-end="url(#ah)"/>')
    if extra:
        parts += extra(A, B, sb)
    parts += [badge(P1, 1), badge(P2, 2), '</svg>']
    return '\n'.join(parts) + '\n'


TITLES = {
    'e1': ('سكوات الكأس بدمبل', 'سكوات بوزن الجسم'),
    'e2': ('رفعة رومانية بدمبلين', 'رفعة رومانية بساق واحدة'),
    'e3': ('لانج للخلف بدمبلين', 'لانج للخلف بوزن الجسم'),
    'e4': ('ضغط دمبلين على الأرض', 'تمرين الضغط'),
    'e5': ('ضغط الكتف بدمبلين', 'ضغط البايك'),
    'e6': ('سحب دمبل بيد واحدة', 'سحب تحت الطاولة'),
    'e7': ('رفع الدمبلين للبايسبس', 'رفع حقيبة الظهر للبايسبس'),
    'e8': ('تمدد الترايسبس فوق الرأس', 'ضغط الألماسة'),
    'e9': ('جسر الأرداف بدمبل', 'جسر الأرداف بوزن الجسم'),
    'e10': ('رفع الكعبين واقفًا بدمبلين', 'رفع الكعب بساق واحدة'),
    'e11': ('التفاف روسي بدمبل', 'الحشرة الميتة'),
}

if __name__ == '__main__':
    for name, (start, end, extra, weights) in FIGS.items():
        ex, ver = name.split('-')
        title = TITLES[ex][0 if ver == 'with' else 1]
        svg = build(name, start, end, extra, weights)
        svg = svg.replace('role="img">', f'role="img" aria-label="{title}: وضع البداية (1) ووضع النهاية (2)"><title>{title}</title>', 1)
        (OUT / f'{name}.svg').write_text(svg, encoding='utf-8')
    print(f'{len(FIGS)} figures written to {OUT}')
