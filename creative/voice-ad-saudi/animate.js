window.__timelines=window.__timelines||{};
const tl=gsap.timeline({paused:true});
const pivot={'arm-l':[185,245],'fore-l':[145,345],'arm-r':[335,245],'fore-r':[375,345],'leg-l':[228,427],'leg-r':[292,427],head:[260,145]};
function joint(s,name,value,t,d=.54,ease='sine.inOut'){
 const [x,y]=pivot[name];tl.to(`${s} .${name}`,{attr:{transform:`rotate(${value} ${x} ${y})`},duration:d,ease},t);
}
function initialPose(s,values,t){
 for(const [k,v]of Object.entries(values)){const[x,y]=pivot[k];tl.set(`${s} .${k}`,{attr:{transform:`rotate(${v} ${x} ${y})`}},Math.max(0,t-.30));}
}
function enter(selector,t,kind=0,d=.52){
 const vars=kind===1?{x:24,opacity:0}:kind===2?{scale:.965,opacity:0}:kind===3?{rotation:-1.8,y:14,opacity:0}:{y:18,opacity:0};
 tl.from(selector,{...vars,duration:d,ease:kind===1?'power3.out':kind===2?'power2.out':kind===3?'sine.out':'power4.out',immediateRender:true},t);
}
function transition(index,previous){
 const b=BEATS[index],old='#'+previous.id,next='#'+b.id,t=b.start-.28;
 const vertical=['s11','s12'].includes(b.id),length=b.id==='s14'?.70:.60;
 tl.set(next,{opacity:1},t);
 tl.fromTo(next,{clipPath:vertical?'inset(100% 0 0 0)':'inset(0 0 0 100%)'},
  {clipPath:'inset(0 0 0 0%)',duration:length,ease:'sine.inOut',immediateRender:false},t);
 tl.set(old,{opacity:0},t+length+.01);tl.set(next,{clipPath:'none'},t+length+.015);
}
tl.from('.brandbar',{opacity:0,duration:.42,ease:'sine.out'},.10);
tl.from('.footer',{opacity:0,duration:.50,ease:'power2.out'},.14);
tl.from('.progress i',{scaleX:0,duration:DURATION,ease:'none'},0);
BEATS.forEach((b,i)=>{
 if(i)transition(i,BEATS[i-1]);
 const t=Math.max(.12,b.start-.015),s='#'+b.id;
 enter(s+' h2',i===0?.12:b.start+(b.id==='s14'?.44:.35),i%2,.45);
 if(document.querySelector(s+' .stage'))tl.from(s+' .stage',{opacity:0,duration:.52,ease:'sine.out',immediateRender:true},t+.03);
 if(document.querySelector(s+' .eyebrow'))enter(s+' .eyebrow',t+.04,1,.40);
 if(document.querySelector(s+' .demo-note'))enter(s+' .demo-note',t+.27,0,.44);
 if(document.querySelector(s+' .hero-disc'))enter(s+' .hero-disc',t+.06,2,.60);
 if(document.querySelector(s+' .character'))enter(s+' .character',t+.09,1,.56);
});
const time=id=>BEATS.find(b=>b.id===id).start;
initialPose('#s0',{'arm-l':58,'fore-l':112,'arm-r':-52,'fore-r':-105,head:-3},0);
enter('#s0 .label',.38,1,.48);joint('#s0','head',2,.72,.70);
let t=time('s1');
initialPose('#s1',{'arm-r':-120,'fore-r':-116,'arm-l':25,'fore-l':45,head:-5},t);
['.src1','.src2','.src3','.src4'].forEach((sel,i)=>enter('#s1 '+sel,t+.10+i*.09,i%2,.52));
joint('#s1','head',3,t+.70,.70);joint('#s1','fore-r',-122,t+.80,.48);joint('#s1','fore-r',-116,t+1.42,.50);
t=time('s2');initialPose('#s2',{'arm-l':55,'fore-l':70,'arm-r':-45,'fore-r':-70,head:3},t);
enter('#s2 .speech',t+.25,2,.50);joint('#s2','head',-2,t+.80,.60);
t=time('s3');enter('#s3 .week-sheet',t+.12,1,.53);enter('#s3 .check-mark',t+.42,2,.46);
tl.from('#s3 .week-grid>div',{opacity:0,stagger:.045,duration:.38,ease:'sine.out',immediateRender:true},t+.30);
t=time('s4');initialPose('#s4',{'arm-l':25,'fore-l':40,'arm-r':-30,'fore-r':-42,head:-3},t);
['.qp1','.qp2','.qp3'].forEach((sel,i)=>enter('#s4 '+sel,t+.12+i*.20,i%2,.48));joint('#s4','head',4,t+.90,.65);
t=time('s5');initialPose('#s5',{'arm-r':-45,'fore-r':-45,'arm-l':15,'fore-l':20,head:-3},t);
enter('#s5 .training-icon',t+.12,1,.52);enter('#s5 .food-prop',t+.58,0,.58);enter('#s5 .doubt-pulse',t+.60,2,.48);
joint('#s5','head',3,t+1.10,.62);
t=time('s6');initialPose('#s6',{'arm-r':-40,'fore-r':-55,'arm-l':20,'fore-l':30,head:2},t);
enter('#s6 .follow-label',t+.20,0,.48);
joint('#s6 .character:first-of-type','head',-3,t+.70,.65);
joint('#s6 .character:nth-of-type(2)','fore-r',-48,t+.90,.65);
t=time('s7');initialPose('#s7',{'arm-l':30,'fore-l':68,'arm-r':-52,'fore-r':-103,head:-3},t);
enter('#s7 .receipt',t+.10,1,.58);enter('#s7 .over-budget',t+.85,3,.48);
tl.from('#s7 .bars i',{scaleY:.35,transformOrigin:'bottom',stagger:.10,duration:.65,ease:'power2.out',immediateRender:true},t+.22);
joint('#s7','head',4,t+1.10,.70);
t=time('s8');initialPose('#s8',{'arm-l':45,'fore-l':45,'arm-r':-50,'fore-r':-103,head:-3},t);
enter('#s8 .product-phone',t+.08,2,.65);enter('#s8 .digital-tag',t+.38,1,.52);
tl.set('#s8 .pointer-l',{opacity:1},Math.max(0,t-.10));joint('#s8','head',2,t+1.10,.70);
t=time('s9');enter('#s9 .pc4',t+.10,1,.54);enter('#s9 .pc5',t+.26,0,.60);
tl.to('#s9 .pc4',{rotation:2,y:-8,duration:.70,ease:'sine.inOut'},t+.80);
tl.to('#s9 .pc5',{rotation:-2,y:-8,duration:.70,ease:'sine.inOut'},t+1.08);
t=time('s10');enter('#s10 .product-phone',t+.10,2,.58);enter('#s10 .link-card',t+.34,1,.52);
t=time('s11');enter('#s11 .screen-frame',t+.10,2,.62);
t=time('s12');enter('#s12 .screen-frame',t+.10,1,.58);enter('#s12 .recipe-count',t+.26,0,.52);enter('#s12 .serving-demo',t+.76,0,.48);
tl.to('#s12 .recipe-first',{y:-120,duration:.95,ease:'sine.inOut'},t+.75);
tl.to('#s12 .recipe-scaled',{y:-120,duration:.95,ease:'sine.inOut'},t+.75);
tl.to('#s12 .recipe-scaled',{opacity:1,duration:.32,ease:'sine.inOut'},t+1.65);
t=time('s14');initialPose('#s14',{'arm-l':45,'fore-l':45,'arm-r':-50,'fore-r':-105,head:0},t);
enter('#s14 .final-stage',t+.06,2,.62);enter('#s14 .closing-logo',t+.12,0,.48);enter('#s14 .product-phone',t+.12,1,.62);enter('#s14 .cta',t+.32,0,.56);enter('#s14 .url',t+.46,0,.50);
joint('#s14','head',-2,t+1.70,.85);
// Fixed caption plate; phrase fades only. No jumping box or per-word scale changes.
CAPTIONS.forEach((g,i)=>{
 tl.set('#cap-'+i,{visibility:'visible'},g.start);
 tl.fromTo('#cap-'+i,{opacity:0},{opacity:1,duration:Math.min(.095,(g.end-g.start)/4),ease:'sine.out',immediateRender:false},g.start);
 tl.set('#cap-'+i,{opacity:0,visibility:'hidden'},g.end);
});
window.__timelines['mdaar-voice']=tl;
