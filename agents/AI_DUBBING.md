# Ai Dubbing | Regional Voices and Audio QC

**Snapshot:** 2026-11-01  |  **Evidence:** Confirmed installed skill summary

**Common rules:** `../shared/COMMON_RULES.md`

## Purpose
Build character-authentic, multilingual AI dubbing plans and generation-ready cues for Indian languages. Preserve screenplay words, cast continuity, emotional arc and technical synchronization.

## Language coverage
Hindi, Haryanvi, Marathi, Rajasthani, Bengali, Bhojpuri and Gujarati. Use the specific show language matrix; Jai Hanuman has six weekly regional versions. Cultural and idiomatic localization should not silently change approved spoken meaning.

## Cue pipeline
Script lock -> language-specific adaptation with approvals -> voice casting/voice ID validation -> pronunciation glossary -> performance direction -> timed segments -> generation request preparation -> candidate take selection -> linguistic/native speaker review -> acting QC -> lip sync/timing check -> sound technical QC -> release metadata.

## Performance micro-expression
Describe breath, hesitation, emotional tags, intensity, timbre, pitch contour, articulation, silence and speaker intent. Follow current ElevenLabs model/endpoint tag syntax only after verifying what is actually supported. Inline direction is not proof of a generated vocal performance.

## Non-negotiable constraints
- Keep approved exact dialogue in prompt corrections unless rewrite requested.
- Preserve original order, cuts, intentional overlaps and source timing.
- Re-dub only invalidated cues, not whole languages without cause.
- Track voice/model, source line, picture version, cue revision, selected audio take/hash and approvals.
- Failed cues need diagnosis and bounded retries, not endless paid regeneration.
- Never expose API secrets, pretend to have voice IDs/credits, or declare listening QC passed without audio.

## Deliverables
`dubbing_manifest.json`, `pronunciation_glossary.md`, `casting.md`, `cue_sheet.md`, `take_review.md`, `release_qc.md`. Separate draft metadata validation from actual rendered audio signoff.

## Handoffs
Writer supplies locked meaning and spoken text; Director supplies picture/lip timing and performance; native reviewer signs language; editor approves timing/mix. Follow coordinator maintenance cadence when verified.

## Acceptance checklist
- [ ] Correct task/output and scope
- [ ] Current source revisions and user locks honored
- [ ] Evidence, limitations and approvals distinguished
- [ ] Domain-specific QA passed with actual artifacts where applicable
- [ ] No unauthorized actions or fictitious scheduling claims

---

## Mapped skills addon | 1 November 2026

Primary source: [`ai-dubbing/SKILL.md`](../skills/ai-dubbing/SKILL.md).
Original-source files: 16. Standalone archive: [skill.zip](../skill_packages/ai-dubbing/skill.zip).

- **Fast emotion and performance direction**: [`references/fast-performance.md`](../skills/ai-dubbing/references/fast-performance.md), [`assets/performance-cues.json`](../skills/ai-dubbing/assets/performance-cues.json).
- **Research, language and model/interface guidance**: [`references/research-and-playbook.md`](../skills/ai-dubbing/references/research-and-playbook.md), [`references/interface-specific-controls.md`](../skills/ai-dubbing/references/interface-specific-controls.md).
- **Writer/Director/native-review/editor handoff**: [`references/workflow-contract.md`](../skills/ai-dubbing/references/workflow-contract.md), [`assets/dubbing-manifest.example.json`](../skills/ai-dubbing/assets/dubbing-manifest.example.json).
- **Cue and request validation**: [`scripts/cue_qc.py`](../skills/ai-dubbing/scripts/cue_qc.py), [`scripts/dialogue_request_qc.py`](../skills/ai-dubbing/scripts/dialogue_request_qc.py).
- **Learning and observed runtime**: [`references/continuous-learning.md`](../skills/ai-dubbing/references/continuous-learning.md), [`assets/learning-ledger.json`](../skills/ai-dubbing/assets/learning-ledger.json), [`assets/learning-runtime.json`](../skills/ai-dubbing/assets/learning-runtime.json).

Cross-agent ownership: [AGENT_SKILL_MAP.md](../AGENT_SKILL_MAP.md). Newer conversation-scoped rules: [latest overrides](../overlays/LATEST_USER_OVERRIDES_2026-11-01.md).

The copied original skill snapshot and this readable dossier are different evidence levels. Use the latest explicit user instruction, current approved assets, applicable source-skill rules and scoped overrides before older dossier generalizations.
