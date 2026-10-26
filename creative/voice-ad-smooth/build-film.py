from pathlib import Path
import json,html
from character import actor

ROOT=Path(__file__).resolve().parent
edit=json.loads((ROOT/'reports/audio-edit.json').read_text())
duration=edit['editedSeconds']
def mapped(t):
    for s in edit['keptSegments']:
        if t <= s['sourceEnd']:
            return s['outputStart']+max(0,t-s['sourceStart'])
    return duration

# Speech drives the story. Raw anchors stay reviewable against the unchanged upload.
source_starts=[0,2.0,5.36,7.28,9.25,11.65,14.18,16.90,21.25,24.55,27.85,29.80,33.80,36.80,36.80]
starts=[round(mapped(t),5) for t in source_starts]
ends=starts[1:]+[duration]
beats=[{'id':f's{i}','sourceStart':s,'start':a,'end':b} for i,(s,a,b) in enumerate(zip(source_starts,starts,ends)) if i!=13]
(ROOT/'beats.json').write_text(json.dumps({'duration':duration,'beats':beats},indent=2)+'\n')
final=ROOT/'words-final.json'
if final.exists():
    words=json.loads(final.read_text())
else:
    # Draft view only. This is replaced by a reviewed multilingual transcript before export.
    raw=json.loads(Path('/workspace/mdaar-local/audio-ad-work/transcript-raw.json').read_text())
    words=[dict(text=w['text'],start=mapped(w['start']),end=mapped(w['end'])) for s in raw['segments'] for w in s['words']]
groups=[];current=[]
for i,w in enumerate(words):
    current.append(w)
    nxt=words[i+1] if i+1<len(words) else None
    punct=w['text'].endswith(('.','؟','!','…'))
    if len(current)>=4 or (punct and len(current)>=2 and w['end']-current[0]['start']>.70) or not nxt or nxt['start']-w['end']>.32:
        start=max(0,current[0]['start']-.015)
        end=min(nxt['start']-.015 if nxt else duration,current[-1]['end']+.11)
        groups.append({'start':start,'end':max(start+.10,end),'words':current});current=[]
(ROOT/'captions.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2)+'\n')

def section(i,title,body,kind='',extra=''):
    return f'<section id="s{i}" class="scene {kind}" data-beat="{starts[i]}" aria-label="{html.escape(title)}"><div class="back-orbit" data-layout-ignore></div><div class="grain" data-layout-ignore></div><div class="scene-content">{extra}<h2>{title}</h2>{body}</div></section>'
def stage(content,cls=''):
    return '<div class="stage '+cls+'">'+content+'</div>'
def cards():
    names=['جدول جديد','نصيحة ثانية','طريقة ثانية','أبدأ من وين؟']
    return ''.join(f'<div class="source-card src{i+1}"><span>{v}</span><i></i><i></i><i></i></div>' for i,v in enumerate(names))
gym='''<div class="prop training-icon"><svg class="line-svg" viewBox="0 0 300 300" aria-label="رسم رمزي لأداة تدريب وليس شرحاً للحركة"><path d="M40 110v80m25-95v110m170-110v110m25-95v80M65 150h170"/><path stroke="#d1ac65" d="M100 240h100"/></svg></div>'''
week='<div class="week-sheet"><h3>جدول التمرين</h3><div class="week-grid">'+''.join(f'<div class="'+('selected' if i in [0,1,3,4] else '')+'">'+v+'</div>' for i,v in enumerate(['علوي','سفلي','راحة','علوي','سفلي','راحة','راحة','✓']))+'</div></div><div class="check-mark">✓</div>'
scenes=[
 section(0,'نعرف <span class="gold">الحيرة.</span>',stage('<div class="hero-disc" data-layout-ignore></div><div class="shadow" data-layout-ignore></div>'+actor()+'<span class="label" style="right:0;top:60px">بالنادي؟</span>')),
 section(1,'مصادر… <span>كثيرة.</span>',stage(cards()+actor()),'paper'),
 section(2,'سؤال <span class="gold">واحد.</span>',stage(actor()+'<div class="speech">؟</div>')),
 section(3,'جدول؟ موجود.',stage(week),'goldground'),
 section(4,'وبعدين؟',stage(actor()+'<div class="question-pill qp1">كيف أطبّق؟</div><div class="question-pill qp2">وش آكل؟</div><div class="question-pill qp3">أبدأ من وين؟</div>')),
 section(5,'من الكلام… <span class="gold">للتطبيق.</span>',stage(actor()+gym+'<div class="food-prop"><img src="assets/meal.png" alt="طبق توضيحي للأكل"></div><div class="doubt-pulse">؟</div>','split-stage')),
 section(6,'المتابعة <span>الشخصية.</span>',stage(actor()+actor()+'<div class="follow-label">توجيه ومتابعة</div>','coach'),'paper'),
 section(7,'والتكلفة؟',stage(actor()+'<div class="receipt"><h3>المتابعة الشخصية</h3><div class="receipt-rule"></div><div class="bars"><i></i><i></i><i></i></div><p>هل تناسب ميزانيتك؟</p></div><div class="over-budget">فوق الميزانية؟</div>','receipt-stage'),'paper'),
 section(8,'بروتوكول <span class="gold">التحوّل.</span>',stage('<div class="halo" data-layout-ignore></div><div class="product-phone"><img src="assets/book-cover.svg" alt="غلاف بروتوكول التحول الأصلي"></div>'+actor()+'<div class="digital-tag">دليل رقمي من مدار</div>','book-stage'),extra='<span class="eyebrow gold">MDAAR21 / THE PROTOCOL</span>'),
 section(9,'برنامجك. <span class="gold">على أيامك.</span>',stage('<div class="program-covers"><div class="program-cover pc4"><img src="assets/program-four.webp" alt="غلاف برنامج 4 أيام الأصلي"><span class="program-tag">٤ أيام</span></div><div class="program-cover pc5"><img src="assets/program-five.webp" alt="غلاف برنامج 5 أيام الأصلي"><span class="program-tag">٥ أيام</span></div></div>')),
 section(10,'ورابط <span class="gold">للشرح.</span>',stage('<div class="product-phone"><img src="assets/book-guide.svg" alt="غلاف دليل مدار الأصلي"></div><div class="link-card">روابط شرح التمارين <span><svg viewBox="0 0 40 40" aria-hidden="true"><path d="M8 32 32 8M12 8h20v20" stroke="#121210" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg></span></div>')),
 section(11,'احسب <span class="gold">نقطة البداية.</span>',stage('<div class="screen-frame screen-calculator"><img src="assets/demo-calculator.png" alt="نتيجة الحاسبة الفعلية لمثال توضيحي"></div>')+'<p class="demo-note">مثال توضيحي · احتياجك تقديري ويختلف حسب بياناتك</p>'),
 section(12,'<span class="gold">٥٠٠</span> وصفة في الموقع.',stage('<div class="screen-frame screen-recipes"><img class="recipe-first" src="assets/demo-recipe-1.png" alt="وصفة الشوفان الفعلية من الموقع"><img class="recipe-scaled" src="assets/demo-recipe-15.png" alt="الوصفة نفسها بعد تعديل الحصة إلى 1.5" style="position:absolute;inset:0;opacity:0"></div><div class="recipe-count"><b>٥٠٠</b><span>وصفة</span></div><div class="serving-demo">غيّر حصتك<b>تتحدّث القيم.</b></div>')+'<p class="demo-note">القيم الغذائية تقديرية حسب المقادير والتحضير</p>'),
 section(13,'اختَر <span class="gold">اللي يناسبك.</span>',stage('<div class="program-covers"><div class="program-cover pc4"><img src="assets/program-four.webp" alt="برنامج 4 أيام"></div><div class="program-cover pc5"><img src="assets/demo-recipe-15.png" alt="وصفة بمقادير وحصص"></div></div>')+'<div class="summary-pills"><span>تمرينك</span><span>وصفاتك</span><span>أدواتك</span></div>'),
 section(14,'ابدأ <span class="gold">مدارك.</span>','<div class="final-stage"><img class="closing-logo" src="assets/closing-logo.png" alt="شعار مدار الأصلي"><div class="product-phone"><img src="assets/book-cover.svg" alt="غلاف بروتوكول التحول"></div>'+actor()+'</div><div class="cta">احصل على بروتوكول التحوّل</div><p class="url">mdaar21.zid.store</p>')
]
caption_html='<div class="caption-layer">'+''.join('<div class="caption" id="cap-'+str(i)+'"><div class="caption-inner"><div class="caption-text">'+' '.join('<span class="caption-word" id="cw-'+str(i)+'-'+str(j)+'">'+html.escape(w['text'])+'</span>' for j,w in enumerate(g['words']))+'</div></div></div>' for i,g in enumerate(groups))+'</div>'
header='<div class="brandbar"><div class="mark"><img src="assets/hero-logo.png" alt=""><b>مدار</b></div><span>MDAAR21</span></div><div class="footer"><span class="progress"><i></i></span></div>'
script='const BEATS='+json.dumps(beats)+';const CAPTIONS='+json.dumps(groups,ensure_ascii=False)+';const DURATION='+str(duration)+';\n'+(ROOT/'animate.js').read_text()
output='<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=1080,height=1920"><title>مدار — من الحيرة إلى خطة</title><script src="assets/gsap.min.js"></script><style>'+(ROOT/'style.css').read_text()+'</style></head><body><div id="root" data-composition-id="mdaar-voice" data-start="0" data-duration="'+str(duration)+'" data-width="1080" data-height="1920">'+''.join(v for i,v in enumerate(scenes) if i!=13)+header+caption_html+'<audio id="speech" src="assets/final-mix.wav" data-start="0" data-duration="'+str(duration)+'" data-track-index="3" data-volume="1"></audio></div><script>'+script+'</script></body></html>'
(ROOT/'index.html').write_text(output)
print(json.dumps({'seconds':duration,'scenes':len(beats),'captionGroups':len(groups),'finalTranscript':final.exists()}))
