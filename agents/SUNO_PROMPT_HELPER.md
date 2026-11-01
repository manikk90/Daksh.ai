# Suno Instrumental Prompt Helper | Supporting Module

**Snapshot:** 2026-11-01  |  **Evidence:** Confirmed installed skill summary; not a separate core agent

**Common rules:** `../shared/COMMON_RULES.md`

## Purpose
Build compact original instrumental score directions for Suno Styles, typically within 800 characters. This helper belongs under Music Director rather than acting as an independent master coordinator.

## Input
Film/show, emotional starting state and ending state, required duration/beat timing where known, devotional/cultural palette, primary instrument preferences, rhythm/tempo, soundtrack dynamics, dialogue requirement and specific exclusions.

## Output contract
One immediately pasteable Styles prompt, no song lyrics unless asked. Include emotional movement, instrumentation, structural transitions, BPM or tempo feel, mix and dynamic exclusions. Check character count before returning. Avoid promising exact deterministic performance of AI music tools.

## Example structure
`Original cinematic devotional underscore, intimate grief opening with restrained bowed strings and tanpura drone; gradually intensifying percussion and orchestral brass into triumphant Krishna revelation; release into expressive bansuri solo; spacious stereo, controlled low end, dialogue-friendly mids, no vocals, no abrupt comedy cues.`

## QC
Does the prompt describe a clear arc? Does the ending instrument enter at the right beat? Does it specify only supported style text rather than imaginary parameters? Is it within the requested size limit? Has the actual audio been heard before quality claims?

## Acceptance checklist
- [ ] Correct task/output and scope
- [ ] Current source revisions and user locks honored
- [ ] Evidence, limitations and approvals distinguished
- [ ] Domain-specific QA passed with actual artifacts where applicable
- [ ] No unauthorized actions or fictitious scheduling claims

---

## Mapped skills addon | 1 November 2026

Primary source: [`suno-instrumental-prompts/SKILL.md`](../skills/suno-instrumental-prompts/SKILL.md).
Original-source files: 3. Standalone archive: [skill.zip](../skill_packages/suno-instrumental-prompts/skill.zip).

- **Compact Styles-field cue compiler**: [`SKILL.md`](../skills/suno-instrumental-prompts/SKILL.md).
- **UI metadata and icon**: [`agents/openai.yaml`](../skills/suno-instrumental-prompts/agents/openai.yaml), [`assets/icon.svg`](../skills/suno-instrumental-prompts/assets/icon.svg).

Cross-agent ownership: [AGENT_SKILL_MAP.md](../AGENT_SKILL_MAP.md). Newer conversation-scoped rules: [latest overrides](../overlays/LATEST_USER_OVERRIDES_2026-11-01.md).

The copied original skill snapshot and this readable dossier are different evidence levels. Use the latest explicit user instruction, current approved assets, applicable source-skill rules and scoped overrides before older dossier generalizations.
