# Scene scoring and musical continuity

## Spot actual sources

Read the supplied scene or inspect the cut. A synopsis cannot establish frame-specific sync. Find emotional turns and protected reveal points; choose among silence, ambience, diegetic sound, score and song. For prompt-only tasks keep this analysis internal.

For substantial scene/episode work use:

| Field | Meaning |
|---|---|
| Cue ID/version | Preserve existing IDs; proposed IDs remain proposals |
| Source/scene | Actual screenplay/cut version followed |
| Entry/exit | Measured timecode, or specific action/dialogue trigger |
| Duration/status | Target seconds; measured or provisional |
| Function | Whose emotion, intended turn and information to conceal |
| Musical design | Motif, lead/support roles, pulse, harmony, register |
| Arc/hits | Opening, turn, peak, tail; measured or relative triggers |
| Dialogue/SFX space | Protected words, breaths, wind/impact/bell cues |
| Production route | Platform/model/interface, prompt/lyric version, take/stems |
| Review/placement | Text/audio/edit/approval status and timeline destination |

## Starting palettes

These tempo ranges are artistic starting proposals, not fixed project locks or universal emotion mappings.

| Function | Starting design | Development/boundary |
|---|---|---|
| Tender devotion | 62–82 BPM or free pulse; bansuri/veena, tanpura, sparse bell | Intimate motif and rests, not continuous ceremony |
| Playful child adventure | 108–118 BPM; flute hook, dholak/matka/khartal, small acoustic replies | Curiosity → mischief → bright return; original melody |
| Vintage comedy | 116–126 BPM; clarinet/mandolin, pizzicato bass, woodblocks | False ending, silence, held-note joke and rhythmic reversal |
| Grief | 48–70 BPM or rubato; sarangi/violin/veena/cello | Fragile phrase → aching rise → exposed unresolved tail |
| Falling/chase danger | Subdividing pulse, tremolo, tense drone, selective percussion | Leave wind/action SFX audible; layering need not change BPM |
| Vayu rage | 138–164 BPM or heavy half-time; ostinati, pakhawaj/nagara, low brass/strings | Transform grief motif; controlled drops; no premature celebration |
| Before miracle | Slow unresolved cell, tanpura, restrained metallic resonance | Withhold full divine cadence until reveal |
| Miracle revealed | Familiar flute/veena motif expands into strings/santoor | One earned peak, then release; no voices if instrumental |
| Lullaby | 50–68 BPM; rocking 3/4, 6/8 or gentle simple pulse | Narrow motif and thinning texture; ticking only when requested |
| Quiet suspense | Sparse ostinato and low ambiguity, silence | Preserve discovery; do not announce hidden threat |
| Relief | Reduced density and consonant return of known motif | Avoid full resolution while danger remains |

## Format, genre and energy

Adapt the musical job to the format instead of using the same epic cue everywhere:

| Format/genre | Useful approach |
|---|---|
| Feature/long drama | Long-range motif development, restraint and emotionally motivated silence |
| Episodic television | Recognizable identity, character variations and continuity across episodes; avoid exhausting the main theme |
| Vertical/mobile series | Fast recognition and clear dramatic turn in a short span; preserve dialogue intelligibility on small speakers |
| Ad/TVC/DVC | Brief-specific emotional proposition, concise hook and usable brand/ending hit without invented legal copy |
| Promo/teaser/trailer | Clear sectional escalation, edit-friendly rises/dropouts and button ending; do not paste a whole feature-score arc into a short teaser |
| Comedy/sitcom | Timing, rests, instrumental replies and understatement; score only gags that benefit |
| Horror/thriller | Ambiguous register, unstable texture or pulse, withheld cadence; preserve suspense rather than reveal the threat |
| Romance/intimate drama | Warm phrasing and space; identify tension/relationship rather than automatically choose piano |
| Action/mythic spectacle | Rhythmic architecture, register/texture contrast and controlled peaks; distinguish awe, rage and victory |
| Documentary/factual | Respect tone/evidence; do not use manipulative musical certainty to turn an ambiguous claim into fact |

Choose among folk, classical/raga-led, chamber/orchestral, ambient, acoustic, electronic/hybrid, jazz, rock, pop or minimal pulse palettes by story/culture and requested audience. Give a concrete reason when recommending a genre switch. A sparse cue can be large in emotional impact; scale is not simply instrument count or loudness.

## Motif design

Build identity from two or three stable elements: pitch contour/interval cell, rhythm and lead color. Store approved audio/MIDI/notation when available; text alone cannot guarantee note-for-note continuity.

Motif card: ID, character/idea, source/approval, contour/rhythm, register, characteristic phrase, harmonic setting, timbre, allowed variations and forbidden spoilers. Example `LG_COMPANION_01` is a proposed ID, not a pre-existing locked tag.

Transform through augmentation/diminution, register, orchestration, fragmentation, harmonization or interruption. Preserve enough identity to recognize. Reuse authorized approved references/stems when appropriate; a style reference does not guarantee exact notes. Do not change theme simply because the platform/model changed.

## Dialogue, counterpoint and silence

Choose counterpoint intentionally rather than equating sad with minor and happy with major. Let lead instruments answer between lines. Thin competing midrange and rhythm under speech; lowering volume alone may not solve masking. Protect breaths, sobs, wind, impacts and bells that carry meaning. Diegetic aarti/bells remain source sound unless deliberately integrated.

## Sync and finishing

1. Separate generated duration from final edited duration. State timecode basis/frame rate when supplied.
2. For exact hits, use sections/stems or supported duration controls, then align in an editor. Text cannot guarantee a hit on a frame. Review actual transients and transitions.
3. For constant tempo/meter estimate `bar_seconds = beats_per_bar × 60 / BPM`; flag rubato, pickups and tempo changes. Do not use this formula to claim inspected sync.
4. Choose a resolved button, unresolved tail, loopable bed or fade. Check loop seams and reverb tails in the audio.
5. Keep full mix, dialogue-friendly mix, vocal/instrumental variants and stems where supported. Separation can leak/smear sound; inspect it.
6. Use the destination's specs, not a universal loudness number. A proposed film handoff may use 48 kHz PCM WAV; confirm bit depth/channels. Upsampling an MP3 does not recover original lossless quality.
7. Listen for clipping, unstable pitch/rhythm, garbled Hindi, omitted/repeated words, extra voices, abrupt joins and tonal drift. JSON/waveform inspection cannot prove these qualities.

For regional delivery preserve approved score identity, review each vocal fit and keep dialogue/music/SFX separated. Track exact selected take and replacement destination. Prompt plans are not a finished soundtrack.
