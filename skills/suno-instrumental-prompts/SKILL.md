---
name: suno-instrumental-prompts
description: Create compact, production-focused, directly pasteable instrumental prompts for Suno's Styles field. Use for scene scores, devotional music, emotional or tragic cues, destructive action, epic mythology, character themes, lullabies without lyrics, ambient underscore, and revisions such as grander, faster, darker, more chaotic, or more instrument-forward. Translate narrative emotion into tempo, musical structure, instrumentation, dynamics, texture, mix, and exclusions, normally within 800 characters.
---

# Suno Instrumental Prompts

Create one finished Suno Styles-field prompt, not an explanation of the music.

## Match work to task size

Apply this routing before the full workflow; it governs workflow breadth, not correctness or required checks.

- For a small prompt rewrite, dialogue change, parameter tweak or single-shot repair, use already loaded context and approved profiles/locks. Return the requested result directly after checking the changed fields and affected continuity. Do not restart scene breakdown, master design, whole-project mapping or full-history retrieval.
- For a scoped scene, location or asset task, read only the relevant source spans, references and active lessons. Reuse verified mappings, approvals and project manifests from the current context. Re-read when changed, stale, ambiguous or required by the source's freshness rules.
- For a full breakdown, new connected world, broad continuity audit or skill-learning request, perform the complete relevant workflow. Do not reduce requested coverage to make the answer faster.
- Search history only when missing prior context materially affects this result; do not repeat a search/read that already answered the same unchanged question. Browse when required for current facts or research, not for routine wording edits based on supplied facts.
- Do not invoke subagents or specialist handoffs by default for micro-edits. Delegate only when authorized and useful. Keep role checks proportional; do not turn every role into a separate tool call or ceremony.
- Batch independent reads/checks when practical. After required checks pass, avoid redundant tests/reviews unless new evidence warrants them. Inspect actual media for claims about visible outputs; never replace necessary verification with an unsupported success claim.
- Ask only for essential missing information or an actual required approval; reuse established permissions and locks. For prompt-only requests keep the result compact and copy-ready. Persist requested skill changes through Git, with only affected paths staged. Never promise a fixed response time or background completion that has not occurred.


## Build the cue

1. Extract the scene's emotional starting state, escalation, climax, and ending state. Infer sensible missing details without asking unless a choice would fundamentally change the cue.
2. Choose a precise BPM or tight BPM range. Add meter, rhythmic cycle, key, mode, or raga only when musically useful.
3. Select a lead voice, supporting instruments, percussion, bass foundation, and atmospheric textures that serve the setting and character.
4. Express the cue as a playable arc: opening texture, development, transitions or dropouts, climax, and resolution or intentional non-resolution.
5. Specify dynamics, articulation, spatial character, stereo image, low-end weight, reverb, and mix emphasis where they materially affect the result.
6. End with concise exclusions. For instrumental requests, always enforce `instrumental only, no vocals, no lyrics, no spoken word, no choir` unless the user explicitly allows one of them.

## Adapt by cue type

- **Devotional:** privilege culturally coherent melodic language and organic instruments; balance reverence, innocence, warmth, or divine scale according to the scene.
- **Emotional or tragic:** favor expressive phrasing, restraint, breathing space, evolving harmony, and a clear emotional peak; use unresolved cadences when grief or danger continues.
- **Destructive:** use propulsive percussion, aggressive ostinatos, sharp impacts, accelerating layers, controlled dropouts, dense low end, and relentless escalation.
- **Epic:** increase scale through orchestration, register, rhythmic mass, stereo width, and dynamic contrast rather than vague adjectives alone.
- **Character theme:** create a recognizable lead motif and timbral identity that reflect the character's nature, power, vulnerability, culture, and arc.

Combine categories when the scene demands it, such as devotional tragedy or sacred destructive rage.

## Output rules

- Return only one copy-ready prompt inside a single code block. Put nothing else in the code block.
- Normally keep the prompt at or below 800 characters, including spaces. Treat a user-specified limit as authoritative.
- Use compact English production vocabulary even when the request is in another language, while preserving exact Indian instrument, tala, and raga names.
- Prefer concrete musical instructions over story summary, metaphor, or promotional prose.
- Do not write lyrics, section labels, rationale, alternatives, hashtags, or generic filler unless requested.
- Do not imitate a living artist. Translate references into musical attributes instead.
- Preserve explicit must-use instruments, tempo, raga, mood, and exclusions. When revising, retain unaffected constraints and change only the requested dimensions.

Before answering, silently verify: paste-ready, instrumental constraint present, emotional arc audible in the structure, instrumentation coherent, dynamics and mix useful, exclusions concise, and character count compliant.

## 2 November 2026 Suno compatibility note

Suno's current release notes list v6/v6-wild/v6-mini and a Suno MCP beta. This helper still outputs one compact Styles-field instrumental prompt, normally within Manik's 800-character preference. Do not auto-run MCP, spend credits or expand the prompt merely because newer Suno routes exist. If execution is requested, verify current connector/account/model access first.
