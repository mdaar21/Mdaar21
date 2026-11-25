#!/usr/bin/env python3
"""Program-opener and day pages for «بروتوكول التحول: نسخة البيت».

Same layout idea as the first book's «5 أيام تمرين» and «يوم الدفع» pages:
a big gold number with day boxes, and a day page with an original front/back
body diagram where the day's muscles are coloured gold.

The body diagram is drawn here from simple shapes (original artwork). Every
muscle is its own shape with a class (m-chest, m-back …); home.css colours the
ones listed in the diagram's data-on attribute, so the same markup serves
every day:  <div class="bodymap" data-on="chest shoulders triceps">…</div>

Use from build.py:
    from pages import divider_page, day_page, MUSCLE_NAMES
Or run it to refresh the previews divider.html and day.html:
    python3 docs/book-home/pages.py
"""
import html
from pathlib import Path

HOME = Path(__file__).resolve().parent

# muscle id -> (Arabic, English)
MUSCLE_NAMES = {
    'chest': ('الصدر', 'Chest'), 'shoulders': ('الأكتاف', 'Shoulders'), 'triceps': ('الترايسبس', 'Triceps'),
    'back': ('الظهر', 'Back'), 'biceps': ('البايسبس', 'Biceps'), 'abs': ('البطن', 'Abs'),
    'lowerback': ('أسفل الظهر', 'Lower back'), 'glutes': ('الأرداف', 'Glutes'), 'quads': ('الفخذ الأمامي', 'Quads'),
    'hamstrings': ('الفخذ الخلفي', 'Hamstrings'), 'calves': ('السمانة', 'Calves'),
}

# exercise id (videos.json) -> muscles shown on the diagram
EXERCISE_MUSCLES = {
    'e1': ['quads', 'glutes'], 'e2': ['hamstrings', 'glutes', 'lowerback'], 'e3': ['quads', 'glutes'],
    'e4': ['chest', 'triceps'], 'e5': ['shoulders', 'triceps'], 'e6': ['back', 'biceps'], 'e7': ['biceps'],
    'e8': ['triceps'], 'e9': ['glutes', 'hamstrings'], 'e10': ['calves'], 'e11': ['abs'],
}


def esc(s):
    return html.escape(str(s), quote=True)


def muscles_for(exercise_ids):
    """Muscles of a day, in the order they first appear."""
    out = []
    for e in exercise_ids:
        for m in EXERCISE_MUSCLES[e]:
            if m not in out:
                out.append(m)
    return out


# ---- body diagram (viewBox 0 0 120 236, centred on x=60) -------------------
def _mirror(points):
    return [(120 - x, y) for x, y in points]


def _poly(points, cls):
    return f'<polygon class="{cls}" points="{" ".join(f"{x},{y}" for x, y in points)}"/>'


def _pair(points, cls):
    return _poly(points, cls) + _poly(_mirror(points), cls)


def _limb(x1, y1, x2, y2, w1, w2, cls):
    """Tapered limb, drawn on both sides."""
    def one(a1, a2):
        return (f'<path class="{cls}" d="M{a1 - w1 / 2} {y1} Q{a1 - w1 / 2 - 1} {(y1 + y2) / 2} {a2 - w2 / 2} {y2} '
                f'Q{a2} {y2 + w2 / 2.4} {a2 + w2 / 2} {y2} Q{a1 + w1 / 2 + 1} {(y1 + y2) / 2} {a1 + w1 / 2} {y1} '
                f'Q{a1} {y1 - w1 / 2.4} {a1 - w1 / 2} {y1}Z"/>')
    return one(x1, x2) + one(120 - x1, 120 - x2)


def _figure(side):
    """One view of the body. Base shapes use class b; muscles use m-<id>."""
    s = []
    # head, neck, torso, pelvis (base)
    s.append('<ellipse class="b" cx="60" cy="17" rx="10" ry="12.5"/>')
    s.append('<path class="b" d="M54 27 H66 L67 38 H53 Z"/>')
    s.append('<path class="b" d="M44 40 Q60 35 76 40 L82 50 L80 74 Q77 92 76 106 L44 106 Q43 92 40 74 L38 50 Z"/>')
    s.append('<path class="b" d="M44 104 H76 L79 120 Q70 130 60 131 Q50 130 41 120 Z"/>')
    # arms and legs (base)
    s.append(_limb(34, 58, 30, 94, 11, 9, 'b'))      # upper arm
    s.append(_limb(30, 97, 27, 130, 8.6, 6, 'b'))    # forearm
    s.append('<ellipse class="b" cx="26.5" cy="136" rx="4" ry="5.5"/><ellipse class="b" cx="93.5" cy="136" rx="4" ry="5.5"/>')
    s.append(_limb(50, 124, 49, 180, 19, 12, 'b'))   # thigh
    s.append(_limb(49, 184, 49, 222, 11.5, 7, 'b'))  # lower leg
    s.append('<ellipse class="b" cx="48" cy="227" rx="5" ry="3.2"/><ellipse class="b" cx="72" cy="227" rx="5" ry="3.2"/>')
    # muscles
    s.append('<ellipse class="m m-shoulders" cx="37" cy="50" rx="8" ry="9"/><ellipse class="m m-shoulders" cx="83" cy="50" rx="8" ry="9"/>')
    if side == 'front':
        s.append(_pair([(59, 45), (46, 44), (40, 52), (42, 63), (58, 67)], 'm m-chest'))
        for i, y in enumerate((69, 81, 93)):
            s.append(f'<rect class="m m-abs" x="51.5" y="{y}" width="7.5" height="10.5" rx="2.5"/>'
                     f'<rect class="m m-abs" x="61" y="{y}" width="7.5" height="10.5" rx="2.5"/>')
        s.append(_limb(34.5, 60, 31, 90, 8.5, 6.5, 'm m-biceps'))
        s.append(_limb(50.5, 128, 49, 174, 15, 9, 'm m-quads'))
        s.append(_limb(48.5, 190, 49, 214, 7, 4.5, 'm m-calves'))
    else:
        s.append(_pair([(60, 38), (52, 40), (45, 46), (60, 56)], 'm m-back'))                    # trapezius
        s.append(_pair([(59, 58), (44, 50), (41, 66), (47, 86), (59, 92)], 'm m-back'))         # lats
        s.append(_pair([(59, 92), (49, 88), (47, 103), (59, 104)], 'm m-lowerback'))
        s.append(_limb(34, 60, 30.5, 90, 8.5, 6.5, 'm m-triceps'))
        s.append('<ellipse class="m m-glutes" cx="51" cy="116" rx="9" ry="10"/><ellipse class="m m-glutes" cx="69" cy="116" rx="9" ry="10"/>')
        s.append(_limb(50, 132, 49, 176, 15, 9, 'm m-hamstrings'))
        s.append(_limb(49, 186, 49, 210, 10, 6, 'm m-calves'))
        s.append('<path class="line" d="M60 40 V104"/>')
    return ''.join(s)


def bodymap(muscles, label_front='أمام', label_back='خلف'):
    on = ' '.join(muscles)
    names = '، '.join(MUSCLE_NAMES[m][0] for m in muscles)
    return (f'<div class="bodymap" data-on="{esc(on)}" role="img" aria-label="مخطط الجسم: العضلات المستهدفة {esc(names)}">'
            f'<figure><svg viewBox="0 0 120 236" aria-hidden="true">{_figure("front")}</svg><figcaption>{label_front} <span class="en">FRONT</span></figcaption></figure>'
            f'<figure><svg viewBox="0 0 120 236" aria-hidden="true">{_figure("back")}</svg><figcaption>{label_back} <span class="en">BACK</span></figcaption></figure>'
            '</div>')


def muscle_chips(muscles):
    return '<div class="muscle-chips">' + ''.join(
        f'<span><i></i>{esc(MUSCLE_NAMES[m][0])} <b class="en">{esc(MUSCLE_NAMES[m][1])}</b></span>' for m in muscles) + '</div>'


# ---- pages -------------------------------------------------------------------
LOGO = '../book/identity/source-07-00.png'


def _foot(n, total, index_id='p2'):
    total_txt = '—' if total is None else total
    return (f'<footer class="footer"><a href="#{index_id}">الفهرس ↗</a><span class="en">{n} / {total_txt}</span>'
            '<span>مسودة · © 2026 Mdaar21</span></footer>')


def divider_page(n_days, days, page_id, page_no=None, total=None, dose='3 مجموعات لكل تمرين · التكرار والراحة في بطاقة كل تمرين'):
    """Program opener. days: list of (Arabic day name, English short, anchor id or None)."""
    boxes = ''.join(
        f'<a class="day-box" href="#{esc(a)}"><span class="en">DAY {i + 1:02}</span><b>{esc(ar)}</b><small class="en">{esc(en)}</small></a>'
        if a else
        f'<div class="day-box"><span class="en">DAY {i + 1:02}</span><b>{esc(ar)}</b><small class="en">{esc(en)}</small></div>'
        for i, (ar, en, a) in enumerate(days))
    return f'''<section class="page divider-page" id="{esc(page_id)}" aria-label="برنامج {n_days} أيام">
  <div class="orbits" aria-hidden="true"><i></i><i></i><i></i><b></b><b></b><b></b></div>
  <p class="tagline en">TRAIN · FUEL · TRANSFORM</p>
  <img class="divider-logo" src="{LOGO}" alt="شعار مدار">
  <p class="divider-brand"><span class="en">MDAAR21</span> بروتوكول التحول · نسخة البيت</p>
  <div class="big-number" aria-hidden="true">{n_days}</div>
  <h1><span class="sr-only">{n_days} </span>أيام تمرين</h1>
  <p class="divider-sub">برنامج أسبوعي في البيت، كل يوم يشتغل على عضلات محددة</p>
  <div class="day-boxes" style="--days:{len(days)}">{boxes}</div>
  <p class="divider-dose">{esc(dose)}</p>
  {_foot(page_no or '', total)}
</section>'''


def day_page(program_days, day_index, title_en, title_ar, exercise_ids, page_id, page_no=None, total=None, exercise_names=None):
    """Day opener with the body diagram. exercise_names: optional Arabic names listed under the chips."""
    muscles = muscles_for(exercise_ids)
    en_line = ' • '.join(MUSCLE_NAMES[m][1] for m in muscles)
    ex = ''
    if exercise_names:
        ex = '<ol class="day-exercises">' + ''.join(f'<li>{esc(x)}</li>' for x in exercise_names) + '</ol>'
    return f'''<section class="page day-page" id="{esc(page_id)}" aria-label="{esc(title_ar)}">
  <p class="tagline en">TRAIN · FUEL · TRANSFORM</p>
  <img class="divider-logo small" src="{LOGO}" alt="شعار مدار">
  <p class="day-kicker en">PROGRAM {program_days} · DAY {day_index + 1:02}</p>
  <p class="day-title-en en">{esc(title_en)}</p>
  <h1>{esc(title_ar)}</h1>
  <p class="day-muscles en">{esc(en_line)}</p>
  {bodymap(muscles)}
  {muscle_chips(muscles)}
  {ex}
  {_foot(page_no or '', total)}
</section>'''


# ---- previews (content from plan.md; Yasser's build is the source of truth) --
PROGRAMS = {
    3: [('الجسم كامل (أ)', 'FULL BODY A', ['e1', 'e4', 'e6', 'e11']),
        ('الجسم كامل (ب)', 'FULL BODY B', ['e2', 'e5', 'e9', 'e7']),
        ('الجسم كامل (ج)', 'FULL BODY C', ['e3', 'e6', 'e8', 'e10', 'e11'])],
    4: [('علوي (أ)', 'UPPER A', ['e4', 'e6', 'e5', 'e8']), ('سفلي (أ)', 'LOWER A', ['e1', 'e2', 'e10', 'e11']),
        ('علوي (ب)', 'UPPER B', ['e5', 'e6', 'e4', 'e7']), ('سفلي (ب)', 'LOWER B', ['e3', 'e9', 'e10', 'e11'])],
    5: [('دفع', 'PUSH', ['e4', 'e5', 'e8']), ('سحب', 'PULL', ['e6', 'e7', 'e11']), ('أرجل', 'LEGS', ['e1', 'e2', 'e3', 'e10']),
        ('علوي', 'UPPER', ['e4', 'e6', 'e5', 'e7', 'e8']), ('سفلي وبطن', 'LOWER + CORE', ['e9', 'e2', 'e10', 'e11'])],
}
DAY_TITLES = {'دفع': ('PUSH DAY', 'يوم الدفع'), 'سحب': ('PULL DAY', 'يوم السحب'), 'أرجل': ('LEG DAY', 'يوم الأرجل'),
              'علوي': ('UPPER DAY', 'يوم الجزء العلوي'), 'سفلي وبطن': ('LOWER + CORE', 'يوم السفلي والبطن')}
EX_AR = {'e1': 'السكوات', 'e2': 'هنج الورك', 'e3': 'اللانج للخلف', 'e4': 'ضغط الصدر', 'e5': 'الكتف', 'e6': 'الظهر',
         'e7': 'البايسبس', 'e8': 'الترايسبس', 'e9': 'الأرداف', 'e10': 'السمانة', 'e11': 'البطن'}

HEAD = '''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="../book/book.css">
<link rel="stylesheet" href="home.css">
</head>
<body>
<!-- معاينة مولّدة من pages.py. المحتوى من plan.md، والبناء النهائي في build.py. -->
'''


def write_previews():
    dividers = []
    for n, days in PROGRAMS.items():
        dividers.append(divider_page(n, [(ar, en, None) for ar, en, _ in days], f'program-{n}'))
    (HOME / 'divider.html').write_text(HEAD.format(title='صفحات افتتاح البرامج — نسخة البيت') + '\n'.join(dividers) + '\n</body>\n</html>\n', encoding='utf-8')
    pages = []
    for n, d in ((5, 0), (4, 1), (3, 0)):
        ar, en, ids = PROGRAMS[n][d]
        t_en, t_ar = DAY_TITLES.get(ar, (f'{en} DAY' if 'DAY' not in en else en, f'يوم {ar}'))
        if n != 5:
            t_en, t_ar = en, f'اليوم {["الأول", "الثاني", "الثالث", "الرابع"][d]}: {ar}'
        pages.append(day_page(n, d, t_en, t_ar, ids, f'day-{n}-{d + 1}', exercise_names=[EX_AR[e] for e in ids]))
    (HOME / 'day.html').write_text(HEAD.format(title='صفحات الأيام — نسخة البيت') + '\n'.join(pages) + '\n</body>\n</html>\n', encoding='utf-8')


if __name__ == '__main__':
    write_previews()
    print('wrote divider.html and day.html')
