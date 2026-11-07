# Cutout puppet SVG adapter — stage 2
This is a **diagnostic renderer**, not finished art or video. It consumes existing `poseAt` data and selects transparent layers for eyes and mouth while rotating head, arms, legs, tail/scarf and Wukong staff/Tengu wings. Without actual approved transparent character body parts it displays labeled boxes, never a counterfeit version of the character.

Run `node --test motion-video/character-engine/rig-svg.test.mjs` (Node 18+, no dependencies).

Usage:
```js
import {readFileSync,writeFileSync} from 'node:fs';
import {renderSvg} from './rig-svg.mjs';
const uri=file=>'data:image/png;base64,'+readFileSync(file).toString('base64');
writeFileSync('frame.svg',renderSvg({character:'kitsune',time:.5,layers:{head:uri('head.png'),body:uri('body.png')},diagnostic:false}));
```

**Required next:** extract canonical approved Kitsune into transparent layers, adjust pivots to real geometry, and inspect visual identity. Image sources must be embedded PNG/WebP data URIs; no remote fetch. Mouth is amplitude-threshold open/closed, not phoneme-level visemes. Foot locking/IK and natural Indonesian voice remain unimplemented. No MP4 was rendered by this module.

Local preliminary test of the adapter with the existing `pose.mjs` motion engine: 7/7 passing in Node v22.16.0. The committed GitHub variant should also be tested independently before treating that claim as CI verification.
