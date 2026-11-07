import test from 'node:test';import assert from 'node:assert/strict';import {CLIPS,sampleClip} from './motion-library.mjs';
test('all clips return finite independent part transforms',()=>{
 for(const [name,clip] of Object.entries(CLIPS)){
  assert.ok(clip.duration>0);
  for(const t of [0,clip.duration/4,clip.duration/2,clip.duration]){
   const pose=sampleClip(name,t);
   assert.ok(Object.keys(pose).length>0);
   for(const value of Object.values(pose))assert.ok(Number.isFinite(value));
  }
 }
});
test('walk moves opposite legs',()=>{const p=sampleClip('walk',0);assert.equal(p.leftLeg,-p.rightLeg)});
test('non-looping clips hold last pose',()=>assert.deepEqual(sampleClip('surprise',20),sampleClip('surprise',.45)));
test('unknown clip and invalid time are rejected',()=>{assert.throws(()=>sampleClip('missing',0));assert.throws(()=>sampleClip('walk',-1))});
