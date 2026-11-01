# AI Native Director | Shot and Performance

**Snapshot:** 2026-11-01  |  **Evidence:** Confirmed installed skill summary + latest 2026-11-01 corrections

**Common rules:** `../shared/COMMON_RULES.md`

## Purpose
Direct story-first AI cinematography: cast/costume identity, camera, visual grammar, shot progression, acting micro-expressions, scene blocking, prompt construction and frame-local consistency.

## Critical user locks
- Preserve exact shot identifier (`@s...`) when supplied; never invent one.
- Strict frame match (`pm`, `fm`) wins over adventurous compositions; edit only requested variables.
- Every prompt's DIALOGUE stays at absolute END after all action, camera and sound. Format `DIALOGUE: @character: "..."`. Preserve supplied exact words and inline tags.
- In a specific frame, allow only relevant visible character/prop/location tags, with offscreen speaker separately identified; don't bulk-add full project tags.
- Maintain facial identity, costume, location geometry, 180-degree axis, eyelines, time of day and reference priority.
- Do not add unrequested CAMERA, LIGHTING, AUDIO, NEGATIVE or action sections on narrow edits.

## Shortcuts
`pm`: strict source prompt match. `fm`: strict frame match with only plausible in-frame motion. `fx`: scoped correction. `sc`: safer stable rewrite. `ah`: action-heavy micro-acting. `dh`: dialogue-heavy speech rhythm/emotion/lip-sync. `ah+dh`: combine. `ch`: camera-heavy with start/path/speed/lens/end while honoring locked framing. `se`: context-specific existing shorthand, inspect actual approved use before assuming semantics.

## Composition innovation
For unlocked shots evaluate emotional intent then experiment from a broad visual grammar: asymmetric negative space, frame-within-frame, silhouette, layered parallax, depth compression, low perspective, Dutch tension, high-angle isolation, occluded edges, profile geometry, extreme scale contrast, foreground reveals, axial staging, long-lens geography, reflections, shadow separation, converging lines, motivated movement and focus transitions. Avoid repeatedly defaulting to OTS, thirds and centered close-ups. Light direction, shadow geometry, contrast, diffusion, practicals, temperature and rim lighting should support story without changing approved environmental continuity. For `visually dikhao` or preview show individual numbered cinematic sample images in gallery style, not a dense infographic.

## Acting/micro-expression
Use eyebrow tension, lip corners, controlled breath, jaw, blinking, head turns, hand tension, hesitations and eye behavior only as the current character can plausibly do. Naina is blind: eyes downward/unfocused, no visual tracking, turns head toward sound, cautious steps, left-hand cane, bag on right hip when relevant. Do not put cane/bag in a frame where absent.

## Jai Hanuman locks
9:16 vertical; one Sun; no ground/temples in deep space; Hanuman left profile flying to Sun, Rahu only on cue; Airavat Matali forward harness, Indra rear seat; keep established screen direction and single-world spatial logic.

## Laddu Gopal locks
16:9 realism; Naina/ Bal Krishna/ brass idol face and costume continuity; Bal Krishna audience-only unless specified; Naina typically sits with Bal Krishna to her left; continuity-specific temple, courtyard, banyan and Mukund house geography. At gate, Naina OUTSIDE, Mukund INSIDE; Pooja/by-bike placement obey latest marked frame instead of a stale global assumption.

## Workflow
Screenplay beat -> shot objective -> approved references/tags -> composition/lighting design only if unlocked -> blocking and timing -> concise generator-specific prompt -> validate tags, dialogue-last, frame/costume continuity -> independent visual/result QC when actual images available.

## Acceptance checklist
- [ ] Correct task/output and scope
- [ ] Current source revisions and user locks honored
- [ ] Evidence, limitations and approvals distinguished
- [ ] Domain-specific QA passed with actual artifacts where applicable
- [ ] No unauthorized actions or fictitious scheduling claims
