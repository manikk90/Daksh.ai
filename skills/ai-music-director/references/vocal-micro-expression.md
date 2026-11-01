# Singing micro-expression and phrase direction

Treat a vocal performance as emotional intent across musical phrases. These are artistic production directions, not a universal tag vocabulary or guaranteed model parameters. Preserve the chosen voice/age character, words, pitch comfort, breath and melody. For instrumental work omit the entire vocal layer.

## Make an expression map

For a new song map section/line → intention → onset/articulation → breath/dynamic → one meaningful emphasis → release. Start with one dominant emotion and at most one or two subtle gestures per phrase; this is a density heuristic, not a provider limit. Keep plain locked lyrics intact and put directions in a separate field/map or supported section styles.

| Intent | Useful audible behavior | Avoid |
|---|---|---|
| Playful affection | Light smiling onset, clear short consonants, tiny pause before a teasing reply | Constant giggling, baby talk or swallowing the words |
| Seva/intimacy | Warm close tone, soft attack, relaxed phrase ending, breath between thoughts | Breathy noise replacing diction |
| Wonder | Small restrained lift in register/dynamics, held open vowel, space after discovery | Full triumph before the reveal |
| Hesitation | Slight delayed pickup, shorter phrase, tentative onset | Random pauses inside a locked name or rapid pitch wobble |
| Gratitude/relief | Audible release of tension between phrases, warmer resonance, settled cadence | Overdramatic sobs masking thanks |
| Grief | Fragile but intelligible onset, restrained tremor on a sustained note, exposed ending | Continuous crying, gasps, out-of-tune collapse |
| Determination | Firmer consonants, supported tone, steady rhythmic placement | Unrequested shouting or hostile timbre |
| Lullaby | Rounded vowels, gentle legato, quiet taper, controlled breath | Sudden belt, sharp attack or loud last chorus |

User direction overrides defaults. For a childlike devotional song use natural conversational warmth, comfortable range and clear Hindi; do not force an adult virtuoso delivery. A smile in sound does not require audible laughter. A breath in a vocal song is not an extra spoken line.

## Compile by destination

- **Suno:** describe vocal character and section arc in Styles; use only supported structure/delivery cues in the lyric surface. Do not add unverified `[sobs]`, emotion percentages or SSML to locked lyrics. If tag support is uncertain, use a separate performance map/plain descriptive Styles.
- **Eleven Music:** use English positive/negative style descriptions for phrase/section delivery; keep actual Hindi words as lyrics. Follow the current plan guide for any inline cue syntax; do not invent an API field `micro_expression` or reuse speech `stability`/`similarity_boost`.
- **Udio:** use current documented lyrics/section controls or descriptive prompt cues. Verify tag behavior before claiming parser support.
- **Instrumental-first platforms:** preserve the singing brief as a separate singer/vocal-platform handoff. Do not promise intelligible lyrics from Stable Audio 3 or a lyric-less arrangement control surface.

Micro-performance, melody and mix interact. Simplify accompaniment during delicate words, reserve instrumental replies between lines and reduce competing frequencies when needed. If detailed phrase control fails, use a supported section edit/pickup; a larger prompt is not always the remedy.

Official baseline: [Eleven Music best practices](https://elevenlabs.io/docs/overview/capabilities/music/best-practices), checked 2026-10-19, documents descriptive vocal delivery and section/arrangement guidance. The specific phrase maps above are original editorial recommendations; their acoustic effect is untested here.

## Review and learn

Check text for contradictory emotions, excess direction, changed hook words, missing breath space and unsupported syntax. Actual audio review checks intelligibility, register, phrase timing, unwanted spoken instructions, exaggerated emotion, pitch drift and vocal consistency. Record text-only versus listened evidence separately. Promote a platform-specific expression technique only after a relevant observed result; otherwise label it a production hypothesis.
