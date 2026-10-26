window.__timelines=window.__timelines||{};
const tl=gsap.timeline({paused:true});
const pivot={'arm-l':[185,245],'fore-l':[145,345],'arm-r':[335,245],'fore-r':[375,345],'leg-l':[228,427],'leg-r':[292,427],head:[260,145]};
function joint(scene,name,value,t,d=.28,ease='power2.inOut'){
 const [x,y]=pivot[name];tl.to(`${scene} .${name}`,{attr:{transform:`rotate(${value} ${x} ${y})`},duration:d,ease},t);
}
function pose(scene,values,t,d=.28){for(const [k,v]of Object.entries(values))joint(scene,k,v,t,d)}
function enter(selector,t,kind=0,d=.35){
 const vars=kind===1?{x:95,opacity:0}:kind===2?{scale:.78,opacity:0}:kind===3?{rotation:-7,y:50,opacity:0}:{y:60,opacity:0};
 tl.from(selector,{...vars,duration:d,ease:kind===1?'expo.out':kind===2?'back.out(1.25)':kind===3?'sine.out':'power4.out',immediateRender:false},t);
}
function transition(i,kind){
 const t=BEATS[i].start-.12,old=`#s${i-1}`,next=`#s${i}`;
 if(kind==='iris'){
  tl.set(next,{opacity:1},t);
  tl.fromTo(next,{clipPath:'circle(0% at 55% 53%)'},{clipPath:'circle(130% at 55% 53%)',duration:.36,ease:'power3.out',immediateRender:false},t);
  tl.set(old,{opacity:0},t+.30);tl.set(next,{clipPath:'none'},t+.37);
 }else if(kind==='sheet'){
  tl.set(next,{opacity:1},t);
  tl.fromTo(next,{clipPath:'inset(0 100% 0 0)'},{clipPath:'inset(0 0% 0 0)',duration:.32,ease:'power3.inOut',immediateRender:false},t);
  tl.set(old,{opacity:0},t+.33);tl.set(next,{clipPath:'none'},t+.34);
 }else{
  const axis=kind==='up'?'y':'x',distance=axis==='y'?1920:1080;
  tl.to(old,{[axis]:-distance,duration:.34,ease:'power3.inOut'},t);
  tl.fromTo(next,{[axis]:distance,opacity:1},{[axis]:0,opacity:1,duration:.34,ease:'power3.inOut',immediateRender:false},t);
  tl.set(old,{opacity:0},t+.35);
 }
}
function hop(scene,t,h=55){
 tl.to(scene+' .actor',{scaleX:1.04,scaleY:.94,y:8,duration:.09,ease:'power2.in'},t);
 tl.to(scene+' .actor',{scaleX:.97,scaleY:1.04,y:-h,duration:.17,ease:'power2.out'},t+.09);
 tl.to(scene+' .actor',{scaleX:1.045,scaleY:.95,y:8,duration:.15,ease:'power2.in'},t+.26);
 tl.to(scene+' .actor',{scaleX:1,scaleY:1,y:0,duration:.14,ease:'power2.out'},t+.41);
}
tl.from('.brandbar',{y:-28,opacity:0,duration:.35,ease:'expo.out'},.10);
tl.from('.footer',{opacity:0,duration:.30,ease:'sine.out'},.12);
tl.from('.progress i',{scaleX:0,duration:DURATION,ease:'none'},0);
BEATS.forEach((b,i)=>{
 tl.set('.brandbar>span',{color:[1,3,6,7].includes(i)?'#121210':'#f9f5e9'},b.start+.03);
 tl.set('.footer',{color:[1,3,6,7].includes(i)?'#121210':'#d1ac65'},b.start+.03);
 if(i)transition(i,['sheet','up','iris','sheet','up','sheet','iris','sheet','iris','up','sheet','iris','up','sheet'][i-1]);
 const t=b.start+(i?.10:.12),s='#'+b.id;
 enter(s+' h2',t,i%4,.34);
 if(document.querySelector(s+' .stage'))enter(s+' .stage',t+.08,(i+2)%4,.36);
 if(document.querySelector(s+' .eyebrow'))enter(s+' .eyebrow',t+.04,1,.30);
 if(document.querySelector(s+' .demo-note'))enter(s+' .demo-note',t+.30,0,.30);
 if(document.querySelector(s+' .hero-disc'))enter(s+' .hero-disc',t+.02,2,.40);
 if(document.querySelector(s+' .character'))enter(s+' .character',t+.14,3,.38);
});
let t=BEATS[0].start;
pose('#s0',{'arm-l':60,'fore-l':120,'arm-r':-60,'fore-r':-115},.23,.28);hop('#s0',.32,52);
joint('#s0','head',-6,.93,.22);enter('#s0 .label',.48,2,.28);
t=BEATS[1].start;
['.src1','.src2','.src3','.src4'].forEach((sel,i)=>enter('#s1 '+sel,t+.20+i*.13,i%4,.38));
pose('#s1',{'arm-r':-120,'fore-r':-116,'arm-l':25,'fore-l':45,head:-8},t+.25,.32);
for(const dt of [.8,1.4,2]){joint('#s1','fore-r',-129,t+dt,.11);joint('#s1','fore-r',-114,t+dt+.12,.13)}
tl.to('#s1 .src1',{x:18,rotation:1,duration:.3,ease:'power2.inOut'},t+1);
tl.to('#s1 .src4',{y:-24,rotation:-3,duration:.32,ease:'sine.out'},t+1.7);
t=BEATS[2].start;enter('#s2 .speech',t+.20,2,.34);pose('#s2',{'arm-l':65,'fore-l':80,'arm-r':-50,'fore-r':-80,head:7},t+.30,.32);
t=BEATS[3].start;enter('#s3 .week-sheet',t+.20,3,.38);enter('#s3 .check-mark',t+.50,2,.30);
tl.from('#s3 .week-grid>div',{scale:.85,opacity:0,stagger:.055,duration:.23,ease:'power3.out',immediateRender:false},t+.30);
t=BEATS[4].start;
['.qp1','.qp2','.qp3'].forEach((sel,i)=>enter('#s4 '+sel,t+.18+i*.30,i%3,.32));
pose('#s4',{'arm-l':30,'fore-l':40,'arm-r':-35,'fore-r':-50,head:-6},t+.25,.30);joint('#s4','head',8,t+1.05,.23);
t=BEATS[5].start;enter('#s5 .training-icon',t+.24,1,.38);enter('#s5 .doubt-pulse',t+.45,2,.30);enter('#s5 .food-prop',t+.75,3,.34);
pose('#s5',{'arm-r':-45,'fore-r':-45,'arm-l':15,'fore-l':20,head:-7},t+.25,.28);
t=BEATS[6].start;enter('#s6 .follow-label',t+.20,0,.28);pose('#s6',{'arm-r':-45,'fore-r':-60,'arm-l':25,'fore-l':35,head:5},t+.30,.30);
tl.to('#s6 .character:first-of-type .actor',{x:15,duration:.32,ease:'power2.inOut'},t+.9);
t=BEATS[7].start;enter('#s7 .receipt',t+.15,3,.40);enter('#s7 .over-budget',t+.9,2,.27);
tl.from('#s7 .bars i',{scaleY:.1,transformOrigin:'bottom',stagger:.13,duration:.42,ease:'expo.out',immediateRender:false},t+.27);
pose('#s7',{'arm-l':32,'fore-l':74,'arm-r':-60,'fore-r':-110,head:-8},t+.3,.28);
joint('#s7','head',6,t+1.15,.23);joint('#s7','head',-6,t+1.45,.24);
t=BEATS[8].start;enter('#s8 .product-phone',t+.13,2,.48);enter('#s8 .digital-tag',t+.42,3,.30);
pose('#s8',{'arm-l':45,'fore-l':45,'arm-r':-55,'fore-r':-115,head:-6},t+.32,.32);hop('#s8',t+.60,44);
tl.set('#s8 .pointer-l',{opacity:1},t+.65);
t=BEATS[9].start;enter('#s9 .pc4',t+.20,1,.38);enter('#s9 .pc5',t+.38,3,.38);
tl.to('#s9 .pc4',{rotation:0,y:-15,duration:.38,ease:'power3.out'},t+.85);
tl.to('#s9 .pc5',{rotation:0,y:-15,duration:.38,ease:'power3.out'},t+1.15);
t=BEATS[10].start;enter('#s10 .product-phone',t+.18,3,.38);enter('#s10 .link-card',t+.45,1,.32);
tl.to('#s10 .link-card span',{x:-7,y:-7,duration:.17,ease:'power2.out'},t+1.05);
tl.to('#s10 .link-card span',{x:0,y:0,duration:.22,ease:'sine.out'},t+1.22);
t=BEATS[11].start;enter('#s11 .screen-frame',t+.20,2,.42);
t=BEATS[12].start;enter('#s12 .screen-frame',t+.18,1,.40);enter('#s12 .recipe-count',t+.32,3,.35);enter('#s12 .serving-demo',t+.85,0,.34);
tl.to('#s12 .recipe-first',{y:-120,duration:.60,ease:'power2.inOut'},t+.80);
tl.to('#s12 .recipe-scaled',{y:-120,duration:.60,ease:'power2.inOut'},t+.80);
tl.to('#s12 .recipe-scaled',{opacity:1,duration:.16,ease:'sine.out'},t+1.55);
t=BEATS[13].start;enter('#s13 .pc4',t+.20,3,.38);enter('#s13 .pc5',t+.36,1,.38);enter('#s13 .summary-pills',t+.40,0,.30);
t=BEATS[14].start;enter('#s14 .final-stage',t+.12,2,.35);enter('#s14 .closing-logo',t+.16,3,.32);enter('#s14 .product-phone',t+.15,1,.36);enter('#s14 .cta',t+.30,2,.34);enter('#s14 .url',t+.42,0,.28);
pose('#s14',{'arm-l':45,'fore-l':45,'arm-r':-55,'fore-r':-115,head:0},t+.30,.30);
// One readable RTL caption group at a time. Per-word emphasis never changes layout.
CAPTIONS.forEach((g,i)=>{
 tl.set('#cap-'+i,{visibility:'visible'},g.start);
 tl.fromTo('#cap-'+i,{opacity:0,y:15,scale:.985},{opacity:1,y:0,scale:1,duration:Math.min(.13,(g.end-g.start)/3),ease:'power3.out',immediateRender:false},g.start);
 g.words.forEach((w,j)=>{
  tl.set('#cw-'+i+'-'+j,{color:'#d1ac65'},Math.max(g.start,w.start));
  tl.set('#cw-'+i+'-'+j,{color:'#f9f5e9'},Math.min(g.end,w.end));
 });
 tl.set('#cap-'+i,{opacity:0,visibility:'hidden'},g.end);
});
window.__timelines['mdaar-voice']=tl;
