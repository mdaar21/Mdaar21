window.__timelines=window.__timelines||{};
const tl=gsap.timeline({paused:true});
const pivots={head:[260,174],'arm-l':[225,228],'fore-l':[170,310],'arm-r':[295,228],'fore-r':[350,310],'leg-l':[235,433],'leg-r':[285,433]};
function joint(s,key,deg,time,duration=.65){const [x,y]=pivots[key];tl.to(`${s} .${key}`,{attr:{transform:`rotate(${deg} ${x} ${y})`},duration,ease:'sine.inOut'},time)}
function pose(s,values,time){for(const[k,v]of Object.entries(values)){const[x,y]=pivots[k];tl.set(`${s} .${k}`,{attr:{transform:`rotate(${v} ${x} ${y})`}},Math.max(0,time-.6))}}
function enter(selector,t,kind='rise',d=.56){
 const p=kind==='side'?{x:26,opacity:0}:kind==='scale'?{scale:.975,opacity:0}:kind==='turn'?{rotation:-1.8,y:12,opacity:0}:{y:22,opacity:0};
 const ease=kind==='side'?'power3.out':kind==='scale'?'power2.out':kind==='turn'?'sine.out':'power4.out';
 tl.from(selector,{...p,duration:d,ease,immediateRender:true},Math.max(0,t));
}
function handoff(b,old){
 const next='#'+b.id,prev='#'+old.id,T=b.start-.30,d=.62;
 if(b.family==='dissolve'){
  // Old title is removed only during the handoff; new type enters afterwards.
  tl.to(prev+' h2,'+prev+' .subtitle,'+prev+' .demo-note',{opacity:0,duration:.24,ease:'sine.in'},T);
  tl.fromTo(next,{opacity:0},{opacity:1,duration:d,ease:'sine.inOut',immediateRender:false},T);
  tl.fromTo(next+' .camera',{scale:1.015},{scale:1,duration:d,ease:'power2.out',immediateRender:false},T);
 }else{
  tl.to(prev+' h2,'+prev+' .subtitle,'+prev+' .demo-note',{opacity:0,duration:.10,ease:'sine.in'},T);
  tl.set(next,{opacity:1},T);
  let from='inset(0% 0% 0% 100%)',to='inset(0% 0% 0% 0%)';
  if(b.family==='vertical')from='inset(100% 0% 0% 0%)';
  if(b.family==='anchor')from='inset(35% 30% 40% 25% round 26px)';
  if(b.family==='diagonal'){from='polygon(0% 0%, -30% 0%, -60% 100%, 0% 100%)';to='polygon(0% 0%, 130% 0%, 100% 100%, 0% 100%)'}
  if(b.family==='diagonal-reverse'){from='polygon(160% 0%, 100% 0%, 100% 100%, 130% 100%)';to='polygon(0% 0%, 100% 0%, 100% 100%, -30% 100%)'}
  tl.set(next,{clipPath:from},T);
  tl.fromTo(next,{clipPath:from},{clipPath:to,duration:d-.12,ease:'power3.inOut',immediateRender:false},T+.12);
  const axis=b.family==='vertical'?'y':'x';
  tl.fromTo(next+' .camera',{[axis]:b.family==='anchor'?0:40,scale:b.family==='anchor'?1.035:1.01},{[axis]:0,scale:1,duration:d,ease:'power2.out',immediateRender:false},T);
 }
 tl.set(prev,{opacity:0},T+d+.01);
 tl.set(next,{clipPath:'none',opacity:1},T+d+.012);
}
BEATS.forEach((b,i)=>{
 const s='#'+b.id,t=Math.max(.1,b.start-.25);
 if(i)handoff(b,BEATS[i-1]);
 if(i===0)tl.from(s+' h2',{y:12,duration:.52,ease:'power3.out',immediateRender:true},.12);
 else enter(s+' h2',b.start+(i===7?.34:.36),'rise',.48);
 if(document.querySelector(s+' .subtitle'))enter(s+' .subtitle',i?b.start+.40:.23,'side',.50);
 if(document.querySelector(s+' .stage')){
  if(i===0)tl.from(s+' .stage',{scale:.99,duration:.60,ease:'power2.out',immediateRender:true},.1);
  else enter(s+' .stage',t,'scale',.60);
 }
 if(document.querySelector(s+' .demo-note'))enter(s+' .demo-note',b.start+.41,'side',.45);
});
pose('#s0',{'arm-l':18,'fore-l':68,'arm-r':-18,'fore-r':-68,head:-5},0);
joint('#s0','head',4,.45,.75);joint('#s0','fore-r',-92,.62,.65);
enter('#s0 .mini-source',.28,'side');enter('#s0 .question-mark',.19,'turn');
pose('#s1',{'arm-l':28,'fore-l':87,'arm-r':-25,'fore-r':-90,head:4},1.6);
['.source-option:nth-child(1)','.source-option:nth-child(2)','.source-option:nth-child(3)'].forEach((sel,i)=>enter('#s1 '+sel,1.91+i*.20,i%2?'rise':'side',.52));
joint('#s1','head',-5,3.3,.80);joint('#s1','head',3,4.5,.8);
tl.to('#s1 .source-option:nth-child(1)',{x:-12,duration:.65,ease:'sine.inOut'},3.2);
tl.to('#s1 .source-option:nth-child(2)',{x:12,duration:.65,ease:'sine.inOut'},3.7);
pose('#s2',{'arm-r':-55,'fore-r':-88,'arm-l':5,'fore-l':12,head:-3},6.0);
enter('#s2 .book-object',6.11,'turn',.68);enter('#s2 .book-caption',6.82,'side');
joint('#s2','head',2,8.0,.75);joint('#s2','fore-r',-103,8.4,.65);
enter('#s3 .book-object',10.44,'turn',.66);enter('#s3 .bundle-tag',10.60,'side');
document.querySelectorAll('#s3 .menu-row').forEach((e,i)=>enter('#s3 .menu-row:nth-of-type('+(i+2)+')',10.75+i*.14,'side',.52));
enter('#s4 .pc-four',14.05,'turn',.64);enter('#s4 .pc-five',14.18,'side',.64);enter('#s4 .link-note',14.55,'rise',.50);
enter('#s5 .screen-frame',16.78,'scale',.66);enter('#s5 .calc-corner',17.38,'side',.50);
enter('#s6 .screen-frame',19.78,'side',.66);enter('#s6 .portion-callout',20.38,'rise',.50);
tl.set('#s6 .portion-after',{opacity:0},0);
tl.to('#s6 .recipe-after',{opacity:1,duration:.28,ease:'sine.inOut'},22.18);
tl.set('#s6 .portion-one',{opacity:0},22.18);
tl.set('#s6 .portion-after',{opacity:1},22.18);
tl.to('#s6 .portion-callout',{y:-7,duration:.42,ease:'power2.out'},22.18);
pose('#s7',{'arm-r':-55,'fore-r':-90,'arm-l':2,'fore-l':4,head:0},25.0);
enter('#s7 .close-logo',25.34,'rise',.52);enter('#s7 .close-stage',25.24,'scale',.62);
enter('#s7 .price-line',25.53,'rise',.52);enter('#s7 .purchase-cta',25.65,'side',.52);enter('#s7 .store-url',25.74,'rise',.52);
CAPTIONS.forEach((g,i)=>{
 tl.set('#cap-'+i,{visibility:'visible'},g.start);
 tl.fromTo('#cap-'+i,{opacity:0},{opacity:1,duration:Math.min(.08,(g.end-g.start)/4),ease:'sine.out',immediateRender:false},g.start);
 tl.set('#cap-'+i,{opacity:0,visibility:'hidden'},g.end);
});
tl.from('.progress i',{scaleX:0,duration:DURATION,ease:'none'},0);
window.__timelines['mdaar-premium']=tl;
