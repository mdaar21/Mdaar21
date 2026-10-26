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
const transitionMap=Object.fromEntries(TRANSITIONS.map(x=>[x.to,x]));
function transition(index,previous){
 const b=BEATS[index],spec=transitionMap[b.id],old='#'+previous.id,next='#'+b.id;
 const T=b.start-.28,d=spec.duration,oc=old+' .scene-camera',nc=next+' .scene-camera';
 const neutral={x:0,y:0,scale:1,filter:'blur(0px)'};
 if(spec.family==='diagonal'){
  const from=spec.direction==='left'?'polygon(0% 0%, -30% 0%, -60% 100%, 0% 100%)':'polygon(160% 0%, 100% 0%, 100% 100%, 130% 100%)';
  const to=spec.direction==='left'?'polygon(0% 0%, 130% 0%, 100% 100%, 0% 100%)':'polygon(0% 0%, 100% 0%, 100% 100%, -30% 100%)';
  tl.set(next,{opacity:1},T);
  tl.fromTo(next,{clipPath:from},{clipPath:to,duration:d,ease:'power3.inOut',immediateRender:false},T);
  tl.fromTo(nc,{...neutral,x:spec.direction==='left'?28:-28},{x:0,duration:d,ease:'power2.out',immediateRender:false},T);
 }else if(spec.family==='anchor'){
  const n=spec.anchor.match(/[-.0-9]+/g).map(Number),cy=(n[0]+100-n[2])/2,cx=(n[3]+100-n[1])/2;
  const point=`inset(${cy}% ${100-cx}% ${100-cy}% ${cx}% round 16px)`;
  tl.set(next,{opacity:1},T);
  tl.fromTo(next,{clipPath:point},{clipPath:spec.anchor,duration:d*.24,ease:'power2.out',immediateRender:false},T);
  tl.to(next,{clipPath:'inset(0% 0% 0% 0% round 0px)',duration:d*.76,ease:'power3.inOut'},T+d*.24);
  tl.fromTo(nc,{...neutral,scale:1.045},{scale:1,duration:d,ease:'power2.out',immediateRender:false},T);
 }else if(spec.family==='parallax'){
  const axis=spec.axis,value=spec.distance;
  const clip=axis==='x'?(value>0?'inset(0% 0% 0% 100%)':'inset(0% 100% 0% 0%)'):(value>0?'inset(100% 0% 0% 0%)':'inset(0% 0% 100% 0%)');
  tl.set(next,{opacity:1},T);
  tl.fromTo(next,{clipPath:clip},{clipPath:'inset(0% 0% 0% 0%)',duration:d,ease:'power3.inOut',immediateRender:false},T);
  tl.to(oc,{[axis]:-value*.55,scale:.995,duration:d,ease:'sine.inOut'},T);
  tl.fromTo(nc,{...neutral,[axis]:value,scale:1.02},{[axis]:0,scale:1,duration:d,ease:'power3.out',immediateRender:false},T);
 }else if(spec.family==='focus'){
  tl.to(old+' h2',{opacity:0,duration:d*.35,ease:'power2.in'},T);
  tl.to(oc,{filter:'blur(5px)',scale:.99,duration:d,ease:'sine.inOut'},T);
  tl.fromTo(next,{opacity:0},{opacity:1,duration:d,ease:'power2.out',immediateRender:false},T);
  tl.fromTo(nc,{...neutral,filter:'blur(4px)',scale:1.025},{filter:'blur(0px)',scale:1,duration:d,ease:'sine.out',immediateRender:false},T);
 }else if(spec.family==='shutter'){
  const close=d*.35,open=d*.44;
  tl.set('.transition-shutter',{opacity:1},T);
  tl.fromTo('.shutter-top',{y:0,yPercent:-100},{yPercent:0,duration:close,ease:'sine.inOut',immediateRender:false},T);
  tl.fromTo('.shutter-bottom',{y:0,yPercent:100},{yPercent:0,duration:close,ease:'sine.inOut',immediateRender:false},T);
  tl.set(old,{opacity:0},T+close);
  tl.set(next,{opacity:1},T+close);
  tl.to('.shutter-top',{yPercent:-100,duration:d-open,ease:'sine.inOut'},T+open);
  tl.to('.shutter-bottom',{yPercent:100,duration:d-open,ease:'sine.inOut'},T+open);
  tl.set('.transition-shutter',{opacity:0},T+d+.01);
 }else throw new Error('Unknown transition family '+spec.family);
 tl.set(old,{opacity:0},T+d+.012);
 tl.set(next,{clipPath:'none',opacity:1},T+d+.014);
}
tl.from('.brandbar',{opacity:0,duration:.42,ease:'sine.out'},.10);
tl.from('.footer',{opacity:0,duration:.50,ease:'power2.out'},.14);
tl.from('.progress i',{scaleX:0,duration:DURATION,ease:'none'},0);
BEATS.forEach((b,i)=>{
 if(i)transition(i,BEATS[i-1]);
 const lead=transitionMap[b.id]?.family==='anchor'?.58:.36;
 const t=Math.max(.12,b.start-lead),s='#'+b.id;
 if(i===0)tl.from(s+' h2',{y:18,scale:.985,duration:.50,ease:'power3.out',immediateRender:true},.12);
 else enter(s+' h2',b.start+(b.id==='s8'?.27:.02),i%2,.45);
 if(document.querySelector(s+' .stage'))tl.from(s+' .stage',{opacity:0,duration:.52,ease:'sine.out',immediateRender:true},t+.03);
 if(document.querySelector(s+' .eyebrow'))enter(s+' .eyebrow',b.id==='s8'?b.start+.31:t+.04,1,.40);
 if(document.querySelector(s+' .demo-note'))enter(s+' .demo-note',t+.27,0,.44);
 if(document.querySelector(s+' .hero-disc'))enter(s+' .hero-disc',t+.06,2,.60);
 if(document.querySelector(s+' .character'))enter(s+' .character',t+.09,1,.56);
});
const time=id=>BEATS.find(b=>b.id===id).start-(transitionMap[id]?.family==='anchor'?.58:.36);
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
