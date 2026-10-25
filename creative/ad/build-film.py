from pathlib import Path
from shutil import copy2
import re,json

root=Path(__file__).resolve().parent
(root/'DESIGN.md').write_text('''# مدار — الشخصية تتحرّك
\n## Style Prompt
نفس الشخصية الكرتونية في مرجع المستخدم: رأس دائري ووجه فارغ بالكامل، شعر أسود قصير، قميص ذهبي بشريط أسود، بنطال أسود وحذاء عاجي، وحواف قصاصات بيضاء. الشخصية هي البطل في المشاهد الثمانية، بحركات مستقلة للرأس والذراعين والساقين وليست صورة ثابتة. المرجع الأخير يسمح بالرأس الكرتوني الخالي من الملامح؛ لا عيون أو أنف أو فم أو حواجب أو ملامح جانبية.
\n## Colors
#eee4d1 ورق، #121210 حبر، #d1ac65 ذهب، #f9f5e9 حواف، #a35437 طيني محدود. بشرة الشخصية #d9a171. شعار وغلاف مدار الأصليان محفوظان.
\n## Typography and layout
Lalezar للعرض. لوحة 1080×1920، تصدير 4K وHD، 30fps. عناوين كبيرة ومساحة واضحة للشخصية، مع هوامش آمنة 90px جانبيًا و210px أعلى وأسفل.
\n## Motion
20 ثانية بدل 22.4، دخول سريع وقفات قراءة قصيرة. قفز وثني ذراعين، حك الرأس، رفع باربل، الإشارة للأهداف والكتاب والشراء. الحركة بمفاصل SVG فعلية وحركة جسم كاملة. انتقالات دفع وكشف قصيرة مع التوقيت القصصي.
\n## Sound
مؤثرات فقط. لا موسيقى أو لحن أو هارموني أو إيقاع خلفي أو طبول أو أصوات بشرية. أصوات ورق واندفاعات ونقرات وارتطامات قصيرة، مأخوذة من مكتبة المؤثرات ومحررة للتزامن مع الأفعال، تتخللها فترات صمت.
\n## Avoid
لا إعادة استخدام score.mp3 أو الموسيقى السابقة. لا وجوه بملامح. لا تغيير الحقائق: 500 وصفة، 34 صفحة، وبرنامجا 4 و5 أيام. لا ضمان نتائج أو قيمة بيع. لا إعادة رسم الشعار أو الغلاف.
''')
(root/'SCRIPT.md').write_text('''# مدار — الشخصية والمعلومة
\n0–2: تبغى تتحوّل؟ الشخصية تقفز وتستعرض الذراعين.
2–4: ومحتار من وين تبدأ؟ تحك رأسها وتلتفت بحيرة.
4–7: برنامجا تدريب: 4 أو 5 أيام. الشخصية ترفع الباربل.
7–9.5: 500 وصفة بالسعرات والماكروز. تشير الشخصية للطبق والرقم.
9.5–11.5: خفض / ثبات / زيادة. تتفاعل مع الخيارات الثلاثة.
11.5–14: 34 صفحة وروابط شرح التمارين. تسحب الكتاب وتدل عليه.
14–16.8: بروتوكول التحوّل، تمرينك وأدواتك في مدار واحد.
16.8–20: مدار، ابدأ خطوتك. احصل على البروتوكول، mdaar21.zid.store.
\nالصوت مؤثرات فقط، دون موسيقى أو تعليق صوتي.
''')
(root/'STORYBOARD.md').write_text('''# Storyboard — 20s / 30fps
\nالشخصية الكرتونية يعاد بناؤها بأشكال متجهية مستوحاة مباشرة من مرجع المستخدم، برأس بلا ملامح وشعر أسود وقميص ذهبي وبنطال أسود وحواف بيضاء. مفاصل الذراعين والساعدين والرأس والساقين مستقلة؛ لا حاجة لتوليد لقطات بشرية.
\n| Scene | Time | Action |
|---|---|---|
| 1 | 0–2 | دخول وقفزة، هبوط مرن ثم ثني الذراعين |
| 2 | 2–4 | حك الرأس، ميلان للرأس والكتفين، علامات استفهام |
| 3 | 4–7 | حمل باربل وحركتا رفع وخفض مع قبضة محددة |
| 4 | 7–9.5 | الإشارة للطبق والرقم 500 |
| 5 | 9.5–11.5 | الإشارة لأعلى ثم الوسط ثم أسفل الخيارات |
| 6 | 11.5–14 | حركة سحب للكتاب مع فتح القصاصات |
| 7 | 14–16.8 | كشف الغلاف ومؤشر اليد نحوه |
| 8 | 16.8–20 | قفزة صغيرة والإشارة للشراء ثم تثبيت النهاية |
\nالمؤثرات لا تستعمل شبكة إيقاعية أو لحنًا: كل اندفاع أو نقرة مربوط بفعل بصري، مع صمت بين الأفعال. الملف الصوتي الوحيد sfx-only.mp3. الأغلفة والشعار والحقائق من مصادر مدار الأصلية. لا تعديل على مرجع المستخدم.
''')

def actor(light=False,bar=False):
 barbell='''<g class="barbell" transform="translate(0 0)" stroke="#f9f5e9" stroke-width="16" paint-order="stroke fill" stroke-linejoin="round"><rect x="48" y="228" width="424" height="14" rx="7" fill="#121210"/><rect x="28" y="182" width="52" height="106" rx="10" fill="#d1ac65"/><rect x="80" y="196" width="25" height="78" rx="5" fill="#121210"/><rect x="440" y="182" width="52" height="106" rx="10" fill="#d1ac65"/><rect x="415" y="196" width="25" height="78" rx="5" fill="#121210"/></g>''' if bar else ''
 return '''<div class="character '''+('light-kit' if light else '')+'''"><svg class="actor" viewBox="0 0 520 700" role="img" aria-label="شخصية مدار الكرتونية بوجه خالٍ تمامًا من الملامح"><g class="person" stroke="#f9f5e9" stroke-width="18" stroke-linecap="round" stroke-linejoin="round" paint-order="stroke fill">'''+barbell+'''
 <g class="leg-l" transform="rotate(0 228 427)"><path d="M204 409H258L241 606H190L202 460Z" fill="#121210"/><ellipse cx="215" cy="625" rx="49" ry="25" fill="#f3ebd8"/></g>
 <g class="leg-r" transform="rotate(0 292 427)"><path d="M262 409H316L329 606H278L264 460Z" fill="#121210"/><ellipse cx="305" cy="625" rx="49" ry="25" fill="#f3ebd8"/></g>
 <rect x="238" y="194" width="44" height="58" rx="9" fill="#d9a171"/>
 <g class="arm-l" transform="rotate(0 185 245)"><path d="M184 244Q174 240 168 253L129 338Q123 355 143 362Q161 365 166 348L204 260Q210 246 194 242Z" fill="#d9a171"/>
  <g class="fore-l" transform="rotate(0 145 345)"><path d="M128 344Q126 330 143 329Q159 328 161 344L167 433Q170 455 151 460Q130 461 128 441Z" fill="#d9a171"/><circle cx="150" cy="440" r="23" fill="#d9a171"/><circle cx="145" cy="345" r="18" stroke="none" fill="#d9a171"/><path class="pointer-l" d="M138 451L136 479Q136 491 148 491Q161 491 161 478L161 450Z" fill="#d9a171"/></g>
 </g>
 <g class="arm-r" transform="rotate(0 335 245)"><path d="M336 244Q346 240 352 253L391 338Q397 355 377 362Q359 365 354 348L316 260Q310 246 326 242Z" fill="#d9a171"/>
  <g class="fore-r" transform="rotate(0 375 345)"><path d="M392 344Q394 330 377 329Q361 328 359 344L353 433Q350 455 369 460Q390 461 392 441Z" fill="#d9a171"/><circle cx="370" cy="440" r="23" fill="#d9a171"/><circle cx="375" cy="345" r="18" stroke="none" fill="#d9a171"/><path class="pointer-r" d="M359 451L359 479Q359 491 371 491Q384 491 383 478L382 450Z" fill="#d9a171"/></g>
 </g>
 <path class="jersey" d="M186 225Q260 209 334 225L348 407Q260 426 172 407Z" fill="#d1ac65"/>
 <path d="M177 365H343L344 388H176Z" stroke="none" fill="#121210"/>
 <rect x="178" y="411" width="164" height="51" rx="25" fill="#121210"/>
 <g class="head" transform="rotate(0 260 145)"><path class="face" d="M195 145C190 104 216 72 260 72C306 72 328 100 325 145C326 183 296 216 260 216C224 216 194 185 195 145Z" fill="#d9a171"/><path class="hair" d="M195 145C190 104 216 72 260 72C306 72 328 100 325 145H215V160H195Z" fill="#121210" stroke="none"/></g>
 </g></svg></div>'''

(root/'character-rig.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"'+actor().split('<svg',1)[1].split('</svg>',1)[0]+'</svg>')
base=(root/'base-style.css').read_text()
overrides='''\n.character{position:relative;flex:none;display:flex;align-items:center;justify-content:center;width:520px;height:700px}.actor{display:block;width:100%;height:100%;overflow:visible;filter:drop-shadow(5px 8px 0 #12121022);transform-origin:50% 90%}.pointer-l,.pointer-r{opacity:0}.light-kit .jersey{fill:#f3ebd8}
.scene-content{gap:16px;padding-top:220px;padding-bottom:200px}
#s1 .word1{font-size:188px}#s1 .word2{font-size:202px}#s1 .character{width:680px;height:880px}#s1 .scene-content{gap:4px}#s1 .sub{font-size:42px}#s1 .disc,#s1 .halftone{top:760px}
#s2 .scene-content{gap:10px}#s2 .confusion{font-size:130px}#s2 .word-start{font-size:145px}#s2 .character{width:670px;height:850px}#s2 .q1{top:1070px}#s2 .q2{top:830px}
#s3 .metric-row{height:265px}#s3 .number{font-size:278px}#s3 .metric-copy{font-size:88px}#s3 .program-card{height:205px;width:335px}#s3 .program-card strong{font-size:78px}#s3 .program-card small{font-size:31px}#s3 .character{width:570px;height:720px}#s3 .week-dots i{width:15px;height:15px}#s3 .sub{font-size:40px}
.duo-stage{display:flex;align-items:center;justify-content:center;width:900px;height:650px;direction:ltr;position:relative}
#s4 .metric-row{height:310px}#s4 .number{font-size:310px}#s4 .metric-copy{font-size:116px}#s4 .character{width:390px;height:650px;z-index:2}#s4 .food-art{width:590px;height:485px;margin-left:-80px;object-fit:contain;flex:none;z-index:1}#s4 .ribbon{font-size:52px}
#s5 .character{width:380px;height:650px}#s5 .goal-list{width:500px;margin:0;gap:22px;flex:none}#s5 .goal{width:500px;height:148px;padding:10px 30px;border-width:6px}#s5 .goal strong{font-size:80px}#s5 .goal svg{width:70px;height:70px}#s5 h2{font-size:145px}
#s6 .guide-stage{width:900px;height:680px;direction:ltr;gap:18px}#s6 .guide-cover{width:420px;flex:none}#s6 .character{width:330px;height:600px}#s6 .sheet.one{width:430px;height:610px;left:72px;top:40px}#s6 .sheet.two{width:430px;height:610px;left:66px;top:28px}#s6 .metric-row{height:320px}#s6 .number{font-size:310px}
#s7 .duo-stage{height:900px;width:900px;gap:0}#s7 .book-wrap{width:560px;flex:none;z-index:2}#s7 .character{width:290px;height:540px;z-index:3;margin-left:15px;align-self:flex-end;margin-bottom:20px}#s7 h2{font-size:98px;margin-top:14px}
#s8 .closing-brand{height:420px;gap:30px;direction:ltr}#s8 .closing-brand .logo{width:165px;height:120px}#s8 .closing-book{width:180px}#s8 .character{width:300px;height:420px}#s8 .brand-name{font-size:180px}#s8 h2{font-size:98px}#s8 .scene-content{gap:16px}#s8 .cta{font-size:62px;min-height:125px}
'''
arrow=lambda path:f'<svg viewBox="0 0 100 100" aria-hidden="true"><path d="{path}"/></svg>'
goals='<div class="goal-list"><div class="goal cut"><strong>خفض</strong>'+arrow('M36 10H64V55H88L50 94 12 55H36Z')+'</div><div class="goal steady"><strong>ثبات</strong>'+arrow('M8 35H92V47H8ZM8 59H92V71H8Z')+'</div><div class="goal gain"><strong>زيادة</strong>'+arrow('M36 90H64V45H88L50 6 12 45H36Z')+'</div></div>'
programs='<div class="program-cards"><div class="program-card four"><strong>٤ أيام</strong><small>٣ أيام راحة</small></div><div class="program-card five"><strong>٥ أيام</strong><small>يومان راحة</small></div></div>'
decor='<div class="disc" data-layout-ignore></div><div class="halftone" data-layout-ignore></div>'
scenes=[
'<section id="s1" class="scene">'+decor+'<div class="scene-content"><div class="headline"><h1 class="word1 paper-title">تبغى</h1><h2 class="word2 paper-title"><span class="headline-paper torn" data-layout-ignore></span><span class="word2-ink">تتحوّل؟</span></h2></div>'+actor()+'<p class="sub">كل خطوة تصنع فارقًا.</p></div></section>',
'<section id="s2" class="scene">'+decor+'<span class="question-mark q1" data-layout-ignore>؟</span><span class="question-mark q2" data-layout-ignore>؟</span><div class="scene-content"><h2 class="confusion">ومحتار</h2><h2 class="word-start">من وين تبدأ؟</h2>'+actor(light=True)+'<p class="sub">خلّ البداية أوضح.</p></div></section>',
'<section id="s3" class="scene"><div class="halftone" data-layout-ignore></div><div class="scene-content"><div class="metric-row"><span class="number paper-title" dir="ltr">2</span><h2 class="metric-copy">برنامجا تدريب</h2></div>'+programs+actor(bar=True)+'<p class="sub">اختَر الأنسب لجدولك.</p></div></section>',
'<section id="s4" class="scene"><div class="wash" data-layout-ignore></div><div class="scene-content"><div class="metric-row"><span class="number paper-title" dir="ltr">500</span><h2 class="metric-copy">وصفة</h2></div><div class="ribbon ink torn">بالسعرات والماكروز</div><div class="duo-stage">'+actor()+'<img class="food-art" src="assets/meal.png" alt="قصاصة طبق وجبة توضيحية"></div><p class="sub">خيارات أكثر. يومك أوضح.</p></div></section>',
'<section id="s5" class="scene"><div class="wash" data-layout-ignore></div><div class="scene-content"><h2>على <span class="gold">هدفك.</span></h2><div class="duo-stage">'+actor()+goals+'</div><p class="sub">حدّد هدفك من الحاسبة.</p></div></section>',
'<section id="s6" class="scene"><div class="halftone" data-layout-ignore></div><div class="scene-content"><div class="metric-row"><span class="number paper-title" dir="ltr">34</span><h2 class="metric-copy">صفحة</h2></div><div class="guide-stage"><div class="sheet one" data-layout-ignore></div><div class="sheet two" data-layout-ignore></div><img class="guide-cover" src="assets/book-guide.svg" alt="الغلاف الأصلي للدليل الرقمي الحالي">'+actor()+'</div><div class="ribbon ink torn">روابط شرح التمارين</div><p class="sub">دليل رقمي، معك في كل خطوة.</p></div></section>',
'<section id="s7" class="scene">'+decor+'<div class="scene-content"><p class="eyebrow">TRAIN · FUEL · TRANSFORM</p><div class="duo-stage"><div class="book-wrap"><img src="assets/book-cover.svg" alt="غلاف بروتوكول التحول الأصلي"></div>'+actor()+'</div><h2>بروتوكول التحوّل</h2><p class="sub">تمرينك وأدواتك، في مدار واحد.</p></div></section>',
'<section id="s8" class="scene">'+decor+'<div class="scene-content"><div class="closing-brand"><img class="closing-book" src="assets/book-end.svg" alt="غلاف بروتوكول التحول"><img class="logo" src="assets/closing-logo.png" alt="شعار مدار الأصلي">'+actor()+'</div><p class="brand-name">مدار</p><h2>ابدأ خطوتك.</h2><div class="cta">احصل على البروتوكول<img src="assets/arrow.svg" alt=""></div><p class="url">mdaar21.zid.store</p><p class="closing-note">برنامجك · غذاؤك · تقدّمك</p></div></section>'
]
header='<div class="brand-bar"><div class="brand"><img src="assets/hero-logo.png" alt=""><span>مدار</span></div><span class="edition">MDAAR21</span></div><div class="footer"><span class="footer-label">YOUR NEXT CHAPTER</span><span class="progress"><i></i></span></div>'
script=(root/'animation-source.js').read_text()
html='<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=1080,height=1920"><title>مدار — الشخصية ترجع</title><script src="assets/gsap.min.js"></script><style>'+base+overrides+'</style></head><body><div id="root" data-composition-id="mdaar-character" data-start="0" data-duration="20" data-width="1080" data-height="1920">'+''.join(scenes)+header+'<audio id="effects" src="assets/sfx-only.mp3" data-start="0" data-duration="20" data-track-index="3" data-volume="1"></audio></div><script>'+script+'</script></body></html>'
assert 'score.mp3' not in html and 'strength.png' not in html and 'map.png' not in html
(root/'index.html').write_text(html)
print('Character film built: eight independently posed SVG characters, blank faces, effects-only track.')
