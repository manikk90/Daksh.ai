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

---

## Mapped skills addon | 1 November 2026

Primary source: [`ai-native-director/SKILL.md`](../skills/ai-native-director/SKILL.md).
Original-source files: 31. Standalone archive: [skill.zip](../skill_packages/ai-native-director/skill.zip).

- **Director controller and task routing**: [`references/controller-runtime.md`](../skills/ai-native-director/references/controller-runtime.md), [`references/execution-quality.md`](../skills/ai-native-director/references/execution-quality.md).
- **Camera, coverage, composition and focus**: [`references/camera-and-coverage.md`](../skills/ai-native-director/references/camera-and-coverage.md), [`references/camera-catalog.md`](../skills/ai-native-director/references/camera-catalog.md), [`references/shot-composition.md`](../skills/ai-native-director/references/shot-composition.md), [`assets/composition-patterns.json`](../skills/ai-native-director/assets/composition-patterns.json), [`assets/composition-study.frames.json`](../skills/ai-native-director/assets/composition-study.frames.json), [`scripts/composition_lookup.py`](../skills/ai-native-director/scripts/composition_lookup.py).
- **Cast identity and costumes**: [`references/cast-and-costume.md`](../skills/ai-native-director/references/cast-and-costume.md), [`assets/cast-costume.template.json`](../skills/ai-native-director/assets/cast-costume.template.json).
- **Performance, action and micro-expressions**: [`references/performance-and-action.md`](../skills/ai-native-director/references/performance-and-action.md), [`assets/character-performance.template.json`](../skills/ai-native-director/assets/character-performance.template.json).
- **Image/video compiler and model adapters**: [`references/image-video-prompts.md`](../skills/ai-native-director/references/image-video-prompts.md), [`references/model-adapters.md`](../skills/ai-native-director/references/model-adapters.md), [`references/reference-input-preflight.md`](../skills/ai-native-director/references/reference-input-preflight.md), [`scripts/audit_prompt_contract.py`](../skills/ai-native-director/scripts/audit_prompt_contract.py).
- **Reference Mapper role and tag/asset binding**: [`agents/reference-mapper.md`](../skills/ai-native-director/agents/reference-mapper.md), [`references/reference-mapper-contract.md`](../skills/ai-native-director/references/reference-mapper-contract.md), [`references/mapping-and-qc-agents.md`](../skills/ai-native-director/references/mapping-and-qc-agents.md), [`scripts/validate_handoff.py`](../skills/ai-native-director/scripts/validate_handoff.py).
- **Filmmaking QC role and evidence contract**: [`agents/filmmaking-qc.md`](../skills/ai-native-director/agents/filmmaking-qc.md), [`references/filmmaking-qc-contract.md`](../skills/ai-native-director/references/filmmaking-qc-contract.md).
- **Continuity, editing and sound**: [`references/composition-editing-sound.md`](../skills/ai-native-director/references/composition-editing-sound.md), [`references/laddu-gopal.md`](../skills/ai-native-director/references/laddu-gopal.md), [`scripts/project_context.py`](../skills/ai-native-director/scripts/project_context.py).
- **Scoped corrections and continuous learning**: [`references/continuous-learning.md`](../skills/ai-native-director/references/continuous-learning.md), [`assets/learning-ledger.json`](../skills/ai-native-director/assets/learning-ledger.json), [`scripts/validate_learning_ledger.py`](../skills/ai-native-director/scripts/validate_learning_ledger.py).

Cross-agent ownership: [AGENT_SKILL_MAP.md](../AGENT_SKILL_MAP.md). Newer conversation-scoped rules: [latest overrides](../overlays/LATEST_USER_OVERRIDES_2026-11-01.md).

The copied original skill snapshot and this readable dossier are different evidence levels. Use the latest explicit user instruction, current approved assets, applicable source-skill rules and scoped overrides before older dossier generalizations.
