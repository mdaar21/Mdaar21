const tl=gsap.timeline({paused:true});
BEATS.forEach((b,i)=>{
 const s='#'+b.id,cam=s+' .camera',d=b.end-b.start;
 tl.set(s,{opacity:1},b.start);
 if(i){
  // Fast broadcast-style handoff with a brief focus/dissolve bridge.
  tl.fromTo(s,{opacity:0},{opacity:1,duration:i===12?.28:.10,ease:'power1.inOut'},b.start);
  tl.set('#'+BEATS[i-1].id,{opacity:0},b.start+(i===12?.28:.11));
 }
 if(b.kind.startsWith('wide')||['host','c1','c2','c3'].includes(b.kind)){
  tl.from(cam,{scale:i===0?1.015:1.022,x:i%2?10:-10,duration:d,ease:'sine.inOut'},b.start);
  if(b.kind.startsWith('wide')){
   if(i)tl.from(s+' .scoreboard',{opacity:0,duration:.16,ease:'power2.out'},b.start+.04);
   else tl.from(s+' .scoreboard',{y:5,duration:.16,ease:'power2.out'},0);
   if(b.kind!=='wide0')tl.from(s+' .answer.active',{rotationX:-78,opacity:0,transformPerspective:800,transformOrigin:'50% 0%',duration:.32,ease:'power3.out'},b.start+.10);
  }else tl.from(s+' .shot-tag',{x:35,opacity:0,duration:.22,ease:'power3.out'},b.start+.10);
 }
 if(b.kind==='win'){
  tl.from(s+' .winning-board strong',{scale:.78,opacity:0,duration:.24,ease:'expo.out'},b.start+.02);
  tl.fromTo(s+' .cyan-sweep',{x:-850},{x:1600,duration:.45,ease:'power2.inOut'},b.start);
 }
 if(['product','program','calculator','recipe','closing'].includes(b.kind)){
  const q=s+' .product-content';
  tl.from(q+' h2',{y:32,opacity:0,duration:.30,ease:'power3.out'},b.start+.10);
  if(b.kind!=='closing')tl.from(q+' .eyebrow',{y:15,opacity:0,duration:.23,ease:'sine.out'},b.start+.04);
  const hero={product:'.hero-book',program:'.program-covers',calculator:'.real-screen',recipe:'.real-screen',closing:'.close-book'}[b.kind];
  tl.from(s+' '+hero,{y:65,scale:.96,opacity:0,duration:.38,ease:'power2.out'},b.start+.16);
  if(b.kind==='product')tl.fromTo(s+' .book',{rotationY:-20,rotationZ:-4},{rotationY:-8,rotationZ:-1,duration:d,ease:'sine.inOut'},b.start);
  if(b.kind==='calculator')tl.to(s+' .real-screen img',{y:-50,duration:1.0,ease:'sine.inOut'},b.start+.45);
  if(b.kind==='recipe')tl.to(s+' .after',{opacity:1,duration:.30,ease:'sine.inOut'},b.start+.65);
  if(b.kind==='closing'){
   tl.from(s+' .logo',{scale:.93,opacity:0,duration:.28,ease:'sine.out'},b.start+.08);
   tl.from(s+' .price',{y:22,opacity:0,duration:.28,ease:'power2.out'},b.start+.25);
   tl.from(s+' .slogan',{y:18,opacity:0,duration:.25,ease:'power3.out'},b.start+.32);
   tl.from(s+' .buy',{y:15,opacity:0,duration:.22,ease:'sine.out'},b.start+.35);
   tl.from(s+' .store',{opacity:0,duration:.20,ease:'power1.out'},b.start+.35);
  }
 }
});
CAPS.forEach((c,i)=>{
 // Final line is already displayed on the held hero; do not cover the price.
 if(c.start>=27)return;
 tl.set('#cap'+i,{opacity:1},c.start);
 tl.from('#cap'+i,{y:8,duration:.10,ease:'power2.out'},c.start);
 tl.set('#cap'+i,{opacity:0},c.end);
});
tl.set('.fiction-label',{opacity:0},19);
window.__timelines=window.__timelines||{};window.__timelines['mdaar-feud']=tl;
