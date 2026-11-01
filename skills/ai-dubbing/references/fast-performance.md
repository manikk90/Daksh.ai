# Fast response, tone and vocal micro-expression system

## Contents

1. Automatic routing
2. Tone axes and revision handling
3. Micro-expression to voice mapping
4. Character performance patterns
5. Quality and evidence

## 1. Automatic routing

Default to a direct line pass for a short dialogue or performance revision. Reuse active context and the latest exact line; avoid re-reading the playbook or searching official docs for a changed emotion. This is an automatic task-routing policy, not a background automation or a promise to change model inference speed.

Use batch processing when several cues share a cast/language. Resolve shared profiles once, then evaluate cue-specific changes. Do not flatten every cue into the same emotional template. Use the production path only when actual assets, new casting, regional acceptance, API capabilities or audio issues require it.

Maintain only useful context: project/character, approved line, language/variety, voice/model when known, baseline tone, pace, intensity, breath, last explicit override and word lock. Do not invent a persistent cache, a voice ID or a previous line if unavailable. Ask for the missing line only when context cannot recover it.

## 2. Tone axes and revision handling

| Axis | Examples | Preserve independently |
|---|---|---|
| Emotion | grief, relief, fear, delight, anger | The feeling can be hidden or restrained. |
| Tone/subtext | pleading, reassuring, accusatory, reverent, teasing | Intent toward listener, not merely pitch. |
| Volume | quiet, conversational, projected, shouted | Quiet anger and loud joy are valid. |
| Pitch/resonance | natural, lower register, light resonance | Do not recast a character for one line. |
| Pace | deliberate, flowing, hurried | Fast delivery need not be loud or comic. |
| Breath/texture | steady, breathless, fragile, gently trembling | Keep consonants intelligible. |
| Micro-expression | caught breath, slight voice catch, audible smile | Use sparingly at a meaningful beat. |

For an unqualified “low tone” in Manik's grief scenes, default to quiet, restrained delivery in the existing voice; do not automatically lower pitch. If pitch is explicitly requested, address it separately and audition identity.

Revision examples:

- “thoda fast”: keep current feeling, volume, words and dialect; shorten hesitations and change pacing direction.
- “rote hue”: keep wording and character; change vocal affect without appending sob syllables.
- “zone out hata do”: remove detachment, keep independently requested crying.
- “soft but angry”: use contained firmness; no contradiction needing clarification.
- “smile ho par hasi nahi”: direct a smile in the voice; omit laugh events.
- “chillate hue”: project/shout while retaining the character's motivation; do not add stretched written syllables to a locked name.

## 3. Micro-expression to voice mapping

These are authored cue hypotheses. They express audible direction, not facial-animation controls and not guaranteed features. A visual detail alone does not require an audible event.

| Contextual beat | Possible audible direction | Avoid |
|---|---|---|
| Tiny relieved smile | `[softly, relief warming the voice]` | Automatic laugh or giggle. |
| Holding back tears | `[quietly, voice catching with grief]` | Sobbing so much the line vanishes. |
| Speaking through tears | `[tearful, gently trembling voice]` | An inserted “हाय” or new appeal. |
| Sudden realization | `[startled, brief catch in the voice]` | Written gasp syllables added to dialogue. |
| Gathering courage | `[hesitant, then quietly firm]` | Random repetitions or stammering. |
| Fear concealed by authority | `[controlled voice, fear underneath]` | Switching to a villain persona. |
| Anger under restraint | `[low intensity, tightly controlled anger]` | Teeth-grinding or aggressive SFX. |
| Affectionate teasing | `[warm, lightly teasing voice]` | Adult sarcasm for a child character. |
| Hurt concealed by politeness | `[polite, voice faintly strained]` | Rewriting the line to explain hurt. |
| Reverent wonder | `[hushed, quietly awed]` | An automatic whisper or chant. |

Remove visual-only cues such as eyebrow raise, eye flick, blink, jaw movement or head tilt from TTS text. If the user requests storyboard/performance alignment, provide a separate optional Director handoff outside a tags-only line request.

Compile no more than the useful audible detail. A short line often needs only one bracketed cue. An emotional turn can justify a second cue. For a long passage, add cues at meaningful changes, not a rigid total cap. Avoid competing directions on the same words.

## 4. Character performance patterns

Reuse approved character identity before these optional patterns:

- **Anjana:** maternal warmth under distress; grief may produce a small voice catch and pleading softness. A louder cry requires explicit context or request.
- **Kesari:** grounded paternal voice; crying can weaken steadiness without making him detached. Do not keep a removed “zoned out” direction.
- **Vayu:** recognizable parental concern inside authority; urgent rescue calls and controlled wrath are different delivery states.
- **Narrator:** clear story rhythm; a restrained transition can carry more suspense than a tag on every word.
- **Naina:** sincere age-appropriate phrasing; wonder or fear need not become baby talk.
- **Bal Krishna:** warmth and playful composure; direct a slight smile in the voice rather than constant giggling.

Character presets are suggestions until actual casting/scene approval. Never override explicit user tone, dialect, speaker or volume with a preset.

## 5. Quality and evidence

Before output, run one silent check: exact words/order; correct language; latest override; tone/identity consistency; sparse vocal-only tags; no extra writing. A source/script change invalidates old rendering text. A delivery-only change does not require new source research.

For a delivery-only scene revision, retain its supplied speaker identity and approved Director locks: camera, seated/standing state, supported props and offscreen presence. Keep any visual-reference tag separate from its supplied speaker tag in a production handoff; tags are not dialogue or TTS controls. Revise only audible intent and do not silently restage the scene. This does not add labels or handoff prose to strict fast-line output.

For real audio, also inspect added breaths/interjections, spoken tags, drift, clarity and timing. A text-only check cannot establish these. If a cue adds unwanted reactions, simplify the tag first; do not rewrite approved dialogue to accommodate the artifact.

Official sources checked 19 October 2026:

- [Audio tag help](https://elevenlabs.io/docs/help-center/product/core-capabilities/text-to-speech/how-do-audio-tags-work-with-eleven-v3-and-v4): short square-bracket instructions guide emotions, delivery and human reactions.
- [Text to Dialogue](https://elevenlabs.io/docs/overview/capabilities/text-to-dialogue): per-turn voice selection remains separate from natural-language direction; results vary.
- [Prompting guidance](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices): precise vocal descriptions reduce confusion between delivery and sound effects.

No official fixed “micro-expression enum” is claimed. No audio benchmark or measured speedup was performed for this update. Proposed improvement mechanism: avoid redundant retrieval and repeated profile construction while preserving the text-quality gate.
