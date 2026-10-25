/* Deterministic, seekable cartoon rig. Every face is a single empty fill. */
window.__timelines=window.__timelines||{};
const tl=gsap.timeline({paused:true});
window.__timelines['mdaar-character']=tl;
const pivots={'arm-l':[185,245],'fore-l':[145,345],'arm-r':[335,245],'fore-r':[375,345],'leg-l':[228,427],'leg-r':[292,427],head:[260,145]};
function joint(scene,part,angle,time,duration=.22,ease='power2.inOut'){
  const [cx,cy]=pivots[part];
  const value={attr:{transform:`rotate(${angle} ${cx} ${cy})`}};
  if(duration===0)tl.set(`${scene} .${part}`,value,time);
  else tl.to(`${scene} .${part}`,{...value,duration,ease},time);
}
function pose(scene,values,time,duration=.22,ease='power2.inOut'){
  for(const [part,angle] of Object.entries(values))joint(scene,part,angle,time,duration,ease);
}
function enter(selector,time,kind=0,duration=.3){
  const vars=kind===1?{x:85,opacity:0}:kind===2?{scale:.72,opacity:0}:kind===3?{rotation:-9,scale:.93,opacity:0}:{y:65,opacity:0};
  tl.from(selector,{...vars,duration,ease:kind===1?'expo.out':kind===2?'back.out(1.35)':kind===3?'sine.out':'power3.out'},time);
}
function push(oldScene,newScene,time,direction='up'){
  const axis=direction==='left'?'x':'y',offset=axis==='x'?1080:1920;
  tl.to(oldScene,{[axis]:-offset,duration:.28,ease:'power3.inOut'},time);
  tl.fromTo(newScene,{[axis]:offset,opacity:1},{[axis]:0,opacity:1,duration:.28,ease:'power3.inOut'},time);
  tl.set(oldScene,{opacity:0},time+.29);
}
function paperReveal(oldScene,newScene,time,origin='50% 60%'){
  tl.set(newScene,{opacity:1},time);
  tl.fromTo(newScene,{clipPath:`circle(0% at ${origin})`},{clipPath:`circle(120% at ${origin})`,duration:.26,ease:'power3.out'},time);
  tl.set(newScene,{clipPath:'none'},time+.27);
  // At 0.14 s the expanding circle already covers the entire outgoing canvas.
  tl.set(oldScene,{opacity:0},time+.14);
}
function hop(scene,time,height=60){
  const a=`${scene} .actor`;
  tl.to(a,{scaleX:1.06,scaleY:.92,y:10,duration:.085,ease:'power2.in'},time);
  tl.to(a,{scaleX:.96,scaleY:1.05,y:-height,duration:.16,ease:'power2.out'},time+.085);
  tl.to(a,{scaleX:1.08,scaleY:.93,y:8,duration:.15,ease:'power2.in'},time+.245);
  tl.to(a,{scaleX:1,scaleY:1,y:0,duration:.11,ease:'power2.out'},time+.395);
}
const flex={'arm-l':65,'fore-l':130,'arm-r':-65,'fore-r':-130};
const pointR={'arm-r':-45,'fore-r':-45,'arm-l':-7,'fore-l':12};
const pointL={'arm-l':45,'fore-l':45,'arm-r':7,'fore-r':-12};
tl.from('.brand-bar',{y:-24,opacity:0,duration:.28,ease:'power3.out'},.1);
tl.from('.footer',{opacity:0,duration:.32,ease:'sine.out'},.14);
tl.from('.progress i',{scaleX:0,duration:20,ease:'none'},0);
// 0—2: the actual reference character returns; leap, land, flex.
tl.from('#s1 .word1',{x:85,rotation:-3,duration:.28,ease:'expo.out'},.1);enter('#s1 .word2',.2,2,.32);
enter('#s1 .disc',.17,2,.35);enter('#s1 .halftone',.21,3,.33);
enter('#s1 .character',.22,1,.31);enter('#s1 .sub',.5,0,.25);
hop('#s1',.29,80);
pose('#s1',{'leg-l':12,'leg-r':-12},.36,.12);pose('#s1',{'leg-l':0,'leg-r':0},.61,.16);
pose('#s1',flex,.48,.27,'back.out(1.1)');
pose('#s1',{'fore-l':114,'fore-r':-114,head:-5},1.02,.13);
pose('#s1',{'fore-l':132,'fore-r':-132,head:4},1.18,.16);
tl.to('#s1 .actor',{scale:1.025,duration:.23,ease:'sine.inOut'},1.48);
// 2—4: a comic, readable scratch of the blank head.
push('#s1','#s2',1.85);
enter('#s2 .confusion',2.02,1,.25);enter('#s2 .word-start',2.12,2,.29);
enter('#s2 .disc',2,2,.3);enter('#s2 .halftone',2.06,3,.3);
enter('#s2 .character',2.03,3,.31);enter('#s2 .sub',2.37,0,.25);
enter('#s2 .q1',2.25,2,.22);enter('#s2 .q2',2.43,1,.24);
pose('#s2',{'arm-r':-120,'fore-r':-116,'arm-l':18,'fore-l':35,head:-8},2.05,.24);
for(const t of [2.5,2.91,3.32]){
  joint('#s2','fore-r',-128,t,.09);joint('#s2','fore-r',-114,t+.11,.12);
}
joint('#s2','head',7,2.75,.2);joint('#s2','head',-6,3.22,.2);
tl.to('#s2 .q1',{rotation:9,y:-18,duration:.28,ease:'back.out(1.2)'},2.64);
tl.to('#s2 .q2',{rotation:-8,scale:1.13,duration:.24,ease:'power2.out'},3.05);
// 4—7: two genuine arm-and-barbell repetitions. Hands follow the shaft.
push('#s2','#s3',3.85);
enter('#s3 .number',4,2,.3);enter('#s3 .metric-copy',4.07,1,.28);
enter('#s3 .four',4.16,3,.27);enter('#s3 .five',4.29,0,.27);
enter('#s3 .halftone',4.08,3,.3);enter('#s3 .character',4.12,2,.31);
enter('#s3 .sub',4.43,1,.25);
function gripPose(y,t,d){
  const l1=Math.hypot(-40,100),l2=Math.hypot(5,95),dx=-55,dy=y-245;
  const delta=Math.acos((dx*dx+dy*dy-l1*l1-l2*l2)/(2*l1*l2));
  let angle=Math.atan2(dy,dx)-Math.atan2(l2*Math.sin(delta),l1+l2*Math.cos(delta));
  if(angle<0)angle+=2*Math.PI;
  const upper=(angle-Math.atan2(100,-40))*180/Math.PI;
  const lower=(delta-Math.atan2(95,5)+Math.atan2(100,-40))*180/Math.PI;
  pose('#s3',{'arm-l':upper,'fore-l':lower,'arm-r':-upper,'fore-r':-lower},t,d,'none');
  const vars={attr:{transform:`translate(0 ${y-235})`}};
  if(d===0)tl.set('#s3 .barbell',vars,t);else tl.to('#s3 .barbell',{...vars,duration:d,ease:'none'},t);
}
gripPose(235,3.98,0);
for(const start of [4.65,5.68]){
  [180,120,60,60,120,180,235].forEach((y,i)=>gripPose(y,start+i*.115,.115));
  tl.to('#s3 .actor',{y:8,scaleY:.98,duration:.12,ease:'sine.inOut'},start);
  tl.to('#s3 .actor',{y:-6,scaleY:1.015,duration:.15,ease:'power2.out'},start+.24);
  tl.to('#s3 .actor',{y:0,scaleY:1,duration:.18,ease:'sine.inOut'},start+.61);
}
// 7—9.5: a sharp plate reveal with a pointing character, rather than a lone prop.
paperReveal('#s3','#s4',6.85,'65% 58%');
enter('#s4 .number',6.98,2,.32);enter('#s4 .metric-copy',7.07,1,.25);
enter('#s4 .ribbon',7.16,3,.25);enter('#s4 .wash',6.95,0,.3);
enter('#s4 .character',7.12,1,.3);enter('#s4 .food-art',7.21,3,.34);
enter('#s4 .sub',7.42,0,.26);
pose('#s4',pointR,7.14,.24);tl.set('#s4 .pointer-r',{opacity:1},7.36);
hop('#s4',7.56,40);joint('#s4','head',-7,7.62,.2);
joint('#s4','arm-r',-62,8.15,.19);joint('#s4','fore-r',-32,8.15,.19);
tl.to('#s4 .food-art',{rotation:3,scale:1.045,duration:.16,ease:'power2.out'},8.23);
tl.to('#s4 .food-art',{rotation:0,scale:1,duration:.24,ease:'back.out(1.2)'},8.41);
pose('#s4',{'arm-l':45,'fore-l':85,head:4},8.62,.23);
// 9.5—11.5: hand gestures follow the three goals, top to bottom.
push('#s4','#s5',9.35);
enter('#s5 h2',9.52,1,.26);enter('#s5 .wash',9.5,3,.29);
enter('#s5 .character',9.56,2,.3);enter('#s5 .cut',9.66,3,.24);
enter('#s5 .steady',9.92,2,.25);enter('#s5 .gain',10.19,0,.25);
enter('#s5 .sub',9.87,1,.26);
tl.set('#s5 .pointer-r',{opacity:1},9.68);
pose('#s5',{'arm-r':-72,'fore-r':-45,'arm-l':-6,'fore-l':15,head:-5},9.59,.25);
pose('#s5',{'arm-r':-43,'fore-r':-48,head:0},10,.22);
pose('#s5',{'arm-r':-18,'fore-r':-40,head:6},10.42,.22);
for(const [selector,time] of [['.cut',9.91],['.steady',10.29],['.gain',10.71]]){
  tl.to('#s5 '+selector,{x:16,scale:1.025,duration:.1,ease:'power2.out'},time);
  tl.to('#s5 '+selector,{x:0,scale:1,duration:.17,ease:'sine.out'},time+.1);
}
// 11.5—14: paper fans out; the character draws attention to the actual guide.
push('#s5','#s6',11.35,'left');
enter('#s6 .number',11.52,2,.31);enter('#s6 .metric-copy',11.59,1,.26);
enter('#s6 .halftone',11.52,3,.3);
enter('#s6 .sheet.one',11.62,3,.3);enter('#s6 .sheet.two',11.73,0,.3);
enter('#s6 .guide-cover',11.81,1,.34);enter('#s6 .character',11.65,3,.3);
enter('#s6 .ribbon',12.01,2,.28);enter('#s6 .sub',12.2,0,.25);
pose('#s6',{'arm-l':18,'fore-l':90,head:-6},11.68,.24);
pose('#s6',pointL,12.1,.22);tl.set('#s6 .pointer-l',{opacity:1},12.3);
tl.to('#s6 .guide-cover',{rotation:2,y:-8,duration:.35,ease:'back.out(1.1)'},12.4);
tl.to('#s6 .sheet.one',{rotation:-13,x:-14,duration:.3,ease:'power2.out'},12.41);
tl.to('#s6 .sheet.two',{rotation:9,x:14,duration:.31,ease:'power2.out'},12.5);
joint('#s6','head',5,13.1,.2);
// 14—16.8: an original cover reveal, with the character celebrating beside it.
paperReveal('#s6','#s7',13.85,'42% 56%');
enter('#s7 .disc',13.9,2,.4);enter('#s7 .halftone',13.96,3,.4);
enter('#s7 .eyebrow',14.02,1,.26);enter('#s7 .book-wrap',14.03,2,.4);
enter('#s7 .character',14.14,3,.32);enter('#s7 h2',14.3,0,.28);enter('#s7 .sub',14.46,1,.26);
pose('#s7',pointL,14.14,.24);tl.set('#s7 .pointer-l',{opacity:1},14.37);
hop('#s7',14.56,55);
tl.to('#s7 .book-wrap',{rotation:2.4,scale:1.025,duration:.45,ease:'sine.inOut'},15.05);
pose('#s7',{'arm-r':-65,'fore-r':-130,head:-5},15.37,.23);
tl.to('#s7 .book-wrap',{rotation:1,scale:1.012,duration:.45,ease:'sine.inOut'},15.85);
// 16.8—20: final jump, then a readable purchase frame with no music.
push('#s7','#s8',16.65,'left');
enter('#s8 .disc',16.73,2,.35);enter('#s8 .halftone',16.8,3,.35);
enter('#s8 .closing-book',16.82,3,.29);enter('#s8 .logo',16.86,2,.29);
enter('#s8 .character',16.84,1,.3);enter('#s8 .brand-name',16.95,0,.3);
enter('#s8 h2',17.06,1,.28);enter('#s8 .cta',17.19,2,.32);
enter('#s8 .url',17.34,0,.28);enter('#s8 .closing-note',17.48,1,.26);
pose('#s8',{'arm-l':65,'fore-l':130,'arm-r':10,'fore-r':-10,head:-5},16.83,.25);
hop('#s8',17.06,45);tl.set('#s8 .pointer-r',{opacity:1},17.51);
pose('#s8',{'arm-r':-8,'fore-r':6,head:3},17.72,.18);
pose('#s8',{'arm-r':8,'fore-r':-8,head:0},18,.19);
tl.to('#s8 .closing-book',{rotation:-2,duration:.42,ease:'sine.inOut'},18.13);
tl.to('#s8 .cta img',{x:-9,duration:.16,ease:'power2.out'},18.4);
tl.to('#s8 .cta img',{x:0,duration:.2,ease:'sine.out'},18.56);
