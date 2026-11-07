# Character animation engine — stage 1

This is a **motion-data engine**, NOT a complete character rig or finished video. It creates deterministic poses for three approved VO1995 mascots: Kitsune, Wukong, and Tengu.

## Run free local tests
```sh
node --test motion-video/character-engine/pose.test.mjs
```
Requires Node.js 18+; no packages, GPU, paid API, or credentials.

## API
```js
import {poseAt} from './pose.mjs';
const actions=[
 {type:'walk',start:0,end:2,fromX:0,toX:240},
 {type:'speak',start:2,end:4},
 {type:'gesture',start:2.3,end:3.1,hand:'right'}
];
const syllables=[{start:2.1,end:2.4,energy:.9},{start:2.5,end:2.8,energy:.7}];
const pose=poseAt('kitsune',2.6,actions,syllables);
```
The resulting pose includes world position, head turn, blink, mouth aperture, body motion, arms, legs and secondary motion. Wukong has staff motion; Tengu has wing motion.

## Essential limitations
- There are **no cutout PNG body-part layers** in this repo. Approved full illustrations cannot be treated as articulated meshes. Next step: extract/draw transparent separate layers from approved artwork, preserving canon, and map the pose channels to image transforms.
- Mouth aperture is syllable-timing approximation, **not true phoneme viseme recognition**.
- No speech synthesis, audio, rendered video, or Remotion integration has been validated by this module.
- Walking uses procedural joint rotations and path position; true foot planting/IK is not implemented. Do not claim foot sliding solved.

## Asset requirements per character
Transparent separate layers with documented pivots: torso, head, eyes open/closed, mouth closed/open/intermediate, upper/lower arms, legs, accessories, tail (Kitsune/Wukong), wings/fan (Tengu), scarf. Reference approved original images in Library. Never redraw permanent facial markings arbitrarily.

## QA gate
Before declaring animated footage complete: check exact design identity, blinking, mouth alignment to actual voice, coherent gestures, walking foot contact, audio licensing, repeatable MP4 render and frame-by-frame review.
