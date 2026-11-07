# VO1995 — Episode prototype: "Payung yang Takut Hujan" (production plan)
Status: SCRIPT / ACTION PLAN ONLY. No approved animation or narration render exists.

## Creative direction
Clean 2D chibi animation, Japanese woodblock color palette as a restrained influence, NOT manga panels, speech bubbles, or heavy textured posters. 9:16 compositions drawn natively for portrait. Kitsune keeps white fur, red markings, kasa hat, indigo wave kimono, crimson scarf, bells, lantern and curled tail. No new canonical redesign.

## Story (approx. 30–35 s)
**Hook 0–4 s:** Rain starts. Kitsune opens a tiny umbrella. The umbrella snaps shut and trembles.
**Setup 4–9 s:** Kitsune tries again. The umbrella hides behind his tail. Kitsune: "Lho, kamu takut hujan?"
**Escalation 9–17 s:** One drop falls. Umbrella panics and darts away; Kitsune runs after it, slips, then catches it before it hits a puddle.
**Turn 17–25 s:** Kitsune notices a soaked baby bird under the shrine. He places his straw hat over the bird instead.
**Payoff 25–33 s:** The umbrella opens by itself to shelter both of them. Kitsune: "Ternyata, berani itu bukan nggak takut." The bird chirps. A large drop hits Kitsune's nose; he sneezes. Umbrella flinches again. Cut on the joke.

## Required acting, not camera tricks
Shot 1: two separate arms lift umbrella; fingers grasp; umbrella hinges open and collapse.
Shot 2: Kitsune eye darts, head turns, ears twitch; mouth matches speech.
Shot 3: independent umbrella movement, real walk cycle, feet contact ground, body slip and recovery.
Shot 4: hand removes hat; bird visibly shivers and blinks.
Shot 5: umbrella hinge opens; Kitsune and bird react independently; mouth synced to line.
Camera locked except motivated hard cuts. No full-frame shake, Ken Burns, slideshow, or panning to simulate acting.

## Audio and subtitles
Voice: Indonesian warm conversational, one narrator and optional Kitsune dialogue. ElevenLabs is a candidate only; no paid API calls without approval. Use silent animatic during technical rig tests rather than fake music.
Captions: separate overlay, max two lines, roughly <=24 characters per line, high contrast, timed to actual words; reserve bottom 320 px of 1080x1920 portrait for safe area.
Do not bake dialogue into generated artwork.

## Go/no-go
1. Verify transparent layered character art and umbrella prop with correct pivots.
2. Render 5 seconds showing actual independent arm, head, umbrella, eye, mouth, tail movement; inspect full portrait framing.
3. Validate natural voice and timed word timestamps before integrating 30+ second story.
4. Reject any output that only shakes/zooms a static illustration. Do not claim final video until exported MP4 is inspected.
