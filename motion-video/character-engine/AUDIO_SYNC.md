# Audio-driven mouth timing (zero-cost)

`audio-sync.mjs` parses local PCM16 or IEEE float32 RIFF WAV and estimates mouth-open intervals from RMS audio frames. Output is compatible with `poseAt(character, t, actions, syllables)` in `pose.mjs`.

```js
import {readFileSync} from 'node:fs';
import {analyzeWav} from './audio-sync.mjs';
import {poseAt} from './pose.mjs';
const {duration,syllables}=analyzeWav(readFileSync('voice.wav'));
const pose=poseAt('kitsune',0.35,[{type:'speak',start:0,end:duration}],syllables);
console.log(pose.mouth.open);
```

Test: `node --test motion-video/character-engine/audio-sync.test.mjs`. Convert locally with FFmpeg: `ffmpeg -i narration.mp3 -ac 1 -ar 16000 -c:a pcm_s16le narration.wav`.

**Limitations:** This is amplitude-driven timing, not phoneme visemes or natural speech generation. Feed isolated voice audio, not music. Adjust threshold and gap to match recording. Tests synthesize WAV in memory; no actual narration or MP4 has been produced by this module. Next: approved character body-part cutouts and visual render integration.
