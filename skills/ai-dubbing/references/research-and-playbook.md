# Ai Dubbing — ElevenLabs research and regional production playbook

Checked: 19 October 2026, Asia/Kolkata. For Manik Prajapati / Mohit Kumar. Agent: **Ai Dubbing**.

## Contents

1. Model snapshot
2. Voice/audio modules
3. Regional support
4. Regional techniques
5. Performance direction
6. Voice bible and pronunciation
7. Episode pipeline
8. Timing and sync
9. QC and delivery
10. API execution
11. Experiments
12. Learning and opportunities
13. Sources and conflicts
14. Automatic fast routing
15. Workflow audit
16. Continuous learning
17. Review on 22 October 2026

**Evidence:** Documented = official source states it. Recommended = production design authored here. Hypothesis = needs an audio experiment. User lock = explicit preference. No audio was generated or auditioned during this research; no voice was trained. Support does not establish production quality in a specific dialect.

## 1. Model snapshot

| Component | Documented state | Recommended use |
|---|---|---|
| Eleven v4, `eleven_v4` | Flagship expressive TTS, 90+ languages, improved voice accuracy. [S1, S3] | Film dialogue audition candidate; compare existing approved cast before migration. |
| v4 Turbo, `eleven_v4_turbo` | Real-time variant; vendor cites about 100 ms median inference / 150 ms first speech. [S2] | Interactive rehearsal/voice agents; latency is not an acting-quality score. |
| v4 controls | Stability and Similarity; an additional Clone Strength UI slider for v4 Professional Voice Clones. No Speed/Style sliders or SSML. [S4, S23] | Preserve approved settings; keep UI Clone Strength distinct from Dubbing v2 cloning strength and API `use_pvc_as_ivc`. |
| Accent handling | Same-language reference preserves accent; cross-language v4 aims at native target speech. [S1] | Audition regional authenticity separately from voice resemblance. |
| Professional Voice Clones | Current v4 page states full support (rechecked 22 October); this is public documentation, not account verification. [S23] | Inspect the real voice/model readiness; compare to approved identity before migration. |
| v3 | Older expressive route; v4 recommended in current guide. [S4] | Retain approved takes as migration baseline. |
| Dubbing v2 | Separate automatic translation/dubbing system. [S5] | Source-media localization, not another name for v4. |
| Dubbing Studio | Legacy v1 editor in maintenance mode. [S6] | Maintain existing projects; avoid relying on future feature development. |

This Ai Dubbing agent is a skill-based dubbing workflow. ElevenAgents is a different conversational product; no bot was deployed there.

## 2. Voice/audio modules

These modules organize work; they are not newly trained voice models.

| Module | Purpose | Acceptance condition |
|---|---|---|
| Casting / Voice Library | Compare voices against character brief. | Real selected voice IDs and approved takes, never invented IDs. |
| Voice Design | Prompt-based voice exploration; specify language, age, timbre and delivery. [S7] | Audition intended regional dialogue, not generic English. |
| Instant Voice Clone | Quick authorized prototype; guide recommends about 1–2 minutes of clear consistent speech. [S8] | Clean source, consent and a comparison take. |
| Professional Voice Clone | Verified, longer-term voice asset using substantial recorded speech. [S9] | Satisfy ownership/verification workflow and actual model readiness; no promised training time. |
| Voice Remixing | Create variants of eligible voices by changing attributes. [S10] | Preserve original; higher strength can change identity. Native-check regional variants. |
| v4 TTS | Author individual character cues. | Word accuracy, acting, identity and timing pass. |
| Text to Dialogue | Exchanges with per-turn text and voice IDs. [S11] | Correct role mapping; do not assume isolated stems. |
| Dubbing v2 | Translate media while retaining speaker performance. [S5] | Target support, transcript, names and naturalness pass. |
| Voice Changer | Transfer guide performance into another voice; documented 29-language route includes Hindi. [S12] | It changes voice, not language; broader v4 support does not transfer to STS. |
| Voice Isolator | Extract speech from noisy recordings. [S13] | Compare original for lost breaths, damaged cries and softened consonants. |
| Scribe | Source transcription, speaker labels and timing. [S14] | Manual review of names, chants and regional words. |
| Forced Alignment | Time-align supplied audio and transcript. [S15] | Not proof every supplied word was pronounced correctly. |
| Mix / subtitle handoff | Assemble accepted cues with picture and M&E. | NLE/DAW verification and actual delivery spec. |

Recommended asset ladder: approved cast → eligible library audition → designed audition → authorized IVC prototype → verified PVC where justified. Avoid replacing a working cast simply because a new feature exists.

## 3. Regional support

v4 TTS lists Hindi, Marathi, Bengali and Gujarati. [S3] The inspected English Dubbing v2 tables list Hindi, Marathi and Gujarati, but omit Bengali; they place Bengali under v1. Some search snippets/localized results disagree, so Bengali v2 needs actual selector/API confirmation. [S16, S17]

| Release target | Authored-speech route | Media dubbing route | Local review focus |
|---|---|---|---|
| Hindi | v4, native script. | v2 `hi` documented. | Names, Sanskrit vocabulary, natural register. |
| Marathi | v4, Marathi script. | v2 `mr` documented. | ळ, dental/retroflex sounds, respect and idiom. |
| Bengali | v4, Bengali script. | v2 unresolved; verify or choose v1/approved TTS fallback. | Spoken vowels, aspiration, names, natural rhythm. |
| Gujarati | v4, Gujarati script. | v2 `gu` documented. | Nasalization, vowel length, address and rhythm. |
| Haryanvi | Separately listed native support not found. | No confirmed automatic target. | Native grammar, local phrase groups, appropriate lehja. |
| Rajasthani | Separately listed native support not found. | No confirmed automatic target. | First lock intended variety; do not silently substitute Marwari. |
| Bhojpuri | Separately listed native support not found. | No confirmed automatic target. | Grammar and respect levels; avoid Hindi with an accent. |

Absence from inspected lists does not prove the model cannot utter a regional phrase. It means target acceptance and quality cannot be promised. Do not invent accepted `hry`, `bgc`, `bho` or `raj` API values. Use only documented endpoint codes. Dubbing uses BCP-47 tags and restricts region-qualified values to its listed dialects. [S16]

For other Indian languages, re-check each route. Never transfer a platform-wide language count to STS, STT or an automatic dubbing endpoint.

## 4. Regional techniques

The techniques here are **recommendations/hypotheses**, not guaranteed vendor features.

### Three text layers

Keep immutable source dialogue, approved localized dialogue and TTS rendering text separate. Store a change map for spelling aliases or phonetic renderings. Subtitles use approved words without delivery tags. A word-locked cue must preserve every spoken token in order.

### Native script first, then a controlled comparison

Audition the language's normal script first. If a word fails, compare an approved Roman rendering or alternative target-script spelling. Mixed Roman spellings can cause unintended language switching. A winning rendering is specific to the voice/model, not a universal spelling rule.

### Grammar before accent

A regional tag cannot fix standard-Hindi grammar. Give the adapter relationships, era, intent and regional variety. Build a phrase bank from the project's accepted lines, recording speaker and situation. Avoid stuffing every sentence with stereotypical regional particles.

### Native guide performance

A local actor's short reading can establish rhythm, phrase grouping and emotion. Try authorized Voice Changer only within verified support. Hindi STS applied to Haryanvi/Bhojpuri/Rajasthani remains an uncertain experiment, not documented support. Retaining the native actor's recording is a valid quality fallback.

### One-variable auditions

Compare identical lines with one change: script representation, cue, voice variant or a permitted language override. Changing voice, wording and settings together prevents diagnosis. Have a native listener compare the results without candidate labels where feasible.

### Pronunciation islands and pickups

Create approved recordings for names such as Hanuman, Anjana, Kesari, Vayu, Narad, Brahma, Vajra and Naina. Keep the proper name stable unless an accepted local convention differs. Repair a word or phrase at a clean edit boundary rather than destroying an otherwise good emotional paragraph. Match intensity and room tone.

### Code switching

Record intended language and meaning for switched words. A whole-request language override can harm another part of a mixed line; compare with and without it only where the endpoint supports the option. Do not translate names or invocations automatically.

### Breath and regional rhythm

Get a native reader's phrase divisions. Preserve meaningful repetition such as “देखो... देखो...”. Generate in breath/performance units with adjacent context, avoiding random sentence splits. Authentic rhythm matters as much as individual phonemes.

### Avoid caricature

“Strong accent” is not a quality target. Check whether native listeners believe the character belongs to the intended region and social register. A non-speaker's preference cannot certify dialect accuracy.

## 5. Performance direction

Documented: v4 audio tags are natural-language square-bracket cues, not a fixed enum. They can shift delivery at meaningful boundaries. [S18] Some cues can be interpreted as sound effects; precise vocal descriptions help. v4 supports slash-wrapped IPA, still requiring testing with the selected voice. [S19]

**User locks:** only tags + dialogue for line editing; English tags; no narrator label; preserve word order and repetition; add no line without permission; use current regional lehja; later delivery corrections supersede earlier ones. Do not change simple words into literary synonyms merely because the story is mythological.

| Intention | Proposed cue, not audio-tested | Failure to check |
|---|---|---|
| Anjana, low grief | `[crying softly, low trembling voice]` | Sobs hiding consonants. |
| Maternal urgent plea | `[breathless, tearful pleading]` | Invented scream or added words. |
| Kesari crying | `[crying, voice trembling]` | Detached “zoned out” delivery after its removal. |
| Vayu calling during fall | `[shouting desperately, breathless]` | Distorted name or unwanted wind SFX. |
| Vayu restrained wrath | `[low voice, restrained fury]` | Villain caricature replacing paternal pain. |
| Narrator suspense | `[grave, measured voice]` | Overlong pauses weakening story rhythm. |
| Brahma authority | `[calm, firm, compassionate]` | Overly weak/whispery delivery. |
| Krishna warmth | `[gently playful, warm voice]` | Adult sarcasm or cartoon pitch. |

For approved “फेर आँख क्यूँ ना खोल रह्या मेरा पुत्र”:

> [crying softly, low trembling voice] फेर आँख क्यूँ ना खोल रह्या... मेरा पुत्र?

Do not move “मेरा पुत्र” earlier or add “अपणी माँ नै देख”. Do not replace माँ with मैया, साँस with श्वास or बेटा with पुत्र without request. Fast crying and low-volume grief are separate directions; do not make all sadness slow or all distress loud.

Keep environmental effects separate from clean dialogue by default. Integrated events can complicate multilingual stem mixing. Do not promise millisecond pauses from tags, or use SSML breaks on v4.

## 6. Voice bible and pronunciation

Recommended character direction below is an audition brief, not canon or finalized casting.

| Character | Distinct baseline | Emotional movement |
|---|---|---|
| Narrator | Clear, grounded, story-conscious; episode-defined language. | Restraint → suspense → impact. |
| Anjana | Warm maternal specificity. | Shock → pleading → grief → hope. |
| Kesari | Grounded paternal texture. | Disbelief → recognition → grief. |
| Vayu | Breath-supported authority, recognizable parent. | Panic → grief → fury → release. |
| Hanuman | Approved childlike voice, clear and spontaneous. | Vulnerability at revival; later playfulness. |
| Narad | Clear messenger urgency without comic default. | Alert → solemn witness. |
| Brahma | Measured weight and compassionate decision. | Deliberation → resolution. |
| Vishnu/Mahesh/Indra/Yama | Separate texture, cadence and casting for each. | Respect each scene's motive. |
| Naina | Age-appropriate gentleness and sincere questions. | Innocence → concern → trust. |
| Bal Krishna | Warm playfulness and composure. | Teasing affection → reassurance. |

Store project, character, language/variety, real voice ID, model, casting version, age impression, timbre, cadence, register, relationships, allowed deviations, pronunciation version, accepted takes and review status. Unknown IDs remain null. Compare after model upgrades before replacing identity.

Repair order: transcription → native spelling → context/segmentation → supported dictionary/alias route → reliable reference-derived v4 IPA experiment → guide/pickup. Never guess precise IPA for unfamiliar words. Keep IPA/alias forms out of subtitles and frozen scripts.

Keep clone reference audio consistent in recording and baseline style. Keep expressive benchmark clips as a separate evaluation collection. Current v4 model guidance recommends a single speaking style in training audio. [S1] Do not combine every shout/whisper/cry demo into clone training by default.

## 7. Episode pipeline

Recommended for Jai Hanuman's Marathi, Haryanvi, Rajasthani, Bengali, Bhojpuri and Gujarati releases:

1. Freeze picture and approved source script. Assign scene/cue IDs and language/register by character.
2. Inspect source audio and correct speaker/transcript mapping, names and repeated cries.
3. Adapt all six versions from the same approved source, not through another translated dub. Keep intent and duration changes traceable.
4. Approve native phrase banks, lexicon and per-language voice maps.
5. Pilot one scene containing quiet grief, crying, narration and energetic speech before episode generation.
6. Generate cues using route-specific support. Supported Dubbing API targets can share one source project and have independent statuses. [S20] Unsupported regional targets cannot be assumed available.
7. Measure duration, check omissions and overlaps, and regenerate only affected cues.
8. Obtain native/acting review; compare to character anchor takes.
9. Mix with original M&E stems where available; remove double source speech and retain original picture resolution.
10. Deliver language masters, clean subtitles, manifest and unresolved pickup list. API completion alone is not editorial approval.

For Laddu Gopal retain TV pacing and intimate village characters; do not import Jai Hanuman's epic declamation.

## 8. Timing and sync

Measure rendered audio; word counts only estimate. Store start/end, actual duration, allowed overhang, entry/exit breaths and picture priority. Use project-defined tolerance, not a universal pass threshold.

Repair order: correct cue boundaries/unintended silence → same words with better pace → authorized localized compression → authorized picture adjustment → modest post processing after listening. Preserve grief breaths and hesitation. A word lock overrides automatic compression; report the unresolved timing conflict.

Dubbing timing preservation is not lip sync. Official docs say lip sync is outside Dubbing, with third-party options in other surfaces. [S6] Alignment supplies timestamps, not animated mouth changes. Never certify mouth sync from text/waveform alone.

Map breaths and emphasis to approved shot actions. A visible tightly closed mouth may limit a generated inhalation; a reaction shot may offer flexibility if edits are authorized. Do not invent blocking or new dialogue to force a fit.

## 9. QC and delivery

| Gate | Acceptance | Evidence |
|---|---|---|
| Text | No unauthorized additions, omissions, changed names or reordering. | Token comparison and listening; localized text compares to its own approval. |
| Region | Correct variety, grammar, address, rhythm and pronunciation. | Native reviewer. |
| Identity | Same character across cues and releases. | Anchor takes; voice ID alone insufficient. |
| Acting | Correct intention, intelligible cries, believable relationship. | Director/native acting review. |
| Sync | Entry, exit and overlap fit picture. | Actual audio in NLE. |
| Technical | No clipping, clicks, truncation, leakage or unintended sounds. | Meters + listening. |
| Delivery | Correct versions and requested mix specification. | Manifest/export check. |

ASR flags discrepancies; it cannot certify pronunciation or authenticity. Keep raw and normalized transcripts separate. Do not let an average score hide a missing word.

Suggested filename: `JH_E##_SC##_CUE##_CHAR_LANG_VOICEVER_TAKE##.wav`. Retain measured sample rate/bit depth. Conform once to project standards; upsampling does not restore detail. Use actual delivery loudness requirements rather than imposing a generic social-video target.

Dubbing v2 supplies lossless audio; its video is a preview and multichannel fidelity is not guaranteed. Use accepted audio with the original picture master. [S6] Keep dialogue, music/effects, clean subtitles and pickup history separate where available.

## 10. API execution

No ElevenLabs connection or key was supplied for this work. Preparation and deterministic cue QC are usable offline. Generation needs authorized access, actual voice IDs and credits. Use secure credential mechanisms, never secrets pasted into chat or stored in manifests.

Create speech documents neighboring context, pronunciation dictionary locators and best-effort seeds; seed determinism is not guaranteed. [S21] The 28 September changelog adds Text to Dialogue continuity support. [S22]

**Text to Dialogue REST preflight (rechecked 22 October; baseline documentation, not a new launch):**

- Pin the approved `model_id` explicitly: the endpoint still defaults to `eleven_v3`. Use `eleven_v4` for approved v4 content requests; v4 Turbo is documented on the Text to Dialogue WebSocket route, not assumed interchangeable with REST. [S22, S24]
- The model/product's advertised 10,000-character capacity does not override this endpoint's reliability guidance: keep total `inputs[].text` at or below 2,000 characters, including tags, and at most 10 unique voice IDs. Longer payloads can end early in streams or fail validation. Split at performance boundaries without shortening approved words. This 2,000-character preflight is a conservative authored production policy based on the endpoint guidance, not a universal model maximum. [S24]
- `previous_text` and `future_text` each allow up to 100 characters; previous/next request-ID lists each allow up to 3 IDs. Previous IDs end with the nearest take; next IDs begin with the nearest take. Support varies by model. Verify the actual route before claiming continuity works. Do not insert descriptions into spoken dialogue. [S24]
- The optional `language_code` can be ignored for unsupported model/language combinations. Supplying it is not proof of dialect acceptance. Keep regional approval and capability evidence separate. Zero retention disables history features including request stitching and is Enterprise-only. [S24]
- Keep up to 3 pronunciation dictionary locators; seeds remain best effort. MP3 192 kbps requires Creator+; 44.1 kHz PCM/WAV requires Pro+ per this endpoint. Public plan rules do not establish the user's entitlement. [S24]

Use `python3 scripts/dialogue_request_qc.py PAYLOAD.json --output-format ACTUAL_FORMAT` on the real JSON body; pass the query output format separately. It checks the bounded subset above, not the complete provider schema or access. Continue using `cue_qc.py` for word locks and approvals.

**Effects and clean dialogue (12 October baseline, rechecked 22 October):** `audio_effects` is post-processing, separate from delivery tags. Keep it absent by default for clean multilingual dialogue. The UI effects surface is the Text to Speech tab; dialogue effects use the API. Reverb (`environment_id` with positive `send_level`) or nonzero `pan` produces stereo and is rejected for `pcm_*`, `ulaw_*` and `alaw_*`. Do not silently switch the export format; verify the requested format and plan. Catalog IDs require a live catalog check before use. [S24–S26]

When effects are intentionally used, record `audio_effects`, `output_format`, `api_endpoint` and relevant `request_options` on the cue (or in its already fingerprinted `generation_context`). The checker now includes these optional cue-level records in approval fingerprints; effects or format changes require fresh review. Absent optional records preserve existing fingerprint recipes. No production manifest is rewritten by this maintenance.

Recommended implementation modules:

- Capability probe: current model, voice, endpoint, target and plan access.
- Planner: validate approved cues and budget; prevent full-episode reruns for one change.
- Separate adapters: TTS, dialogue, dubbing and STS payloads remain distinct.
- Tracker: real request IDs and per-language status; bounded retry of retryable failures.
- Registry: approved text/model/voice/settings/take versions without secrets.
- Pickup queue: group failures by text, region, pronunciation, acting, identity or timing.
- Delivery builder: consume only approved takes, original picture and clean subtitle words.

Inspect endpoint schemas before coding. Do not infer model-specific support from a generic parameter list. Dubbing v2 API transcript editing/regeneration is documented as Enterprise-only, distinct from UI editing. [S5] Do not spend credits just to validate a manifest.

## 11. Experiments

All tests below are proposed, not completed audio findings.

| Test | Controlled comparison | Success condition |
|---|---|---|
| v3 → v4 | Same approved voice/words: quiet, crying and shouting. | Better acting/clarity without identity regression. |
| Grief cues | Sparse direction vs verbose tag stack. | Exact words, intelligible consonants, believable grief. |
| Regional script | Native vs approved Roman rendering. | Native preference and name accuracy. |
| Unsupported variety | Native performance vs explicitly labeled Hindi-route experiment. | Native authenticity pass or retain human performance. |
| IPA name | Baseline vs reference-derived IPA. | Correct name without odd pause or voice shift. |
| Guide transfer | Original guide vs STS within verified support. | Regional rhythm survives; cast identity matches. |
| Dubbing similarity | Default 7 vs one lower and one higher permitted setting. [S5] | Natural speech and acceptable resemblance. |
| Pickup continuity | Cue alone vs supported neighboring context. | Seamless entry/exit cadence. |
| Regional remix | Baseline vs low-strength eligible variant. | Local acceptance without identity drift. |
| Cleanup | Original vs isolated cry/whisper. | Less noise without lost voice detail. |

Use accepted scene lines: Anjana soft plea, Kesari recognition, Vayu call/vow, narrator suspense, Brahma authority and Hanuman “माता”, plus names and local idioms. These are test categories, not new canonical dialogue.

Start with two candidates per failed cue. Match playback level; hide take labels where practical. Collect separate 1–5 judgments for identity, region, pronunciation, acting and timing plus a plain-language reason. Record time/cost only when measured. Re-test a small accepted baseline on upgrades.

## 12. Learning and opportunities

Ledger fields: date, correction, project/character/language/model scope, evidence source, test conditions, actual take IDs, outcome and status. User corrections become `user_rule`; researched recipes remain `hypothesis`; actual reviewed comparisons can become `tested`. Model changes may require `needs_retest`.

Keep response speed through progressive loading. Research when requested or materially needed, not for every two-word delivery revision. At initial creation no recurring schedule existed; the historical three-day task and its replacement by the coordinated daily/Sunday cadence are recorded in section 16 and the installed learning-runtime state.

Potential workflow/product hypotheses for Manik:

1. Regional character voice bible with language-specific maps and native QA.
2. Human-guided regional ADR with assisted cleanup/pickups/voice transfer where supported.
3. Pickup preflight tool that catches text/timing/version mistakes before native review.
4. Release comparison bench to protect a series' voice identity through model upgrades.
5. Dubbing style packs built from approved character behavior, lexicons and phrase banks.
6. Real-time character rehearsal using Turbo; keep output noncanonical until approved.

These are production ideas, not verified market-size/revenue claims. Pilot internally before selling a capability.

## 13. Sources and conflicts

Official pages inspected on 19 October 2026:

- S1: [Eleven v4](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/eleven-v4)
- S2: [v4 and Turbo](https://elevenlabs.io/v4)
- S3: [Model / TTS language list](https://elevenlabs.io/docs/help-center/technical/what-models-do-you-offer-and-what-is-the-difference-between-them)
- S4: [TTS product guide](https://elevenlabs.io/docs/eleven-creative/playground/text-to-speech)
- S5: [Dubbing product guide](https://elevenlabs.io/docs/eleven-creative/products/dubbing)
- S6: [Dubbing Studio / exports / lip sync](https://elevenlabs.io/docs/eleven-creative/products/dubbing/dubbing-studio)
- S7: [Voice Design](https://elevenlabs.io/docs/eleven-creative/voices/voice-design/)
- S8: [Instant Voice Cloning](https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning/instant-voice-cloning)
- S9: [Professional Voice Cloning](https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning/professional-voice-cloning)
- S10: [Voice Remixing](https://elevenlabs.io/docs/overview/capabilities/voice-remixing)
- S11: [Text to Dialogue](https://elevenlabs.io/docs/overview/capabilities/text-to-dialogue)
- S12: [Voice Changer](https://elevenlabs.io/docs/overview/capabilities/voice-changer)
- S13: [Voice Isolator](https://elevenlabs.io/docs/overview/capabilities/voice-isolator)
- S14: [Scribe / transcription](https://elevenlabs.io/docs/overview/capabilities/speech-to-text)
- S15: [Forced Alignment](https://elevenlabs.io/docs/overview/capabilities/forced-alignment)
- S16: [Dubbing capabilities / languages](https://elevenlabs.io/docs/overview/capabilities/dubbing)
- S17: [Dubbing language help table](https://elevenlabs.io/docs/help-center/product/dubbing/which-languages-are-supported-in-dubbing)
- S18: [Audio Tags guide, updated 15 October](https://elevenlabs.io/blog/elevenlabs-audio-tags-list)
- S19: [Pronunciation and prompting](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)
- S20: [Multi-language projects](https://elevenlabs.io/docs/eleven-api/guides/how-to/dubbing/multiple-languages)
- S21: [Create speech endpoint](https://elevenlabs.io/docs/api-reference/text-to-speech/convert)
- S22: [28 September 2026 changelog](https://elevenlabs.io/docs/changelog/2026/9/28)

Retain these conflicts:

- Generic TTS FAQ says speed control covers all models; v4-specific text explicitly excludes Speed/Style. Prefer specific guidance and inspect actual selected surface.
- Older cloning guidance describes cross-language accent carryover; current v4 guidance describes native target behavior. Avoid a model-independent promise.
- Bengali appears in snippets/localized Dubbing results, but not inspected English v2 tables; it is present under v1. Keep TTS support distinct from v2 acceptance.
- PVC: v4 has a PVC-only Clone Strength control. The26October official change also documents numeric API `clone_strength` for v4-fine-tuned PVCs: TTS uses `voice_settings`, Text to Dialogue uses `settings`, and Edit/Get voice settings stores/returns it. Keep this endpoint-specific; it is not Dubbing v2's0–10 cloning strength. The dialogue endpoint deprecates `use_pvc_as_ivc`; do not transfer that deprecation to unrelated endpoints without evidence. Preserve approved settings and verify actual voice/account readiness. [S23,S24,S25]
- UI editing and Enterprise-only API editing are different access surfaces.

State at creation: skill instructions, agent metadata, workflow templates and offline preflight prepared. Voice auditions, paid dubs, clone training, native sign-off and ElevenAgents deployment remain unperformed.

### Operating Ai Dubbing

Invoke **Ai Dubbing** / `$ai-dubbing` with a line, scene or dubbing brief. Single-line requests return only English tags and dialogue. Full production requests can return a cue plan, casting brief, pronunciation map, regional adaptation, pickup list and delivery manifest. The installed skill includes a project manifest/voice-bible template, scoped learning ledger and offline preflight utility.

For sung invocations, chants and musical dialogue, keep a separate brief: spoken vs rhythmic chant vs melody, exact sacred text, meter, tempo and pronunciation. Do not certify a speech clone as a singing model. Preserve supplied chants verbatim and obtain relevant pronunciation review. Keep music generation and Suno scoring separate from dubbing unless requested; supply clean vocal and instrumental stems when available.


## 14. Automatic fast routing, tone and micro-expression update

Added 19 October 2026. Direct-line requests reuse active context, apply only the changed performance axis, perform one silent text-quality check and return one best-fit tagged line. Batch scenes share profiles; production/research requests load only relevant references. This reduces redundant work; no measured latency gain is claimed.

Tone is tracked separately from emotion, volume, pitch, pace and breath. Vocal micro-expressions include a slight voice catch, restrained tearfulness, audible smile and a moment of hesitation. Visible eye/brow/head actions are not TTS controls. Proposed cues remain untested until an actual voice audition.

Detailed implementation: `references/fast-performance.md` and `assets/performance-cues.json` in the installed skill. Existing word locks, regional rules and native/audio review remain in force.


## 15. Workflow audit and implemented repairs

Audit completed 19 October 2026. Two reproduced failures in the original preflight were an empty cue list passing and a string-valued word lock bypassing text protection. Out-of-range voice settings also passed. These were implementation gaps, not provider/model failures.

| Gap | Repair | Remaining real-world requirement |
|---|---|---|
| Empty cues / invalid lock types / unchecked numeric settings | Reject empty cues, enforce boolean lock and numeric ranges. | Actual script approval. |
| Old review retained after line/tone/voice/take change | Bind five review records to current cue/take fingerprints. | Real reviewers and evidence. |
| One correction could trigger unnecessary full rework | Scope pickups by cue, target language and real context dependencies. | Existing accepted takes must be available. |
| Picture changes not tracked precisely | Pin per-segment picture versions with whole-version fallback. | NLE mouth/timing review. |
| Timeline collisions missing | Flag unmarked same-language/same-track overlaps; record intentional overlap groups. | Actual performance/edit inspection. |
| Prompt-ready confused with delivery-ready | Separate script preparation, candidate audio and delivered master; draft/release metadata gates. | Listening, mix and release sign-off. |
| Audio identity only a filename | Verify selected file bytes against recorded SHA-256. | Audio decoding/quality still requires technical review. |
| Retrying without diagnosis or budget boundary | Define failure categories, targeted attempts, request-status check and checkpoint recovery. | Real connector/jobs/credits; no generator engine claimed. |
| Writer/Director/native reviewer/mixer handoffs informal | Add explicit intake, pronunciation/version and delivery fields. | Populate them from real project sources. |

Validation: 25 offline regression checks pass, including stale approval, changed bytes, Unicode word preservation, duplicate IDs, overlaps, context invalidation and draft/release separation. Independent usage trials inspect task behavior, not sound quality. The checker never creates approvals.

Full operational contract lives in `references/workflow-contract.md` within the installed skill. Every cue can carry separate text, native, acting, sync and technical review records. This conservative validation may require re-evaluation after changes, but does not imply every change needs a new recording.

Still missing for an end-to-end production proof: real approved cast IDs/anchor takes, actual regional native auditions, source/picture/M&E assets, authorized generation access, production mix checks and a complete pilot episode. No measured response-latency improvement or audio benchmark is asserted. Existing phrase banks and pronunciation examples must be populated from approved material rather than invented.


## 16. Coordinated daily learning and Sunday research

The individual three-day task registered on 19 October 2026 is historical. The user's 22 October instruction supersedes its cadence: use one existing Daksh coordinator for daily accessible recent-chat review after 23:00 Asia/Kolkata and relevant official ElevenLabs/primary research on Sunday at 23:00. Check `assets/learning-runtime.json` for observed confirmation and prior task metadata; authorization alone is not proof that the scheduler changed. The independent Friday Suno/ElevenLabs brief remains separate.

The installed `references/continuous-learning.md` defines evidence/adoption gates, bounded candidate selection, checkpointing, regression checks, rollback and a runtime-access fallback. `assets/learning-runtime.json` records the scheduler registration separately from completed research/save history. No scheduled execution or audio benchmark has happened merely because the task was created.

The task can save validated internal changes when its execution runtime exposes skill/file/Git persistence. If that access is absent, it must return a precise unapplied update packet rather than claim a file change. A later write-capable maintenance invocation revalidates accessible pending changes before applying them. Documented features, code-tested contracts, hypothetical performance techniques and audio-tested results retain separate evidence labels. No model-weight training, paid audio or silent production-cast changes are authorized by maintenance.


## 17. Review on 22 October 2026

First-run coverage: 15–22 October 2026, through this review; exact timestamps and persistence status live in `assets/learning-runtime.json`. No prior successful checkpoint existed. The latest visible official changelog was 12 October, so 28 September model/continuity and 12 October effects entries are **older baseline**, not launches within the review window. Undated documentation below is checked-date evidence; its publication date is unknown.

Historical22October adoption: (1) explicit-model/size/context REST preflight, (2) effects-format and review-fingerprint protection, (3) then-verified v4 PVC UI Clone Strength guidance. The26October documented API addition below supersedes the older UI-only restriction at its named endpoints. Preserve approved settings; neither documentation nor the vendor's suggested0% starting point is a new approved project setting or an audio-quality result.

## Scoped26October control correction, verified29October

The official26October changelog documents `clone_strength`0–1 for a Professional Voice Clone fine-tuned for the selected v4 model. Use the actual endpoint field: TTS `voice_settings.clone_strength`, Text to Dialogue `settings.clone_strength`; Edit/Get voice settings additionally supports a nullable0–1 field. Do not add it to generic Dubbing payloads or claim every voice/account can use it. The changelog, not an inferred nested-property rendering, establishes the TTS/dialogue addition. Text to Dialogue's `use_pvc_as_ivc` is deprecated; the TTS page still lists that flag separately. Do not silently migrate approved production settings. Cases: an eligible v4 PVC on the documented route may use an explicitly selected value; a non-PVC, non-v4 or unrelated dubbing request does not inherit the control. This is documentation/text validation only; no API call, cloning or listening test.

- S24: [26October2026 changelog](https://elevenlabs.io/docs/changelog/2026/10/26), dated26October, checked29October.
- S25: [Edit voice settings](https://elevenlabs.io/docs/api-reference/voices/settings/update), checked29October; contrast [Create speech](https://elevenlabs.io/docs/api-reference/text-to-speech/convert) and [Create dialogue](https://elevenlabs.io/docs/api-reference/text-to-dialogue/convert).

Rechecked Hindi/Marathi/Bengali/Gujarati TTS, v2 media-dubbing table omissions, STS's separate 29-language scope, pronunciation/SSML, voice identity and cloning, multi-speaker/context constraints, timing/subtitle/QC handoffs and interface/plan boundaries. Bengali v2 acceptance remains unresolved; Haryanvi/Rajasthani/Bhojpuri have no newly verified automatic target. No account access was inferred.

In-window reading: audio tags article updated 15 October and SSML explainer published 15 October confirm existing sparse-tag/no-v4-SSML rules; no duplicate rule adopted. Content-creator STT guide published 19 October / updated 20 October reinforces existing transcript/subtitle/native-review separation; no new product support inferred. Original AI4Bharat IndicF5 repository lists Hindi, Bengali, Gujarati and Marathi among 11 languages, but its visible revision history predates this window. Treat as an older research baseline, not an ElevenLabs route, certified regional replacement or inspected-audio result.

Accessible correction coverage: supplied conversation and the saved ledger/profiles only. Existing word/order/repetition locks, English tags, no narrator labels, language scopes and voice mappings remain. No inaccessible chats or reviewed takes were claimed. Performance profiles remain proposed, not audio-tested. No paid generation, upload, cloning/training or cast change occurred.

Sources added/rechecked 22 October:

- S23: [Eleven v4 — model, PVC, accent and controls](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/eleven-v4) — undated current docs.
- S24: [Create dialogue API](https://elevenlabs.io/docs/api-reference/text-to-dialogue/convert) — undated current endpoint contract.
- S25: [12 October changelog](https://elevenlabs.io/docs/changelog/2026/10/12) — older baseline, effects launch.
- S26: [TTS UI effects and controls](https://elevenlabs.io/docs/eleven-creative/playground/text-to-speech) — undated current UI guide.
- S27: [SSML explained](https://elevenlabs.io/blog/ssml-tags-explained) — published 15 October 2026.
- S28: [Content-creator STT guide](https://elevenlabs.io/blog/speech-to-text-for-content-creators) — published 19 / updated 20 October 2026.
- S29: [Original IndicF5 repository](https://github.com/AI4Bharat/IndicF5) — older baseline; no local model or audio run.

Regression results and rollback paths are recorded in the learning ledger/runtime. Software checks do not certify voice identity, dialect, tone, micro-expressions, pronunciation, sync or mix. Real takes and appropriate native/acting review remain pending.
