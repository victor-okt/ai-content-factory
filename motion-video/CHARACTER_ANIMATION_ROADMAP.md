# VO1995 Character Animation — Production Handoff (2026-11-07)

## Objective
Build genuinely acting, talking 2D ukiyo-e characters **Kitsune, Wukong, Tengu** for reusable story videos, not static images sliding around. No new paid APIs, subscriptions, or spending without creator approval. Make reasonable technical decisions autonomously. Save each meaningful change to this repository and report actual tested results, not unverified claims.

## Approved references
ChatGPT Library: `/Character Universe/Kitsune_Original_Approved.png` (canonical Kitsune) and `/Character Universe/Kitsune_Wukong_Tengu_Concept_Sheet.png` (approved trio). See `skills/character-universe/CHARACTER_BIBLE.md`. Do not redesign their identity. Existing six-pose Kitsune test demonstrated expressions, but not believable full-body acting, walking, or dialogue.

## Work order
1. Inspect existing repo and available build/runtime tools. Choose zero-cost 2D solution; prioritize layered cutout puppet rigging and mouth/eye animation. Do not treat frame interpolation alone as convincing animation.
2. Establish animation asset specification: transparent body parts, pivots, eye/mouth visemes, tail/cloth secondary motion, walk cycle, breathing, head turns, facial expression and hand gestures. Identify what approved sheets cannot supply and avoid pretending the parts already exist.
3. Implement a reusable deterministic character animation module with timed actions, poses, and viseme input; produce a minimal local renderable demonstration with **one character** before cloning to the other two.
4. Add separate animation presets for Wukong (staff, tail, energetic gestures) and Tengu (wings, fan, restrained expressions), while preserving canonical look.
5. Investigate and test free, locally executable natural Indonesian speech options. Record exact quality limits and install requirements. Do not substitute robotic eSpeak as production-ready.
6. Create a short **dialogue scene** with acting and audio only after character rig and speech pass acceptance tests.
7. Commit source, instructions, test fixtures, QA checklist, and progress logs. Never claim video rendered without verified output.

## Acceptance criteria
- Character visibly acts: blinks, looks around, speaks with timed mouth movement, changes facial expression, shifts body posture, performs a gesture, and has secondary motion (tail/wings/clothing).
- At least one character walks without sliding.
- Identity matches approved character reference.
- Dialogue is intelligible Indonesian, reasonably natural, and lip motion aligns with speech.
- MP4 export is repeatable and has sound; full 3-character scene is stretch goal after each individual test.
- Cost: Rp0 additional until approval.

## Current truth
- Character concepts approved and saved.
- Prior six-frame expression test is only a limited proof-of-concept.
- No validated three-character rig or natural Indonesian TTS integration yet.
- Closing tablet/chat does not by itself run a renderer or GitHub workflow. Progress requires an actual automation, server, or runner.

## Autonomous decisions
Prefer progress on source code and tests over repeated user questions. If blocked, record the blocker and proceed with independent subtasks. Do not change approved designs or incur costs.
