# Automatic prompt budgets and parameter selection

Load `assets/control-profiles.json` for the exact interface/mode. Determine whether a number is a documented provider hard limit, a user cap, or an editorial preference. The effective budget is the smallest applicable known cap; never present a preference as provider policy. Saved facts are dated snapshots; refresh official docs/actual UI when making current claims or executing an unknown/changed control.

## Compilation order

1. Lock platform, model, interface and deliverable; distinguish song, instrumental, plan and arrangement settings. Do not confuse a Music model with TTS.
2. Preserve hard creative requirements first: locked hook/lyrics, no voices, must-use instruments, duration/critical reveal, language and requested exclusions.
3. Allocate remaining prompt space to musical identity, groove, arc, expression and essential mix. Remove repeated adjectives and redundant detail before dropping function.
4. Compress semantically: preserve meaning and grammar, never slice a prompt or Devanagari string to fit. If all hard constraints cannot fit, move detail to a supported separate field/section or state the conflict. Never silently cut locked lyrics.
5. Count the actual pasteable content including spaces/section tags. The helper reports Unicode code points and UTF-16 units; provider counting conventions must be checked where they differ. Token counts are not character counts. Keep raw lyrics intact and avoid normalization that alters a lock.
6. Resolve supported parameters. Pick conservative defaults from the actual interface or a scoped tested profile; do not invent exact percentages. Return chosen settings when useful, but do not claim they were applied to an account without execution.
7. Check mutual exclusion, range/enum, mode compatibility and required inputs. An unknown field is not silently passed through. Distinguish `PENDING_SUPPORT` from invalid known syntax.

## Platform handling

| Route | Automatically handle | Boundary |
|---|---|---|
| Suno | Instrumental toggle/lyrics separation, usual 800-character instrumental preference, model choice by task | Numeric Styles/lyrics maximum remains unknown unless verified; do not invent an API |
| Suno creative sliders | Verify actual available sliders; explain lower/higher style adherence or variation as a proposed setting | Legacy guide describes Weirdness/Style Influence and Audio Influence with an upload; it does not prove each control works on every current model. No universal magic percentages |
| Eleven prompt API | Explicit Music model, prompt length, duration, prompt-only instrumental control | No prompt plus plan; no seed with prompt in checked endpoint |
| Eleven v2/v2.5 plan | Chunk count/durations/styles, total, no-lyric chunks/exclusions for instrumentals | No prompt-mode force flag in a plan; section timing does not prove an acoustic hit |
| Stable Audio | Actual mode, duration and instrumental/part intent | No intelligible-vocal claim; separate hosted settings from open-model controls |
| AIVA/SOUNDRAW | Actual composition/energy/mixer selections and supported exports | Do not turn control maps into invented free-text lyric/API fields |
| Beatoven/Udio | Current field schema and export status | Refresh API/UI/version; old guides do not prove present access |

Reference: [Suno creative sliders](https://help.suno.com/en/articles/6141377), [Eleven compose](https://elevenlabs.io/docs/api-reference/music/compose), [Eleven chunk plans](https://elevenlabs.io/docs/eleven-api/guides/how-to/music/composition-plans). Reviewed 2026-10-19. Slider observations are baseline guidance, not evidence of improved sound.

## Audit package

The local helper accepts `platform`, `mode`, optional `model`, `styles`, `lyrics`, `locked_lines`, `user_max_chars`, `allow_vocals`, `parameters` and `request` (for a complete Eleven Music body). It validates known contracts and produces warnings for unverified fields/support. Exit 0 is a text-contract PASS, exit 1 is FAIL, exit 2 is PENDING; inspect the JSON and resolve pending support before external submission. If returning a song, lyrics must remain present; if instrumental, reject a positive vocal brief/lyrics. It cannot judge rhyme, melody, emotion or actual rendered quality.
