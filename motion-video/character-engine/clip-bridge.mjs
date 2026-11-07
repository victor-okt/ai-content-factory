/** Convert reusable motion clips to the existing rig-svg pose action format.
 * Explicit mapping prevents confusing library keys (e.g. eyeOpen) with SVG layer names.
 * This file is a preparation step; it does not claim finished character rendering.
 */
import {sampleClip,CLIPS} from './motion-library.mjs';
export const RIG_CHANNELS=Object.freeze({
 head:'head',body:'body',tail:'tail',leftLeg:'leftLeg',rightLeg:'rightLeg',
 leftArm:'leftArm',rightArm:'rightArm',staff:'staff',leftWing:'leftWing',rightWing:'rightWing'
});
export function sampleRigChannels(name,seconds){
 const pose=sampleClip(name,seconds);
 const result={};
 for(const [key,value] of Object.entries(pose)){
  if(key in RIG_CHANNELS)result[key]=value;
 }
 return result;
}
export function clipManifest(){
 return Object.entries(CLIPS).map(([name,clip])=>({
  name,duration:clip.duration,loop:clip.loop,
  channels:Object.keys(clip.tracks),
  requiresProp: name.startsWith('umbrella')?'umbrella':null
 }));
}
