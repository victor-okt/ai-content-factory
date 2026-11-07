# VO1995 puppet preview — verified local output

A five-second 540x960 MP4 preview was generated locally on 2026-11-07 using Python, CairoSVG and FFmpeg, with no paid APIs. The actual preview file is provided in the chat, not stored in this repository.

## What moved independently
- Head: rotates toward the umbrella
- Eyes: blink
- Mouth: changes opening
- Arms: move with walking and gesture
- Legs: alternating walk cycle
- Tail: sways
- Umbrella: opens and closes independently

## Limitations
This uses **procedural simplified placeholder vector shapes**, not the approved Kitsune art or a true cutout of its original character illustration. The animation is visibly basic, contains no natural voice, no story, and is not a finished product. It demonstrates only the technical feasibility of independent 2D puppet movement. No camera shake, slideshow, or Ken Burns effect was used.

## Next work
1. Separate approved character artwork into transparent body-part layers.
2. Map real layer anchor/pivot coordinates to the motion library.
3. Test walking and reactions while preserving silhouette and costume.
4. Integrate ElevenLabs narration and timed subtitles only after animation passes visual review.
