from pathlib import Path
import json,html
from character import actor

ROOT=Path(__file__).resolve().parent
DURATION=29.8
beats=[{'id':f's{i}','start':a,'end':b,'family':family} for i,(a,b,family) in enumerate([
    (0,2.08,'opening'),(2.08,6.50,'push'),(6.50,10.80,'anchor'),(10.80,14.35,'diagonal'),
    (14.35,17.05,'vertical'),(17.05,20.05,'anchor'),(20.05,25.50,'diagonal-reverse'),(25.50,DURATION,'dissolve')])]
(ROOT/'beats.json').write_text(json.dumps({'duration':DURATION,'beats':beats},indent=2)+'\n')
def book(cls=''):
    return '<div class="book-object '+cls+'"><img src="assets/book-cover.svg" alt="غلاف بروتوكول التحول الأصلي"></div>'
def scene(i,title,body,sub='',light=False,extra='',note=''):
    return f'<section class="scene {"light" if light else ""} {"closing" if i==7 else ""}" id="s{i}" aria-label="{html.escape(title)}"><div class="camera"><div class="scene-content">{extra}<h2>{title}</h2>{"<p class=subtitle>"+sub+"</p>" if sub else ""}{body}{"<p class=demo-note>"+note+"</p>" if note else ""}</div></div></section>'
scenes=[
scene(0,'هل أتمرّن <span class="gold">صح؟</span>','<div class="stage hook-stage"><div class="gym-floor" data-layout-ignore></div><div class="gym-rack" data-layout-ignore></div>'+actor()+'<div class="question-mark" data-layout-ignore>؟</div><div class="mini-source">جدولي <b>يناسبني؟</b></div></div>',sub='سؤال كل مبتدئ'),
scene(1,'كل واحد <span class="gold">يقول شي</span>','<div class="stage choice-stage">'+actor()+'<div class="source-list"><div class="source-option"><span class="index">١</span><div>تمرّن ٣ أيام<small>هل يناسب وقتك وهدفك؟</small></div></div><div class="source-option"><span class="index">٢</span><div>تمرّن ٦ أيام<small>وهل يناسب استشفاءك؟</small></div></div><div class="source-option"><span class="index">؟</span><div>وش تختار؟<small>السياق يغيّر الاختيار</small></div></div></div></div>',sub='مصادر كثيرة… وآراء مختلفة'),
scene(2,'خلّ مرجعك <span class="gold">واضح</span>','<div class="stage book-stage">'+book()+actor()+'<div class="book-caption">بروتوكول التحوّل<span>من مدار</span></div></div>',light=True,sub='ابدأ بخطة مرتّبة'),
scene(3,'بروتوكول <span class="gold">التحوّل</span>','<div class="stage bundle-stage">'+book()+'<div class="feature-menu"><div class="bundle-tag">دليل PDF + تطبيق مدار</div><div class="menu-row"><span class="num">١</span><div>برامج تدريب<small>٤ أيام أو ٥ أيام</small></div></div><div class="menu-row"><span class="num">٢</span><div>أدوات غذائية<small>الحاسبة ودفتر الأكل</small></div></div><div class="menu-row"><span class="num">٣</span><div>٥٠٠ وصفة<small>في تطبيق مدار</small></div></div></div></div>',light=True),
scene(4,'جدولك <span class="gold">على أيامك</span>','<div class="stage program-stage"><div class="program-card pc-four"><img src="assets/program-four.webp" alt="غلاف برنامج أربعة أيام الأصلي"><p class="program-label"><b>٤</b> أيام</p></div><div class="program-card pc-five"><img src="assets/program-five.webp" alt="غلاف برنامج خمسة أيام الأصلي"><p class="program-label"><b>٥</b> أيام</p></div><p class="link-note">روابط شرح التمارين داخل دليل PDF</p></div>',sub='اختر البرنامج المناسب لوقتك'),
scene(5,'احسب <span class="gold">احتياجك</span>','<div class="stage calculator-stage"><div class="screen-frame calculator-screen"><img src="assets/demo-calculator.png" alt="نتيجة فعلية من حاسبة مدار لمثال توضيحي"></div><div class="calc-corner">سعراتك والماكروز</div></div>',note='مثال توضيحي · احتياجك تقديري ويتغير حسب بياناتك'),
scene(6,'<span class="gold">٥٠٠</span> وصفة في التطبيق','<div class="stage recipe-stage"><div class="screen-frame recipe-screen"><img class="recipe-before" data-layout-allow-overflow src="assets/demo-recipe-1.png" alt="وصفة شوفان فعلية من مدار لحصة واحدة"><img class="recipe-after" data-layout-allow-overflow src="assets/demo-recipe-15.png" alt="الوصفة نفسها بعد تغيير الحصص إلى 1.5"></div><div class="portion-callout">غيّر حصتك<b><span class="portion-one">1</span><span class="portion-after">1.5</span></b></div></div>',sub='حصتك تتغيّر… والقيم تتحدّث',note='عرض توضيحي من التطبيق · القيم الغذائية تقديرية'),
scene(7,'ابدأ <span class="gold">مدارك</span>','<div class="close-stage">'+book()+actor()+'</div><div class="price-line">15.99 <span>ر.س</span></div><div class="purchase-cta">احصل على بروتوكول التحوّل</div><p class="store-url">mdaar21.zid.store</p>',extra='<img class="close-logo" src="assets/closing-logo.png" alt="شعار مدار الأصلي">')
]
groups=json.loads((ROOT/'captions.json').read_text())
captions='<div class="caption-layer">'+''.join(f'<div class="caption" id="cap-{i}"><div class="caption-inner"><div class="caption-text">'+ ' '.join(html.escape(w['text']) for w in g['words'])+'</div></div></div>' for i,g in enumerate(groups))+'</div>'
script='const BEATS='+json.dumps(beats)+';const CAPTIONS='+json.dumps(groups,ensure_ascii=False)+';const DURATION='+str(DURATION)+';\n'+(ROOT/'animate.js').read_text()
output='<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=1080,height=1920"><title>مدار — من الحيرة إلى الوضوح</title><script src="assets/gsap.min.js"></script><style>'+(ROOT/'style.css').read_text()+'</style></head><body><div id="root" data-composition-id="mdaar-premium" data-start="0" data-duration="'+str(DURATION)+'" data-width="1080" data-height="1920">'+''.join(scenes)+captions+'<div class="progress" data-layout-ignore><i></i></div><audio id="mix" src="assets/final-mix.wav" data-start="0" data-duration="'+str(DURATION)+'" data-track-index="3" data-volume="1"></audio></div><script>'+script+'</script></body></html>'
(ROOT/'index.html').write_text(output)
print(json.dumps({'duration':DURATION,'scenes':len(beats),'captionGroups':len(groups)},ensure_ascii=False))
