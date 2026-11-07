import test from 'node:test';
import assert from 'node:assert/strict';
import {poseAt,mouthAt,PROFILES} from './pose.mjs';
test('three characters have distinct secondary motion',()=>{
 const p=Object.keys(PROFILES).map(c=>poseAt(c,1.25));
 assert.equal(p.length,3);
 assert.notEqual(p[0].secondary.tailAngle,p[1].secondary.tailAngle);
});
test('walk moves body and alternating legs',()=>{
 const a=[{type:'walk',start:0,end:2,fromX:0,toX:240}];
 const p=poseAt('kitsune',1.2,a);
 assert.ok(p.world.x>0&&p.world.x<240);
 assert.equal(p.limbs.leftLeg,-p.limbs.rightLeg);
 assert.equal(poseAt('kitsune',3,a).world.x,240);
});
test('mouth follows syllable intervals',()=>{
 const s=[{start:.2,end:.45,energy:1}],a=[{type:'speak',start:0,end:1}];
 assert.equal(poseAt('kitsune',.1,a,s).mouth.open,0);
 assert.ok(poseAt('kitsune',.3,a,s).mouth.open>.9);
 assert.equal(poseAt('kitsune',.6,a,s).mouth.open,0);
 assert.equal(mouthAt(5,s),0);
});
test('deterministic bounded pose',()=>{
 const a=[{type:'walk',start:0,end:2,fromX:0,toX:100}];
 const p=poseAt('tengu',.8,a);
 assert.deepEqual(p,poseAt('tengu',.8,a));
 assert.ok(p.eyes.blink>=0&&p.eyes.blink<=1);
});
test('invalid inputs rejected',()=>{
 assert.throws(()=>poseAt('none',1));
 assert.throws(()=>poseAt('kitsune',-1));
});
