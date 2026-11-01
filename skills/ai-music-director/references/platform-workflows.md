# Platform adapters

Baseline checked **2026-10-19**. See `assets/model-registry.json` for official sources and evidence status. The routes below are production judgments; vendor features remain distinct from tested performance and actual account access. Refresh official docs when making current claims or executing a model-specific job. Do not assume all controls are present in every UI/API, plan or region.

| Destination | Useful starting route | Compile into | Main boundary |
|---|---|---|---|
| Suno | Hindi song/theme and broad score exploration | Styles + custom lyrics OR instrumental control; selected model/editing tool | 800 characters is Manik's instrumental preference, not a universal limit |
| Eleven Music | Structured cue sections, lyric timing, video-conditioned scoring | Simple prompt OR model-specific composition plan; optional video route | Keep Music model IDs separate from speech models |
| Udio | Song/arrangement exploration | Prompt + custom lyrics or Instrumental selection | Official transition notice currently says audio/video/stem downloads disabled |
| Stable Audio | Instrumental cue, texture, isolated part, inpainting | Descriptive prompt + actual mode/duration/reference controls | Stable Audio 3 is primarily instrumental, not a Hindi singing route |
| AIVA | Composition/influence workflow and editable arrangements | Actual style controls, audio/MIDI influence, composition edits | Do not invent Suno-like fields or assume all plans allow delivery use |
| SOUNDRAW | Fast background arrangement with energy blocks | Genre/mood/length controls, energy blocks, mixer | Return settings/edit map; do not invent a free-text lyric field |
| Beatoven | Background cue or API-integrated scoring | Duration/mood/instrument prompt; current API schema if requested | Confirm exact API version; do not use an obsolete payload |

## Suno

Official snapshot: v6, v6-wild and v6-mini. Vendor positions v6 for control, wild for exploration, mini for faster ideas; do not call one empirically superior for Hindi without tests. Plan availability and current model picker require account confirmation. Studio 2.0 is a separate editing surface, not the generation model.

1. Draft core design: genre/context, tempo/groove, lead/support roles, playable arc, production and exclusions.
2. Instrumental: select the actual instrumental control and use the explicit no-voice text. Normally ≤800 characters for Styles; omit lyrics/aalap. Do not force the user's full screenplay into the prompt.
3. Song: custom lyrics in their own field, Style describing voice character, arrangement, tempo and energy. Section tags guide structure but do not guarantee performance.
4. Retain an approved motif/take through supported reference/edit/section tools when available; do not regenerate everything for one line. Verify current exact editing/export controls first.
5. Treat advanced stems and custom-model training as separate documented features with access/data requirements. Do not claim isolated clean parts or trained personal models without execution/evidence.

Sources: [v6 help](https://help.suno.com/en/articles/13924801), [model selection](https://help.suno.com/en/articles/13924737), [Studio 2.0](https://help.suno.com/en/articles/13670529), [stems](https://help.suno.com/en/articles/13925185).

## Eleven Music

Snapshot: docs list `music_v1`, `music_v2`, `music_v2_5`; explicitly select intended version instead of relying on the API default. Prompt/plan are mutually exclusive. Prompt mode has `music_length_ms`; `force_instrumental` is documented for prompt mode only. A seed is not valid with prompt mode in the checked endpoint.

For v2/v2.5 plans use `composition_plan.chunks`, not a copied v1 section schema. Chunk keys include `text`, `duration_ms`, `positive_styles`, `negative_styles`, `context_adherence`. Keep first-chunk styles specific to the whole piece; styles English, lyrics in the target language. No-lyric chunks plus no-voice negative styles for instrumental plans; do not claim the prompt-only force control also applies to plans. Actual silence/voice absence still needs listening.

Original example request skeleton; adapt durations to the scene, refresh schema before execution:

```json
{
  "model_id": "music_v2_5",
  "composition_plan": {
    "chunks": [
      {
        "text": "[Intimate opening]",
        "duration_ms": 18000,
        "positive_styles": ["instrumental devotional underscore", "gentle bansuri", "sparse veena", "tanpura drone", "68 BPM", "restrained dynamics", "dialogue space"],
        "negative_styles": ["vocals", "lyrics", "spoken word", "choir", "humming"],
        "context_adherence": "high"
      },
      {
        "text": "[Unresolved tail]",
        "duration_ms": 12000,
        "positive_styles": ["instrumental", "veena resonance", "thinning texture", "unresolved ending"],
        "negative_styles": ["vocals", "lyrics", "spoken word", "choir", "humming"],
        "context_adherence": "high"
      }
    ]
  }
}
```

Checked plan bounds: at most 30 chunks, each 3–120 seconds, total 3–600 seconds. A bound passing does not prove good phrasing or frame sync. Video-to-music is documented as a separate route; inspect actual video, request instrumental background where needed, then review result against protected dialogue/reveal beats. Audio references and inpainting are documented for v2/v2.5; verify exact interface/permissions before use. Do not confuse speech emotion tags with music syntax.

Sources: [compose endpoint](https://elevenlabs.io/docs/api-reference/music/compose), [chunk plans](https://elevenlabs.io/docs/eleven-api/guides/how-to/music/composition-plans), [Music overview](https://elevenlabs.io/docs/eleven-creative/products/music), [video route](https://elevenlabs.io/docs/api-reference/music/video-to-music).

### Video-to-Music preflight, verified29October2026

Use the dedicated video endpoint, not a copied compose payload. Its current reference allows up to10 ordered videos,200MB combined and600seconds total, optional description1–4100characters and up to10tags. Select the intended listed Music model explicitly; its default is not a project decision. `add_sfx`, `separate_tracks` and `use_audio_as_reference` are separate opt-in booleans, default false. Music-only direction does not authorize SFX or source-audio analysis. `separate_tracks=true` returns a ZIP of music/SFX tracks; it is not a guarantee of arbitrary instrumental stems. Verify actual input sizes/durations/order, account/output-format access and protected dialogue before executing an authorized generation. Do not import these video limits into Suno Styles or another endpoint. Boundary cases:11videos or601seconds exceeds this route; a simple Suno instrumental brief still uses its own compact prompt. Current official [video API reference](https://elevenlabs.io/docs/api-reference/music/video-to-music) was read29October; no uploaded video, generated score, sync or audio-quality test occurred.

## Udio

Use current creation UI: prompt plus Custom lyrics, or Instrumental. Verify supported section/guidance tags; they are not guarantees. Use a phrase/motif concept and focused arrangement changes for variations.

Official help checked on the baseline date states downloads of audio, video and stems are disabled; older posts advertising WAV/stems do not establish present availability. Treat it as an exploration route pending a verified export path before recommending final film delivery. Do not suggest capturing/evading disabled downloads. Account/export status is unverified here; no latest model ID is assumed.

Sources: [custom lyrics](https://help.udio.com/en/articles/10716221-create-a-song-with-your-own-lyrics), [first song](https://help.udio.com/en/articles/10715838-create-your-first-song), [transition notice](https://help.udio.com/en/articles/12683565-changes-associated-with-the-universal-music-group-umg-partnership).

## Stable Audio

Use a concrete prompt: track type/genre → instrument/playing roles → pulse/BPM → mood/development → recording/mix. Stable Audio 3 documentation supports optional `TrackType: Music`, `TrackType: Instrument`, `TrackType: SFX` labels. These are prompt hints, not API keys. Use isolated-instrument mode intent for a part rather than asking for a full ensemble then calling it a stem.

Choose text generation, audio-to-audio, inpainting or continuation according to the actual interface. Duration/model-size limits vary; verify them instead of copying open-model limits to a hosted app. It is primarily instrumental and not intended for intelligible sung lyrics. For strict instrumental use also exclude non-lexical vocal textures. Text pitch/tempo specifications still need review.

Source: [official 3.0 guide](https://stability.ai/guides/stable-audio-3-prompt-guide), [original repository](https://github.com/Stability-AI/stable-audio-3).

## AIVA

Start with the actual style/composition tools or an authorized audio/MIDI influence. Develop structure and edit parts; use MIDI/notation where available to refine motif continuity. Do not turn a general composition brief into unsupported API JSON. Check export and plan-specific permitted use for the intended film/TV destination; do not repeat broad marketing ownership claims as a legal conclusion. No current model version is asserted from a generic product page.

Source: [official product/documentation](https://www.aiva.ai/documentation).

## SOUNDRAW

Return an actionable controls map: genre/mood → duration → energy by section → instrument-group mixer decisions → export option. Edit blocks to create dialogue dips and a peak; inspect whether changes respect phrase boundaries. Stems are plan-dependent; verify current entitlement before promising WAV + Stems. It is not a substitute for writing Hindi sung lyrics.

Sources: [editing](https://docs.channel.io/soundraw-faq/en/articles/edit-a-song-in-soundraw-b6882b09), [stem availability](https://docs.channel.io/soundraw-faq/en/articles/Can-I-download-stem-files-6aee13c3).

## Beatoven

Write desired duration, dramatic mood, genre, instruments and arc as background-music intent. Checked public API accepts `POST /api/v1/tracks/compose` with `prompt: {"text": "..."}`, optional `format` and `looping`. A returned `task_id` is pending work; poll the documented task endpoint and inspect returned track/stem assets. Do not claim a duration hit or usable stems just because the job completed. Refresh current API before coding; store tokens in secure runtime configuration, never skill text.

Source: [original API spec](https://github.com/Beatoven/public-api/blob/main/docs/api-spec.md).

## Selection rule

Recommend by task fit, verified controls, editable output, usable exports, language evidence and actual access—not a universal “best platform” ranking. If a requested destination lacks a feature, produce the best supported route plus a clearly labelled editorial/DAW handoff. Do not buy credits, connect accounts or start training just to make a recommendation.
