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
