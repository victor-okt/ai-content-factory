/** SVG cutout puppet adapter. No canonical character art included. */
import {poseAt} from './pose.mjs';
const f=n=>{if(!Number.isFinite(n))throw Error('non-finite transform');return +n.toFixed(3)};
export function renderSvg({character='kitsune',time=0,actions=[],syllables=[],layers={},width=540,height=960,diagnostic=true}={}){
 const p=poseAt(character,time,actions,syllables);
 if(!Number.isInteger(width)||width<64||width>4096||!Number.isInteger(height)||height<64||height>4096)throw Error('invalid dimensions');
 const keys=['tail','leftLeg','rightLeg','body','leftArm','rightArm','head','eyesOpen','eyesClosed','mouthClosed','mouthOpen','scarf','staff','leftWing','rightWing'];
 for(const key of Object.keys(layers))if(!keys.includes(key))throw Error('unknown layer '+key);
 const x=width/2+p.world.x,y=height*.56-p.body.bob-p.world.y;
 const group=(a,cx,cy,inner)=>'<g transform="rotate('+f(a)+' '+f(cx)+' '+f(cy)+')">'+inner+'</g>';
 const layer=(key,l,t,w,h)=>{
  const uri=layers[key];
  if(!uri)return diagnostic?'<rect x="'+f(l)+'" y="'+f(t)+'" width="'+w+'" height="'+h+'" fill="none" stroke="#9b5c4c" stroke-dasharray="6 6"/><text x="'+f(l+3)+'" y="'+f(t+16)+'" font-size="12" fill="#75443a">'+key+'</text>':'';
  if(typeof uri!=='string'||!/^data:image\/(png|webp);base64,[a-zA-Z0-9+/=]+$/.test(uri))throw Error('layer '+key+' must be embedded PNG/WebP data URI');
  return '<image href="'+uri+'" x="'+f(l)+'" y="'+f(t)+'" width="'+w+'" height="'+h+'"/>';
 };
 const mouth=p.mouth.open>.38?'mouthOpen':'mouthClosed',eyes=p.eyes.blink>.55?'eyesClosed':'eyesOpen';
 const parts=[
 group(p.secondary.tailAngle,x+75,y+50,layer('tail',x+55,y-35,145,170)),
 group(p.limbs.leftLeg,x-36,y+105,layer('leftLeg',x-61,y+102,56,155)),
 group(p.limbs.rightLeg,x+35,y+105,layer('rightLeg',x+8,y+102,56,155)),
 group(p.body.lean,x,y,layer('body',x-91,y-65,182,200)),
 group(p.limbs.leftArm,x-77,y-37,layer('leftArm',x-113,y-45,65,150)),
 group(p.limbs.rightArm,x+77,y-37,layer('rightArm',x+48,y-45,65,150)),
 group(p.head.turn+p.head.tilt,x,y-104,
  layer('head',x-100,y-210,200,174)+
  layer(eyes,x-64,y-146,128,42)+
  layer(mouth,x-31,y-96,62,38)),
 group(p.secondary.scarfAngle,x,y-55,layer('scarf',x-75,y-70,150,50)),
 ...(character==='wukong'?[group(p.secondary.staffAngle,x+85,y,layer('staff',x+80,y-200,30,360))]:[]),
 ...(character==='tengu'?[group(p.secondary.wingAngle,x-80,y,layer('leftWing',x-200,y-80,140,160)),group(-p.secondary.wingAngle,x+80,y,layer('rightWing',x+60,y-80,140,160))]:[])
 ];
 return '<svg xmlns="http://www.w3.org/2000/svg" width="'+width+'" height="'+height+'" viewBox="0 0 '+width+' '+height+'"><rect width="100%" height="100%" fill="#f5e8cd"/>'+parts.join('')+(diagnostic?'<text x="18" y="35" font-size="18" fill="#75443a">DIAGNOSTIC ONLY - '+character+' t='+f(time)+'</text>':'')+'</svg>';
}
