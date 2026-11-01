# Production contract, revision recovery and handoffs

## Contents

1. Scope and evidence
2. Intake and handoffs
3. States and review records
4. Revision handling and pickups
5. Generation recovery and cost
6. Release checks and unresolved work

## 1. Scope and evidence

Apply this reference to episode work and workflow audits, not routine line corrections. Use real project assets and actual approved voice mappings when available. Never fabricate an audio take, native review, source quotation, generation result, connector, measured speedup or saved project record.

Separate three outputs: a prepared prompt/script, generated candidate audio, and an approved delivered master. A well-formed script is not a completed dub. Offline metadata checks do not listen to pronunciation, acting or facial sync.

## 2. Intake and handoffs

Read only missing information that changes execution. Obtain project and source version, picture version or timing source, locked source words, target language/variety, speaker map, approved casting, desired deliverables and existing assets. Do not interrogate the user about context already supplied.

| Owner / input | Handoff fields | Rule |
|---|---|---|
| AI Writer | Exact source/localized words, intent, relationships, register, allowed adaptation | Do not silently rewrite to fit timing. |
| AI Native Director | Cue/shot IDs, picture segment version, visible mouth priority, breath/action cues, permitted editorial flexibility | Visual acting remains separate from TTS directions. |
| Ai Dubbing | Real voice map, pronunciation version, rendering text, tone arc, selected take, pickup reason | Preserve source words and character identity. |
| Native reviewer | Region/grammar/address/name assessment on actual take, reviewer and evidence reference | Do not substitute ASR for language judgment. |
| Editor / mixer | Accepted audio/stems, cue timing, picture version, subtitle text, delivery specification | Retain original-resolution picture and explicit unresolved items. |

Use current project profiles/shared files when they exist; otherwise use a minimal manifest. Do not claim the other agents were updated or contacted merely because a handoff format exists. For screenshot/OCR input, resolve uncertain words before calling the text approved. Preserve script vs performed differences in separate fields.

Keep shot-local visible character/prop/location bindings separate from audio source and speaker cues. A visual prompt uses only its current on-frame bindings, with no stale cast/props from the scene registry or previous shot. An explicitly requested offscreen line still retains its exact words and supplied speaker in the audio handoff; do not delete, relabel or force that speaker on screen. When checking a picture handoff, reject unrelated visual bindings without changing the approved speech cue. The dubbing cue's character/voice map describes who speaks, not who must appear in the frame.

Track pronunciation entries by project/language/variety/character when relevant. Store approved spelling, rendering alias, example recording, voice/model applicability, version and review status. Never let a newly guessed phonetic alias replace an approved name globally.

## 3. States and review records

Use these conceptual stages without adding a permission request at every transition:

`draft → source_locked → localized → pilot_checked → generated → reviewed → mixed → delivered`

Record `blocked` with a concrete reason, and `needs_pickup` with cue IDs and failure type. Existing user authorization permits ordinary reversible preparation and repairs. Ask only for a missing decision that cannot be inferred or for an action outside scope. Keep new writing separate when the line is locked.

Store five independent reviews on the selected audio: text, native language, acting, picture sync and technical audio. Each approved review needs a reviewer, evidence reference and the current cue fingerprint. All can be provided by one qualified reviewer if actually performed; never manufacture five approvals from one unchecked status flag.

Keep source/version records and take selection stable. `scripts/cue_qc.py` prints fingerprints but never grants approval. A changed word, tag, model, voice, setting, pronunciation version, cue timing, selected audio hash or relevant picture segment invalidates old review fingerprints. Also record actual endpoint, output format, audio effects and request options in cue-level `api_endpoint`, `output_format`, `audio_effects`, `request_options`, or in `generation_context`; these execution records are fingerprinted. Missing optional fields preserve the prior recipe. Do not retrofit or approve production records without real evidence. This conservative gate requests re-evaluation; it does not assert every review requires a new recording.

## 4. Revision handling and pickups

| Change | Minimum affected work |
|---|---|
| Pace/tone/micro-expression only | New rendering for that cue, candidate audio when authorized, then affected review. Keep words and region. |
| Correct a localized word | That language/cue and any generation that actually used it as neighboring context. |
| Character voice change | That character's affected language/version and its continuity benchmark. |
| Pronunciation lexicon change | Cues using the entry; retain prior accepted take until replacement passes. |
| Picture edit | Relevant segment timing/mouth-sync review; do not regenerate unchanged audio automatically. |
| Model upgrade | Pilot/regression comparison first; no whole-series migration by default. |
| Selected take bytes change | New file hash and review; never retain old approval on different audio. |

List real neighboring dependencies in `context_ref_ids` only when used by generation. A dependent fingerprint changes if the referenced rendering/voice/model/request changes. Do not mark every cue dependent on every other cue. Pin `picture_segment_version` for selective review; without it, a whole picture-version change conservatively affects all cues.

Use cue fingerprints to propose reuse and pickups. A matching recipe is not a guarantee of deterministic regeneration. Reuse only an available accepted take with a valid file hash and matching review records; never say an output was cached when there is no stored file.

Mark intentional overlaps with an explicit shared `overlap_group`. Check each language/track independently: cross-character overlaps on separate tracks may be intentional, while unmarked collisions on one dialogue track require inspection. Preserve interrupted words and trailing speech as approved; do not add sentence endings for convenience.

## 5. Generation recovery and cost

Prepare only when no authorized generation route exists. Before actual requests, verify model/voice access, accepted target and plan on that route. A regional experiment is not confirmed native support. A human-recording fallback uses its real actor/take mapping; do not put fake ElevenLabs API values in a manifest.

Before an authorized Text to Dialogue REST request, run `scripts/dialogue_request_qc.py` on its actual payload and query output format; section 10 of the playbook states endpoint-specific limits and plan constraints. This is a bounded offline contract check, not proof of language/context/account support. Preserve clean dialogue by omitting post-processing effects unless requested.

Use one approved baseline plus a small number of targeted alternatives. Default to at most two new candidate attempts for a failed cue in a repair cycle unless an approved project budget says otherwise. If both fail, diagnose or change route instead of an endless retry loop. Count paid attempts and record actual cost only when returned/measured.

Classify failures before retry:

- Wrong words/pronunciation: fix the rendering/lexicon within word locks; review it before another generation.
- Wrong affect or unwanted reaction: simplify/adjust one cue axis; do not change words to hide the problem.
- Wrong identity: restore voice/model/casting mapping and compare anchor take.
- Timing overflow: preserve intention; try delivery repair before authorized compression or picture adjustment.
- Provider transport error: inspect actual job/request status before resubmitting; ambiguous timeout may still have incurred a charge.
- Unsupported target/access: select a verified fallback or prepare the script; repeating the same rejected request cannot fix support.

Keep request IDs, attempt count, rejected-take reasons and the selected take. Persist checkpoints after meaningful batches when files are being produced; resume incomplete/changed cues instead of redoing the episode. Do not keep secrets or signed download URLs in durable manifests.

## 6. Release checks and unresolved work

Run `python3 scripts/cue_qc.py MANIFEST.json --phase draft` during preparation. Draft warnings can identify missing execution assets without blocking useful writing. Run `--phase release` for the final metadata gate; missing reviews, unsupported/unverified route, stale approval, missing audio/hash or unmarked overlaps must remain visible blockers.

The script validates nonempty cues, boolean word locks, exact spoken words, tag structure, supported recipe controls, numeric ranges, cue IDs, timing, same-track overlaps, declared context links, artifact hash and review freshness. It does not prove a model can generate a language, that a reviewer is qualified, that an evidence record is honest or that audio sounds good. `release_metadata_complete` means the records and file checks are complete, not a perceptual quality certificate.

Delivery record: project/source/picture versions; target language/variety; selected cue/take IDs; actual audio format; original-resolution picture; requested subtitle/mix variants; requested loudness specification; known exceptions. Keep performance tags and pronunciation aliases out of subtitles.

Remaining real-world requirements: approved voice IDs, source media, service access where generation is requested, native listening, actual acting/sync/mix assessment and a delivery specification. No software-only audit can supply these by assertion.
