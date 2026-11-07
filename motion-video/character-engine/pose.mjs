/** Deterministic, asset-independent animation timing engine. Units: seconds. */
const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
const smooth=x=>{const t=clamp(x,0,1);return t*t*(3-2*t)};
const lerp=(a,b,t)=>a+(b-a)*t;
export const PROFILES=Object.freeze({
 kitsune:{stepHz:1.8,tailHz:1.1,tailAmp:13,gestureAmp:18,blinkPeriod:3.6},
 wukong:{stepHz:2.5,tailHz:1.8,tailAmp:19,gestureAmp:28,blinkPeriod:2.9},
 tengu:{stepHz:1.5,tailHz:.8,tailAmp:10,gestureAmp:13,blinkPeriod:4.1}
});
export function mouthAt(t,syllables=[]){
 let level=0;
 for(const s of syllables){
  if(!(s.end>s.start))continue;
  const fade=Math.min(.055,(s.end-s.start)*.3);
  level=Math.max(level,clamp(s.energy??.8,0,1)*smooth((t-s.start)/fade)*smooth((s.end-t)/fade));
 }
 return level;
}
export function poseAt(character,t,actions=[],syllables=[]){
 if(!Number.isFinite(t)||t<0)throw Error('invalid time');
 const p=PROFILES[character];if(!p)throw Error('unknown character');
 const active=actions.filter(a=>a.end>a.start&&t>=a.start&&t<=a.end);
 const walk=active.find(a=>a.type==='walk');
 const gesture=active.find(a=>a.type==='gesture');
 const look=active.find(a=>a.type==='look');
 const phase=2*Math.PI*p.stepHz*t;
 const walkWeight=walk?smooth(Math.min((t-walk.start)/.16,(walk.end-t)/.16,1)):0;
 const progress=walk?smooth((t-walk.start)/(walk.end-walk.start)):0;
 const gestureWeight=gesture?Math.sin(Math.PI*clamp((t-gesture.start)/(gesture.end-gesture.start),0,1)):0;
 const blinkPhase=t%p.blinkPeriod;
 const blink=blinkPhase<.17?Math.sin(Math.PI*blinkPhase/.17)**2:0;
 const finishedWalks=actions.filter(a=>a.type==='walk'&&a.end<=t).sort((a,b)=>a.end-b.end);
 const restX=finishedWalks.length?finishedWalks[finishedWalks.length-1].toX??0:0;
 const x=walk?lerp(walk.fromX??restX,walk.toX??restX,progress):restX;
 return {character,t,
  world:{x,y:walkWeight*Math.abs(Math.sin(phase))*4},
  body:{bob:Math.sin(t*2.2)*2+walkWeight*Math.abs(Math.sin(phase))*5,lean:walkWeight*Math.sin(phase)*3},
  head:{turn:look?(look.direction??1)*12*Math.sin(Math.PI*clamp((t-look.start)/(look.end-look.start),0,1)):Math.sin(t*.65)*2,tilt:Math.sin(t*.9)*1.8},
  eyes:{blink:clamp(blink,0,1),lookX:look?(look.direction??1)*.7:0},
  mouth:{open:active.some(a=>a.type==='speak')?mouthAt(t,syllables):0},
  limbs:{leftLeg:walkWeight*Math.sin(phase)*24,rightLeg:-walkWeight*Math.sin(phase)*24,
   leftArm:-walkWeight*Math.sin(phase)*14+(gesture?.hand==='left'?gestureWeight*p.gestureAmp:0),
   rightArm:walkWeight*Math.sin(phase)*14+(gesture?.hand==='right'?gestureWeight*p.gestureAmp:0)},
  secondary:{tailAngle:Math.sin(2*Math.PI*p.tailHz*t)*p.tailAmp,
   scarfAngle:Math.sin(t*3.1)*4+walkWeight*7,
   wingAngle:character==='tengu'?Math.sin(t*2)*3+gestureWeight*8:0,
   staffAngle:character==='wukong'?Math.sin(t*1.4)*3+gestureWeight*6:0}
 };
}
