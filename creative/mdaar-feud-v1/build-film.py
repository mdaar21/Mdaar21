from pathlib import Path
import json,html
R=Path(__file__).resolve().parent
spec=[('opening',0,3.1,'wide0'),('one',3.1,4.6,'c1'),('board1',4.6,6.4,'wide1'),('host1',6.4,8,'host'),('two',8,9.7,'c2'),('board2',9.7,11.5,'wide2'),('host2',11.5,13,'host'),('ask',13,14.95,'host'),('three',14.95,16.08,'c3'),('silence',16.08,16.65,'host'),('winner',16.65,17.15,'win'),('celebrate',17.15,19,'host'),('product',19,22.2,'product'),('program',22.2,23.75,'program'),('calculator',23.75,25.45,'calculator'),('recipe',25.45,27,'recipe'),('closing',27,30,'closing')]
beats=[{'id':n,'start':a,'end':b,'kind':k} for n,a,b,k in spec]
(R/'beats.json').write_text(json.dumps({'duration':30,'beats':beats},indent=2)+'\n')
def book():return '<div class="book"><div class="paper-edge"></div><img src="assets/book-cover.svg" alt="غلاف بروتوكول التحول الأصلي"></div>'
def board(count):
 title='<h1>مدار فيود</h1><p class="board-question">وين تدور على جدول تمارين؟</p>'
 if count==0:return '<div class="scoreboard intro-board">'+title+'<span class="board-rule"></span><p class="board-instruction">ثلاث إجابات… من وين تبدأ؟</p></div>'
 answers=['تيك توك','كوتش عشوائي','مدار'];rows=''.join('<div class="answer '+('active' if i==count-1 else '')+'">'+v+'</div>' for i,v in enumerate(answers[:count]))
 return '<div class="scoreboard answer-board">'+title+'<div class="answers">'+rows+'</div></div>'
def content(k):
 if k.startswith('wide'):return '<img class="plate" src="assets/studio-master.png" alt="استوديو خيالي بخمسة أشخاص بلا ملامح">'+board(int(k[-1]))
 if k=='win':return '<img class="plate" src="assets/studio-master.png" alt="الاستوديو نفسه"><div class="scoreboard winning-board"><p>مدار فيود</p><strong>مدار</strong><span>هذي الإجابة!</span></div><div class="cyan-sweep" data-layout-ignore></div>'
 if k in ('c1','c2','c3','host'):
  p={'c1':'contestant1','c2':'contestant2','c3':'contestant3','host':'host'}[k]
  tag={'c1':'المتسابق الأول','c2':'المتسابق الثاني','c3':'المتسابق الثالث','host':'مدار فيود'}[k]
  return f'<img class="plate" src="assets/{p}.jpg" alt="شخص بلا ملامح"><div class="shot-tag">{tag}</div>'
 if k=='product':return '<div class="product-content"><p class="eyebrow">هذي بداية أوضح</p><h2>بروتوكول التحوّل<span>من مدار</span></h2><div class="hero-book">'+book()+'</div><p class="product-caption">دليل PDF + موقع مدار</p><div class="fine-rule"></div></div>'
 if k=='program':return '<div class="product-content"><p class="eyebrow">برنامجك وروابط شرحك</p><h2>اعرف وش تتمرّن</h2><div class="program-covers"><img src="assets/program-four.webp" alt="برنامج أربعة أيام"><img src="assets/program-five.webp" alt="برنامج خمسة أيام"></div><div class="feature-strip"><b>٤ أو ٥ أيام</b><span>روابط شرح التمارين داخل الكتاب ↗</span></div></div>'
 if k=='calculator':return '<div class="product-content"><p class="eyebrow">من موقع مدار</p><h2>احسب احتياجك</h2><div class="real-screen calc"><img src="assets/demo-calculator.png" alt="واجهة حاسبة مدار الفعلية"></div><p class="demo-note">مثال توضيحي · احتياجك تقديري حسب بياناتك</p></div>'
 if k=='recipe':return '<div class="product-content"><p class="eyebrow">من موقع مدار</p><h2>٥٠٠ وصفة<span>وقيم تتحدّث مع حصتك</span></h2><div class="real-screen recipe"><img class="before" src="assets/demo-recipe-1.png" alt="وصفة فعلية لحصة واحدة"><img class="after" src="assets/demo-recipe-15.png" alt="القيم بعد تعديل الحصة إلى 1.5"></div><p class="demo-note">عرض توضيحي · القيم الغذائية تقديرية</p></div>'
 if k=='closing':return '<div class="product-content closing-content"><img class="logo" src="assets/closing-logo.png" alt="شعار مدار الأصلي"><h2>بروتوكول التحوّل<span>من مدار</span></h2><div class="close-book">'+book()+'</div><div class="price">15 <span>ريال فقط</span></div><p class="slogan">مدار… اختصر البداية.</p><div class="buy">ابدأ الآن</div><p class="store">mdaar21.zid.store</p></div>'
scenes=''.join(f'<section id="{n}" class="scene kind-{k}" data-layout-allow-overflow><div class="camera">{content(k)}</div></section>' for n,a,b,k in spec)
caps=json.loads((R/'captions.json').read_text())
caption_html='<div class="caption-layer">'+''.join(f'<div id="cap{i}" class="caption"><span class="speaker">'+('المقدم' if c['role']=='host' else 'المتسابق')+'</span><p>'+html.escape(c['text'])+'</p></div>' for i,c in enumerate(caps))+'</div>'
css=(R/'style.css').read_text();js=(R/'animate.js').read_text()
out='<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=1080,height=1920"><title>مدار فيود — إعلان تمثيلي</title><style>'+css+'</style><script src="assets/gsap.min.js"></script></head><body><main id="root" data-composition-id="mdaar-feud" data-start="0" data-duration="30" data-width="1080" data-height="1920">'+scenes+'<div class="fiction-label">إعلان تمثيلي · برنامج خيالي</div>'+caption_html+'<audio id="mix" src="assets/final-mix.wav" data-start="0" data-duration="30" data-track-index="3" data-volume="1"></audio></main><script>const BEATS='+json.dumps(beats)+';const CAPS='+json.dumps(caps,ensure_ascii=False)+';'+js+'</script></body></html>'
(R/'index.html').write_text(out);print(json.dumps({'seconds':30,'shots':len(spec),'captionGroups':len(caps)}))
