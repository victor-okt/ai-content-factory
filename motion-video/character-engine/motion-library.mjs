/** Reusable motion clips for VO1995 chibi cutout rigs.
 * Angles are degrees; normalized times are 0..1. Layer names match rig-svg.mjs.
 * No camera transforms: every clip moves individual parts only.
 */
export const CLIPS = Object.freeze({
 idle: {duration:1.6,loop:true,tracks:{body:[[-2,0],[0,.5],[-2,1]],head:[[0,0],[2,.5],[0,1]],tail:[[-8,0],[8,.5],[-8,1]]}},
 blink: {duration:.22,loop:false,tracks:{eyeOpen:[[1,0],[0,.4],[0,.6],[1,1]]}},
 talk: {duration:.45,loop:true,tracks:{mouthOpen:[[0,0],[1,.3],[.2,.6],[.8,.85],[0,1]],head:[[0,0],[2,.5],[0,1]]}},
 look: {duration:.65,loop:false,tracks:{head:[[0,0],[18,.65],[15,1]],eyesX:[[0,0],[8,.6],[8,1]]}},
 surprise: {duration:.45,loop:false,tracks:{head:[[0,0],[-12,.35],[-6,1]],leftArm:[[0,0],[-45,.5],[-25,1]],rightArm:[[0,0],[40,.5],[20,1]],mouthOpen:[[0,0],[1,.25],[1,1]]}},
 point: {duration:.5,loop:false,tracks:{rightArm:[[0,0],[-75,.65],[-65,1]],head:[[0,0],[7,1]]}},
 wave: {duration:.85,loop:true,tracks:{rightArm:[[-40,0],[-80,.25],[-35,.5],[-80,.75],[-40,1]]}},
 walk: {duration:.72,loop:true,tracks:{leftLeg:[[-24,0],[24,.5],[-24,1]],rightLeg:[[24,0],[-24,.5],[24,1]],leftArm:[[16,0],[-16,.5],[16,1]],rightArm:[[-16,0],[16,.5],[-16,1]],bodyY:[[0,0],[-7,.25],[0,.5],[-7,.75],[0,1]]}},
 run: {duration:.46,loop:true,tracks:{leftLeg:[[-42,0],[42,.5],[-42,1]],rightLeg:[[42,0],[-42,.5],[42,1]],leftArm:[[28,0],[-28,.5],[28,1]],rightArm:[[-28,0],[28,.5],[-28,1]],bodyY:[[0,0],[-14,.25],[0,.5],[-14,.75],[0,1]]}},
 reach: {duration:.65,loop:false,tracks:{rightArm:[[0,0],[-75,.7],[-65,1]],head:[[0,0],[12,.8],[10,1]]}},
 flinch: {duration:.36,loop:false,tracks:{head:[[0,0],[-15,.3],[0,1]],leftArm:[[0,0],[35,.3],[0,1]],rightArm:[[0,0],[-35,.3],[0,1]]}},
 umbrellaOpen: {duration:.5,loop:false,tracks:{umbrellaHinge:[[0,0],[1,.8],[1,1]]}},
 umbrellaClose: {duration:.3,loop:false,tracks:{umbrellaHinge:[[1,0],[0,.6],[0,1]]}},
 tenguFlap: {duration:.7,loop:true,tracks:{leftWing:[[-20,0],[35,.5],[-20,1]],rightWing:[[20,0],[-35,.5],[20,1]]}},
 wukongStaff: {duration:.75,loop:false,tracks:{staff:[[0,0],[-100,.5],[-60,1]],rightArm:[[0,0],[-65,.5],[-45,1]]}}
});
export function sampleClip(name,seconds){
 const clip=CLIPS[name];if(!clip)throw Error('Unknown clip: '+name);
 if(!Number.isFinite(seconds)||seconds<0)throw Error('Invalid time');
 const phase=clip.loop?(seconds/clip.duration)%1:Math.min(1,seconds/clip.duration);
 const out={};
 for(const [part,keys] of Object.entries(clip.tracks)){
  let i=1;while(i<keys.length-1&&keys[i][1]<phase)i++;
  const [a,at]=keys[i-1], [b,bt]=keys[i];
  const u=(phase-at)/(bt-at);
  const smooth=u*u*(3-2*u);
  out[part]=+(a+(b-a)*smooth).toFixed(3);
 }
 return out;
}
