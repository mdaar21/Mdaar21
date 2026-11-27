#!/usr/bin/env python3
"""Build «بروتوكول التحول: نسخة البيت» (docs/book-home): index.html and plan.md.

Usage: python3 docs/book-home/build.py

Reads docs/book-home/videos.json (the audited YouTube links, one per exercise
version) and writes:
  docs/book-home/index.html   the book, built from the design template
  docs/book-home/plan.md      the table of contents shown to the owner

Exercise pictures are read from docs/book-home/figures/<exercise id>-<with|without>.svg
(drawn by Sara). The picture itself is the link to the video (exercise-hotspot,
like the first book). A missing picture shows an empty "exercise picture" slot.
No network, no third-party packages. Identity (colors, fonts, cover, frame) comes unchanged
from docs/book/book.css and docs/book/identity/, and the two-version card is
styled by docs/book-home/home.css (design) and content.css (content pages).
Wording must stay free of health or weight promises and before/after claims.
"""
import html
import json
from pathlib import Path

from pages import divider_page, day_page
HOME = Path(__file__).resolve().parent
VIDEOS = json.loads((HOME / 'videos.json').read_text(encoding='utf-8'))['videos']
VIDEO = {(v['exerciseId'], v['version']): v for v in VIDEOS}


def esc(s):
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- content
# dose = (sets, reps, rest seconds). Doses are suggestions and need review by
# a qualified trainer, like the first book. cue = one short form reminder.
EXERCISES = [
    dict(id='e1', ar='السكوات', en='Squat', muscle='الفخذ الأمامي والأرداف', dose=('3', '8–12', '60–90'),
         db=dict(short='كأس', ar='سكوات الكأس بدمبل', en='Goblet Squat', cue='امسك الدمبل عند صدرك وانزل ببطء وظهرك مستقيم.'),
         bw=dict(short='وزن الجسم', ar='سكوات بوزن الجسم', en='Bodyweight Squat', cue='ادفع الورك للخلف وانزل بتحكم، وركبتاك باتجاه أصابع قدميك.')),
    dict(id='e2', ar='الرفعة الرومانية', en='Romanian Deadlift', muscle='الفخذ الخلفي والأرداف', dose=('3', '8–12', '60–90'),
         db=dict(short='دمبلين', ar='رفعة رومانية بدمبلين', en='Dumbbell Romanian Deadlift', cue='الدمبلان قريبان من ساقيك وظهرك مستقيم وركبتاك مثنيتان قليلًا.'),
         bw=dict(short='ساق واحدة', ar='رفعة رومانية بساق واحدة', en='Single-Leg Romanian Deadlift', cue='اثبت على ساق واحدة وأمِل الجذع للأمام وارفع الساق الأخرى للخلف.',
                 easy='إذا صعب عليك التوازن، امسك جدارًا أو كرسيًا ثابتًا بيدك.')),
    dict(id='e3', ar='اللانج للخلف', en='Reverse Lunge', muscle='الفخذ الأمامي والأرداف', dose=('3', '8–10 لكل ساق', '60–90'),
         db=dict(short='دمبلين', ar='لانج للخلف بدمبلين', en='Dumbbell Reverse Lunge', cue='اخطُ للخلف وانزل بتحكم والجذع مستقيم.'),
         bw=dict(short='وزن الجسم', ar='لانج للخلف بوزن الجسم', en='Bodyweight Reverse Lunge', cue='اخطُ للخلف وانزل بتحكم ويداك على وركيك.')),
    dict(id='e4', ar='ضغط الصدر', en='Chest Press', muscle='الصدر والترايسبس', dose=('3', '8–12', '60–90'),
         db=dict(short='على الأرض', ar='ضغط دمبلين على الأرض', en='Dumbbell Floor Press', cue='انزل حتى تلمس ذراعاك الأرض، ومرفقاك قريبان من جسمك.'),
         bw=dict(short='وزن الجسم', ar='الضغط بوزن الجسم', en='Push-Up', cue='جسمك خط مستقيم من الرأس إلى الكعبين.',
                 easy='إذا كان التمرين صعبًا، ابدأ بالضغط من الركبتين أو بيديك على حافة طاولة ثابتة.')),
    dict(id='e5', ar='ضغط الكتف', en='Shoulder Press', muscle='الكتف والترايسبس', dose=('3', '6–10', '90'),
         db=dict(short='جالس', ar='ضغط الكتف بدمبلين', en='Dumbbell Shoulder Press', cue='اضغط الدمبلين فوق رأسك دون أن تقوّس ظهرك.'),
         bw=dict(short='بايك', ar='ضغط البايك', en='Pike Push-Up', cue='ارفع الورك إلى الأعلى وانزل برأسك بين يديك ثم ادفع.',
                 easy='إذا كان التمرين صعبًا، ضع يديك على كرسي ثابت وابدأ بتكرارات أقل.')),
    dict(id='e6', ar='سحب الظهر', en='Back Row', muscle='عضلات الظهر والبايسبس', dose=('3', '8–12', '60–90'),
         db=dict(short='بيد واحدة', ar='سحب دمبل بيد واحدة', en='One-Arm Dumbbell Row', cue='اسحب الدمبل نحو جانبك وجسمك ثابت وظهرك مستقيم.'),
         bw=dict(short='تحت الطاولة', ar='سحب تحت الطاولة', en='Table Inverted Row', cue='تأكد أن الطاولة ثقيلة وثابتة قبل أن تسحب صدرك نحو حافتها.')),
    dict(id='e7', ar='ثني البايسبس', en='Biceps Curl', muscle='البايسبس', dose=('3', '10–15', '60'),
         db=dict(short='دمبلين', ar='رفع الدمبلين للبايسبس', en='Dumbbell Biceps Curl', cue='ثبّت مرفقيك بجانبك وارفع دون تأرجح.'),
         bw=dict(short='حقيبة ظهر', ar='رفع حقيبة الظهر للبايسبس', en='Backpack Biceps Curl', cue='املأ الحقيبة بكتب ثقيلة وارفعها نحو صدرك بتحكم.')),
    dict(id='e8', ar='الترايسبس', en='Triceps', muscle='الترايسبس', dose=('3', '8–12', '60–90'),
         db=dict(short='فوق الرأس', ar='تمديد الترايسبس فوق الرأس', en='Dumbbell Overhead Triceps Extension', cue='ثبّت مرفقيك قرب رأسك وأنزِل الدمبل خلف رأسك بتحكم.'),
         bw=dict(short='ألماسة', ar='ضغط الألماسة', en='Diamond Push-Up', cue='يداك قريبتان تحت صدرك، وانزل بتحكم.',
                 easy='إذا كان التمرين صعبًا، ابدأ من الركبتين.')),
    dict(id='e9', ar='جسر الأرداف', en='Glute Bridge', muscle='الأرداف والفخذ الخلفي', dose=('3', '10–15', '60'),
         db=dict(short='دمبل', ar='جسر الأرداف بدمبل', en='Dumbbell Glute Bridge', cue='ضع الدمبل على وركك وارفعه حتى يصير جسمك خطًا مستقيمًا من الكتف إلى الركبة.'),
         bw=dict(short='وزن الجسم', ar='جسر الأرداف بوزن الجسم', en='Bodyweight Glute Bridge', cue='ارفع الورك واضغط الأرداف في الأعلى، وانزل ببطء.')),
    dict(id='e10', ar='رفع السمانة', en='Calf Raise', muscle='عضلات السمانة', dose=('3', '12–20', '45–60'),
         db=dict(short='واقفًا', ar='رفع الكعبين واقفًا بدمبلين', en='Standing Dumbbell Calf Raise', cue='ارفع كعبيك إلى أعلى ما تستطيع وانزل ببطء.'),
         bw=dict(short='ساق واحدة', ar='رفع الكعب بساق واحدة', en='Single-Leg Calf Raise', cue='اثبت على ساق واحدة.',
                 easy='امسك جدارًا بيدك للتوازن.')),
    dict(id='e11', ar='البطن', en='Core', muscle='عضلات البطن والجذع', dose=('3', '8–12 لكل جهة', '45–60'),
         db=dict(short='التفاف روسي', ar='التفاف روسي بدمبل', en='Dumbbell Russian Twist', cue='أدر الجذع من جهة إلى أخرى والدمبل قريب منك وظهرك مستقيم.'),
         bw=dict(short='حشرة ميتة', ar='الحشرة الميتة', en='Dead Bug', cue='ظهرك ملتصق بالأرض، ومدّ ذراعًا وساقًا من الجهتين المتعاكستين ببطء.')),
]
BY_ID = {e['id']: e for e in EXERCISES}

# (program days, label of each day, exercise ids)
PROGRAMS = {
    3: [('الجسم الكامل (أ)', ['e1', 'e4', 'e6', 'e11']),
        ('الجسم الكامل (ب)', ['e2', 'e5', 'e9', 'e7']),
        ('الجسم الكامل (ج)', ['e3', 'e6', 'e8', 'e10', 'e11'])],
    4: [('علوي (أ)', ['e4', 'e6', 'e5', 'e8']),
        ('سفلي (أ)', ['e1', 'e2', 'e10', 'e11']),
        ('علوي (ب)', ['e5', 'e6', 'e4', 'e7']),
        ('سفلي (ب)', ['e3', 'e9', 'e10', 'e11'])],
    5: [('دفع', ['e4', 'e5', 'e8']),
        ('سحب', ['e6', 'e7', 'e11']),
        ('أرجل', ['e1', 'e2', 'e3', 'e10']),
        ('علوي', ['e4', 'e6', 'e5', 'e7', 'e8']),
        ('سفلي وبطن', ['e9', 'e2', 'e10', 'e11'])],
}
PROGRAM_NOTES = {
    3: 'لمن وقته ضيق أو يبدأ لأول مرة.',
    4: 'يوازن بين التمرين والراحة.',
    5: 'لمن اعتاد التمرين.',
}
ORDINALS = ['الأول', 'الثاني', 'الثالث', 'الرابع', 'الخامس']
CARDS_PER_PAGE = 4
DAY_EN = {'الجسم الكامل (أ)': 'FULL BODY A', 'الجسم الكامل (ب)': 'FULL BODY B', 'الجسم الكامل (ج)': 'FULL BODY C',
          'علوي (أ)': 'UPPER A', 'سفلي (أ)': 'LOWER A', 'علوي (ب)': 'UPPER B', 'سفلي (ب)': 'LOWER B',
          'دفع': 'PUSH', 'سحب': 'PULL', 'أرجل': 'LEGS', 'علوي': 'UPPER', 'سفلي وبطن': 'LOWER + CORE'}
DAY_TITLE = {'دفع': ('PUSH DAY', 'يوم الدفع'), 'سحب': ('PULL DAY', 'يوم السحب'), 'أرجل': ('LEG DAY', 'يوم الأرجل'),
             'علوي': ('UPPER DAY', 'يوم الجزء العلوي'), 'سفلي وبطن': ('LOWER + CORE', 'يوم السفلي والبطن')}
MUSCLE_TITLE = {'e1': 'الفخذ الأمامي والأرداف', 'e2': 'الفخذ الخلفي والأرداف', 'e3': 'الفخذ الأمامي والأرداف', 'e4': 'الصدر', 'e5': 'الكتف', 'e6': 'الظهر', 'e7': 'البايسبس', 'e8': 'الترايسبس', 'e9': 'الأرداف', 'e10': 'السمانة', 'e11': 'البطن'}
SITE = 'https://mdaar21.github.io/Mdaar21/'
LABELS = {'with-dumbbell': ('بالدمبل', 'dumbbell', 'i-dumbbell'), 'no-dumbbell': ('بدون دمبل', 'no-dumbbell', 'i-body')}


# ---------------------------------------------------------------- pages
def page_specs():
    specs = [('cover',), ('picker',), ('guide',)]
    for n, days in PROGRAMS.items():
        specs.append(('opener', n))
        for d, (label, ids) in enumerate(days):
            pages = -(-len(ids) // CARDS_PER_PAGE)
            per = -(-len(ids) // pages)
            chunks = [ids[i:i + per] for i in range(0, len(ids), per)]
            specs.append(('dayhead', n, d))
            for c, chunk in enumerate(chunks):
                specs.append(('day', n, d, label, chunk, c, len(chunks)))
    specs += [('index',), ('log',), ('site',)]
    return specs


def head(category):
    return (f'<header><span class="brand"><img src="../book/identity/source-07-00.png" alt="شعار مدار الأصلي"> مدار</span>'
            f'<span>{esc(category)}</span></header>')


def foot(n, total, index_id):
    return (f'<footer class="footer"><a href="#{index_id}">الفهرس ↗</a><span class="en">{n} / {total}</span>'
            f'<span>مسودة · © 2026 Mdaar21</span></footer>')


def figure(ex, which, v):
    """The exercise picture, which is also the link to the video (like the first book)."""
    ver = 'with' if which == 'db' else 'without'
    info = ex[which]
    name = f'{ex["ar"]}، {info["short"]}'
    link = (f'<a class="exercise-hotspot" href="{esc(v["url"])}" aria-label="افتح مقطع شرح {esc(name)}" '
            f'style="left:0;top:0;width:100%;height:100%"></a>')
    if (HOME / 'figures' / f'{ex["id"]}-{ver}.svg').exists():
        img = f'<img src="figures/{ex["id"]}-{ver}.svg" alt="رسم يوضح تمرين {esc(name)}">'
    else:
        img = '<span class="fig-empty">صورة التمرين</span>'
    return f'<div class="exercise-image">{img}{link}</div>'


def version_card(ex, which):
    ver = 'with-dumbbell' if which == 'db' else 'no-dumbbell'
    tag, cls, icon = LABELS[ver]
    info, v = ex[which], VIDEO[(ex['id'], ver)]
    sets, reps, rest = ex['dose']
    easy = f' <b class="easy">للمبتدئين:</b> {esc(info["easy"])}' if info.get('easy') else ''
    return f'''<div class="version {cls}">
          <span class="version-tag"><svg><use href="#{icon}"/></svg>{tag}</span>
          <h3>{esc(info['short'])}</h3>
          <div class="figure-slot">{figure(ex, which, v)}</div>
          <div class="dose-row"><span><bdi dir="ltr">{sets}</bdi> × <bdi dir="ltr">{reps}</bdi></span><span>راحة <bdi dir="ltr">{rest}</bdi> ث</span></div>
          <p class="cue">{esc(info['cue'])}{easy}</p>
        </div>'''


def exercise_card(num, ex):
    return f'''<article class="ex">
      <div class="ex-head"><h2><span class="num">{num}</span>{esc(MUSCLE_TITLE[ex['id']])}</h2><span class="muscle">{esc(ex['ar'])}</span></div>
      <div class="ex-versions">
        {version_card(ex, 'db')}
        {version_card(ex, 'bw')}
      </div>
    </article>'''


SVG_SYMBOLS = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <symbol id="i-dumbbell" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M6.5 7v10M17.5 7v10M3.5 9.5v5M20.5 9.5v5M6.5 12h11"/></g></symbol>
  <symbol id="i-body" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="4.5" r="2"/><path d="M12 7v7M7 10.5l5-2 5 2M9 21l3-7 3 7"/></g></symbol>
  <symbol id="i-home" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m3 11 9-7 9 7M5.5 9.5V20h13V9.5M10 20v-5h4v5"/></g></symbol>
</svg>'''

LEGEND = '''<div class="equip-legend">
    <span><span class="version-tag" style="background:#d9ba7b;color:#0d0e0e"><svg><use href="#i-dumbbell"/></svg>بالدمبل</span> إذا عندك دمبل في البيت</span>
    <span><span class="version-tag" style="border:1px solid #d9ba7b;color:#f0dba7"><svg><use href="#i-body"/></svg>بدون دمبل</span> بوزن جسمك أو بأدوات البيت</span>
  </div>'''


def day_muscles(ids_):
    out = []
    for i in ids_:
        t = MUSCLE_TITLE[i]
        if t not in out:
            out.append(t)
    return '، '.join(out)


def render(spec, n, total, ids):
    index_id = ids['index']
    kind = spec[0]
    if kind == 'cover':
        return f'''<section class="page source-cover home-cover" id="p{n}" aria-label="الغلاف: بروتوكول التحول، نسخة البيت">
  <img class="original-cover" src="../book/identity/cover-01.svg" alt="غلاف مدار الأصلي: بروتوكول التحول. هوية سوداء وذهبية وشعار مدار الأصلي.">
  <div class="edition" aria-hidden="true">
    <b><svg><use href="#i-home"/></svg>نسخة البيت</b>
    <small>برامج 3 و4 و5 أيام · كل تمرين بالدمبل أو بدونه</small>
  </div>
  <div class="sr-only"><h1>بروتوكول التحول: نسخة البيت</h1><p>برامج 3 و4 و5 أيام. كل تمرين له نسختان: بالدمبل وبدون دمبل.</p></div>
  <nav class="cover-navigation" aria-label="تنقل الغلاف"><a href="#{index_id}">الفهرس ↗</a><a href="#p2">ابدأ ←</a></nav>
</section>'''
    if kind == 'opener':
        prog = spec[1]
        days = [(label, DAY_EN[label], ids[('day', prog, d)]) for d, (label, _) in enumerate(PROGRAMS[prog])]
        html_ = divider_page(prog, days, f'p{n}', n, total)
        return html_.replace('href="#p2"', f'href="#{index_id}"')
    if kind == 'dayhead':
        _, prog, d = spec
        label, ex_ids = PROGRAMS[prog][d]
        if prog == 5 and label in DAY_TITLE:
            t_en, t_ar = DAY_TITLE[label]
        else:
            t_en, t_ar = DAY_EN[label], f'اليوم {ORDINALS[d]}: {label}'
        html_ = day_page(prog, d, t_en, t_ar, ex_ids, f'p{n}', n, total, exercise_names=[BY_ID[e]['ar'] for e in ex_ids])
        return html_.replace('href="#p2"', f'href="#{index_id}"')
    if kind == 'site':
        return f'''<section class="page" id="p{n}" aria-label="صفحة {n}: موقع مدار">
  <span class="draft-flag">مسودة</span>
  {head('موقع مدار')}
  <p class="eyebrow">MDAAR21 · WEBSITE</p>
  <h1>موقع مدار: النادي أو البيت</h1>
  <p class="intro">في موقع مدار قسم التمارين فيه خياران. اختر المكان الذي تتمرن فيه، ولكل خيار تمارينه.</p>
  <div class="program-picker">
    <a class="card" href="{SITE}"><div class="stat">النادي</div><h2>تمارين النادي</h2><p>تمارين بأجهزة النادي والأوزان الحرة.</p></a>
    <a class="card" href="{SITE}"><div class="stat">البيت</div><h2>تمارين البيت</h2><p>نفس تمارين هذا الكتاب: نسختان لكل تمرين، بدمبل وبدون.</p></a>
  </div>
  <p class="small"><a href="{SITE}">{SITE} ↗</a></p>
  {foot(n, total, index_id)}
</section>'''
    if kind == 'picker':
        cards = ''.join(
            f'<a class="card" href="#{ids[("prog", p)]}"><div class="stat">{p}</div><h2>أيام بالأسبوع</h2><p>{PROGRAM_NOTES[p]}</p></a>'
            for p in PROGRAMS)
        return f'''<section class="page" id="p{n}" aria-label="صفحة {n}: اختر برنامجك">
  <span class="draft-flag">مسودة أولى</span>
  {head('نسخة البيت')}
  <p class="eyebrow">MDAAR21 · HOME EDITION</p>
  <h1>اختر برنامجك</h1>
  <p class="intro">تمرّن في البيت بالدمبل أو بدونه. كل تمرين في الكتاب له نسختان، واختر التي تناسب أدواتك.</p>
  <div class="program-picker">{cards}</div>
  {LEGEND}
  <aside class="callout">ابدأ بشيء تقدر تتحكم فيه، وأوقف التمرين إذا حسيت بألم حاد أو دوخة. الكتاب للتوعية العامة للبالغين، ولا يقدّم تشخيصًا ولا وعدًا بنتيجة.</aside>
  {foot(n, total, index_id)}
</section>'''
    if kind == 'guide':
        return f'''<section class="page" id="p{n}" aria-label="صفحة {n}: كيف تستخدم الكتاب">
  <span class="draft-flag">مسودة أولى</span>
  {head('نسخة البيت')}
  <p class="eyebrow">MDAAR21 · HOW TO USE</p>
  <h1>كيف تستخدم الكتاب</h1>
  <div class="card"><h2>بطاقة التمرين</h2><p>لكل تمرين نسختان جنبًا إلى جنب: واحدة بالدمبل وواحدة بدون دمبل. اختر واحدة منهما وكمّل عليها طوال البرنامج، وبدّل عند تغيّر أدواتك.</p></div>
  <div class="card"><h2>كيف تقرأ الجرعة</h2><p><bdi dir="ltr">3</bdi> × <bdi dir="ltr">8–12</bdi> تعني 3 مجموعات، وكل مجموعة من 8 إلى 12 تكرارًا. «راحة <bdi dir="ltr">60–90</bdi> ث» (ث = ثانية) تعني أن ترتاح من دقيقة إلى دقيقة ونصف قبل المجموعة التالية. هذه جرعات مقترحة وتحتاج مراجعة مدرب مؤهل.</p></div>
  <div class="card"><h2>مقاطع الشرح</h2><p>اضغط صورة التمرين لفتح مقطع الشرح على يوتيوب. المقاطع من يوتيوب، وأصحابها جهات غير مدار. قد يتغير المقطع أو يُحذف، فإذا لم يعمل الرابط فأخبرنا لنستبدله.</p></div>
  <div class="card"><h2>قبل ما تبدأ</h2><p>سخّن جسمك بحركات خفيفة لبضع دقائق قبل أول مجموعة. اختر وزنًا تقدر تتحكم فيه، وتأكد أن المكان حولك واسع، وأن الطاولة أو الكرسي ثابت إذا استخدمتهما.</p></div>
  <aside class="callout warning">أوقف التمرين فورًا إذا شعرت بألم حاد أو دوخة أو ضيق نفس. إذا كانت عندك حالة صحية أو إصابة، استشر مختصًا قبل البدء. الكتاب لا يقدّم تشخيصًا ولا وعدًا بنتيجة.</aside>
  {foot(n, total, index_id)}
</section>'''
    if kind == 'day':
        _, prog, d, label, chunk, c, nchunks = spec
        first = c == 0
        num0 = c * -(-len(PROGRAMS[prog][d][1]) // nchunks)
        cards = '\n    '.join(exercise_card(num0 + i + 1, BY_ID[eid]) for i, eid in enumerate(chunk))
        title = f'اليوم {ORDINALS[d]} · {label}'
        suffix = '' if nchunks == 1 else f' — الجزء {c + 1} من {nchunks}'
        caption = ('<p class="exercise-caption">لكل تمرين نسختان. اختر واحدة وكمّل عليها. اضغط صورة التمرين لفتح المقطع.</p>'
                   if first else '<p class="exercise-caption">تكملة تمارين اليوم.</p>')
        return f'''<section class="page workout" id="p{n}" aria-label="صفحة {n}: برنامج {prog} أيام، {esc(title)}">
  <span class="draft-flag">مسودة أولى</span>
  {head(f'برنامج {prog} أيام')}
  <p class="eyebrow">PROGRAM {prog} · DAY {d + 1}</p>
  <h1>{esc(title)}{suffix}</h1>
  {caption}
  <div class="ex-list">
    {cards}
  </div>
  {foot(n, total, index_id)}
</section>'''
    if kind == 'index':
        rows = ''.join(
            f'<tr><td>{i + 1}</td><td>{esc(e["ar"])}</td>'
            f'<td><a href="{esc(VIDEO[(e["id"], "with-dumbbell")]["url"])}">{esc(e["db"]["short"])} ↗</a></td>'
            f'<td><a href="{esc(VIDEO[(e["id"], "no-dumbbell")]["url"])}">{esc(e["bw"]["short"])} ↗</a></td></tr>'
            for i, e in enumerate(EXERCISES))
        return f'''<section class="page" id="p{n}" aria-label="صفحة {n}: فهرس التمارين والمقاطع">
  <span class="draft-flag">مسودة أولى</span>
  {head('فهرس')}
  <p class="eyebrow">MDAAR21 · INDEX</p>
  <h1>فهرس التمارين والمقاطع</h1>
  <p class="small">كل رابط يفتح مقطع الشرح على يوتيوب. اختر النسخة التي تناسب أدواتك.</p>
  <table class="log-table index-table"><thead><tr><th>#</th><th>التمرين</th><th>بالدمبل</th><th>بدون دمبل</th></tr></thead><tbody>{rows}</tbody></table>
  <p class="small muted">برامج: <a href="#{ids[('prog', 3)]}">3 أيام</a> · <a href="#{ids[('prog', 4)]}">4 أيام</a> · <a href="#{ids[('prog', 5)]}">5 أيام</a></p>
  {foot(n, total, index_id)}
</section>'''
    if kind == 'log':
        rows = ''.join(f'<tr><td>{esc(e["ar"])}</td><td></td><td></td><td></td><td></td></tr>' for e in EXERCISES)
        return f'''<section class="page logs" id="p{n}" aria-label="صفحة {n}: سجل المتابعة">
  <span class="draft-flag">مسودة أولى</span>
  {head('سجل')}
  <p class="eyebrow">MDAAR21 · LOG</p>
  <h1>سجل المتابعة</h1>
  <p class="small">اكتب لكل تمرين الوزن أو التكرارات التي أنجزتها كل أسبوع. السجل لمتابعتك أنت، وما يقيس نتيجة.</p>
  <table class="log-table"><thead><tr><th>التمرين</th><th>الأسبوع 1</th><th>الأسبوع 2</th><th>الأسبوع 3</th><th>الأسبوع 4</th></tr></thead><tbody>{rows}</tbody></table>
  {foot(n, total, index_id)}
</section>'''
    raise ValueError(kind)


def build_html():
    specs = page_specs()
    total = len(specs)
    ids = {}
    for i, spec in enumerate(specs, 1):
        if spec[0] == 'index':
            ids['index'] = f'p{i}'
        if spec[0] == 'opener':
            ids[('prog', spec[1])] = f'p{i}'
        if spec[0] == 'dayhead':
            ids[('day', spec[1], spec[2])] = f'p{i}'
    body = '\n\n'.join(render(spec, i, total, ids) for i, spec in enumerate(specs, 1))
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>بروتوكول التحول: نسخة البيت — مسودة أولى</title>
<link rel="stylesheet" href="../book/book.css">
<link rel="stylesheet" href="home.css">
<link rel="stylesheet" href="content.css">
</head>
<body>
<!-- Generated by docs/book-home/build.py. Do not edit by hand; change the script or videos.json. -->
{SVG_SYMBOLS}

{body}
</body>
</html>
'''


def build_plan():
    dur_note = 'غير مؤكدة'
    L = ['# بروتوكول التحول: نسخة البيت: جدول المحتوى (المسودة الأولى)', '']
    L.append('هذا جدول المحتوى لكتاب «نسخة البيت» للرجال حسب القرار d29. ما فيه وعود صحية ولا وعود بنزول وزن ولا صور قبل وبعد. '
             'الجرعات (المجموعات والتكرار والراحة) مقترحة وتحتاج مراجعة مدرب مؤهل قبل الاعتماد، مثل الكتاب الأول. '
             'الملف يتولّد من `docs/book-home/build.py` ومن `videos.json`.')
    L.append('')
    L.append('## الخلاصة')
    L.append('')
    L.append('- 11 تمرينًا، لكل تمرين نسختان: بدمبل وبدون دمبل، يعني 22 مقطع يوتيوب.')
    L.append('- 3 برامج: 3 أيام (جسم كامل)، و4 أيام (علوي وسفلي)، و5 أيام (دفع وسحب وأرجل وعلوي وسفلي).')
    L.append('- كل رابط يفتح وعام وعنوانه يطابق التمرين، وشفت ثلاثة إطارات من كل مقطع للتأكد من التمرين ومن عدم وجود امرأة.')
    short = sum(1 for v in VIDEOS if v['format'] == 'short')
    L.append(f'- {short} مقطع من نوع Shorts (غالبًا تحت دقيقة) و{22 - short} مقطع عادي من مكتبات تمارين. **المدة غير مؤكدة لكل المقاطع** (يوتيوب يمنع قراءتها من السيرفر)، '
             'وكتبت «غير مؤكدة» بدل رقم من عندي.')
    L.append('- **ما تم فحصه:** الموسيقى والصوت، ولا أقدر أشوف المقطع كامل. لذلك شرط «بدون موسيقى» والمدة تحتاج سماعًا ومعاينة سريعة منك أو من جهازك (سكربت `audit.py` في مهارة book-video-audit يقرأ المدة على جهازك).')
    L.append('')
    L.append('## التمارين ونسختاها')
    L.append('')
    L.append('| # | التمرين | العضلات | نسخة بالدمبل | نسخة بدون دمبل | الجرعة المقترحة |')
    L.append('|---|---|---|---|---|---|')
    for i, e in enumerate(EXERCISES, 1):
        s, r, rest = e['dose']
        L.append(f'| {i} | {e["ar"]} | {e["muscle"]} | [{e["db"]["short"]}]({VIDEO[(e["id"], "with-dumbbell")]["url"]}) '
                 f'| [{e["bw"]["short"]}]({VIDEO[(e["id"], "no-dumbbell")]["url"]}) | {s} مجموعات × {r} تكرار، راحة {rest} ثانية |')
    L.append('')
    for n, days in PROGRAMS.items():
        L.append(f'## برنامج {n} أيام')
        L.append('')
        for d, (label, ids_) in enumerate(days):
            L.append(f'**اليوم {ORDINALS[d]}: {label}**: ' + '، '.join(BY_ID[i]['ar'] for i in ids_))
            L.append('')
    L.append('## تفاصيل فحص المقاطع')
    L.append('')
    L.append('طريقة الفحص: وجود الفيديو وأنه عام (oEmbed)، وعنوانه، وثلاثة إطارات معاينة. الموسيقى والصوت والمدة ما انفحصت.')
    L.append('')
    L.append('| التمرين | النسخة | القناة | العنوان في يوتيوب | النوع | المدة | وش تظهر الإطارات الثلاثة |')
    L.append('|---|---|---|---|---|---|---|')
    for e in EXERCISES:
        for ver in ('with-dumbbell', 'no-dumbbell'):
            v = VIDEO[(e['id'], ver)]
            kind = 'Shorts' if v['format'] == 'short' else 'عادي'
            L.append(f'| {e["ar"]} | {"بدمبل" if ver == "with-dumbbell" else "بدون دمبل"} | {v["channel"]} | {v["title"]} | {kind} | {dur_note} | {v["checks"]["three_frames"]} |')
    L.append('')
    L.append('## ملاحظات')
    L.append('')
    L.append('- مكان صورة التمرين في كل نسخة: صورة سارة الأصلية (docs/book-home/figures/)، والصورة نفسها هي الرابط للمقطع (اضغطها في الكتاب). لين تنرفع الصور يظهر مكانها «صورة التمرين».')
    L.append('- التمارين بدون دمبل الأصعب على المبتدئ (ضغط البايك وضغط الألماسة والرفعة الرومانية بساق واحدة والسمانة بساق واحدة) لها سطر «طريقة أسهل للبداية».')
    L.append('- سحب الظهر تحت الطاولة ما لقيت له مقطع Shorts فيه رجل فقط، فبقي المقطع القديم؛ وكذلك جسر الأرداف بوزن الجسم.')
    L.append('')
    return '\n'.join(L)


def main():
    (HOME / 'index.html').write_text(build_html(), encoding='utf-8')
    (HOME / 'plan.md').write_text(build_plan(), encoding='utf-8')
    print(f'{len(page_specs())} pages, {len(VIDEOS)} videos, {len(list((HOME / "figures").glob("*.svg"))) if (HOME / "figures").exists() else 0} figures')


if __name__ == '__main__':
    main()
