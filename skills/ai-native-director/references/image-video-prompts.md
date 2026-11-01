# Still, storyboard and video prompt compiler

## Contents
- Context contract and output modes
- Still prompt
- Board prompt
- Image-to-video prompt
- Text-to-video prompt
- Editing prompt
- Cast/costume reference prompts
- Performance, action and review handoff
- Examples and QC

## Context contract and output modes

Extract approved scene version, beat, action instant, subject/reference tags, location/surface, visibility, hand ownership, start/end prop state, action axis, light, intended attention and edit purpose. Resolve conflicts using latest explicit user instruction; do not transfer another project's default or treat an old sample as current script. Keep user vision literal unless an alternative is requested.

Plan request: deliver beat/camera/blocking/coverage table, no generation. Prompt request: executable prompts. Bana do/regenerate: perform available authorized generation and visual QC. Video request: compile motion for actual start-frame state. Default Hinglish output; use precise English for a tool where useful. Preserve user's exact dialogue order/wording.

Maintain a full internal shot specification, then compile only the fields useful to the target. Structured planning detail must not become a bloated model prompt. Unknown model: portable form; named model: apply verified adapter. Keep generation metadata/IDs outside model text if the target does not understand them, while preserving exact tags in the production handoff.

Use story context to choose this beat's intention, continuity and withheld information. Emit only the information needed to realize this cell/shot; omit unrelated exposition, adjacent beats and their tags. A strict supplied frame is the visual contract: retain its crop, visible subjects/partial owners, layout, focus and relevant location view except for specifically authorized edits. Optional 2S/OTS experiments yield to that contract. If source media is unavailable, preserve the stated constraints and leave visual matching pending.

For substantive composition choices, use `shot-composition.md` before compiling. Carry first-read target, essential secondary evidence, physical placement/contact, layer jobs and sharp plane into only the necessary prompt clauses. Keep pattern IDs, source citations and QC notes outside executable prompts. A small wording/dialogue edit reuses the approved composition.

## Scoped revisions and shorthand

Source:27October2026 supplied user corrections/memories and dated retrieved summaries; scope: AI Native Director prompt revisions. Retain the supplied shot identifier in the opening shot header (including its original leading timecode when present); never invent a missing ID. Default to minimal requested edits, preserving original structure and exact tags. Keep prompts compact unless detailed output is requested; do not add unsolicited CAMERA/LIGHTING/NEGATIVE/AUDIO sections.

In every video prompt, put ALL action/timing, camera, sound, performance directions and visual Refs before the final dialogue block. Preserve exact supplied words, punctuation, order and speaker tokens in `DIALOGUE: @character: "..."`. Nothing follows the final dialogue line. Offscreen voice is an audio role, not permission to render its owner. Return only executable prompts in one copyable code block for prompt-only requests.

- `fm`: strict frame match; preserve actual crop/composition, identity, positions, perspective, light and relevant visible bindings; only compatible motion.
- `pm`: the same visible-frame discipline, short by default; primarily improve compatible action/performance and motivated camera movement.
- `fx`: full context-aware scene fix, not VFX; inspect mood, approved view tags, blocking/axis, visible inventory, blindness-relevant behavior and continuity. Its broader authorized repair overrides the ordinary minimal-edit default only within the requested scene.
- `sc`: safety check plus genuinely safer rewrite; change the depiction/shot if necessary while preserving supported story and locks. Never promise acceptance or bypass safeguards.
- `se`: motivated shot experiments within current request; strict reference locks take precedence. Do not silently replace a locked camera.

Resolve reference endpoint role before video progression: an explicitly FINAL frame constrains the ending, not the opening. In supplied `@s9p1s5`, empty foreground precedes the late RIGHT-hand entrance; retain the specified timing and final pose. Boundary: an ordinary approved start-frame task keeps its actual opening; do not apply this late-hand sequence to other shots. New marked-bike position/blocking corrections remain target-specific pending actual image mapping; do not convert screen-left into a courtyard-wide world rule.

## Still prompt

Order: exact references and scene -> chosen action phase/visible performance -> shot size/camera -> blocking/support and depth -> focus -> motivated lighting/material -> essential invariants. Select the instant using `performance-and-action.md`; do not automatically use an action climax as a generation start frame.

```text
@<shot-id> [<SIZE>]: <ratio>, <medium>. <exact subject/costume/prop/location tags and current scene instant>. <Chosen action phase: one visible pose, support/contact, expression and attention target>. <Lens look/mm, camera height, pitch/viewpoint, roll>. <Screen placement and foreground/midground/background>. Focus on <target>; <named layers> softly defocused/readable. <World-light direction and natural texture>. Preserve <critical continuity constraints>.
```

Show one instant. Do not put walking then sitting then opening bag into one still. Do not prescribe a rack-focus transition or camera orbit inside a single still. Do not assert exact lens physics from prompt wording. Bind tags for partial hands, OTS shoulders, silhouettes and reflections too. Include only subjects visible in that frame.

For individually executable tagged shots, repeat each actually visible relevant prop tag inside that shot; shared headers are not a substitute. When Naina's bag or strap is visible, write exact `@canvas-travel-bag`. Preserve the active approved placement and existing strap/support (RIGHT hip in the current supplied seated setup); a later authorized scene override takes precedence. Do not transfer walking hand occupancy into seated coverage. Keep offscreen bag/prop states in separate continuity notes, outside executable visual text and Refs. A face-only crop does not acquire the bag merely because the scene register or an absence clause mentions it. Never use the gardener's `@woven-bamboo-basket` for the small ornate idol basket or invent a basket tag.

Derive each visual prompt and reference-binding allow-list from the actual approved frame/shot source: required visible entities, partial/reflected owners and exact relevant location/surface only. Remove other-frame/global cast, props, crowd and alternate location tags from text and actual tool attachments. For the corrected 23 October cart-only frame, visual inventory is exactly `@nandu-s-cart` plus `@village-alley.ground`; do not add Nandu or Pooja. A distinct Nandu-plus-cart source or explicitly on-frame crowd retains its own visible subjects; do not blindly reuse the cart-only inventory. Missing media/tag binding remains pending rather than invented.

Use source-derived `required_tags`/`allowed_tags` with `audit_prompt_contract.py` on the complete visual text plus visual Refs. Do not derive them from the draft or use the full scene register as the allow-list. Review untagged prose for extra entities/location descriptions and actual reference-role inputs too; removing a tag while keeping its unwanted subject in prose does not pass. Keep explicitly requested offscreen dialogue/sound and its exact speaker token in a separate audio handoff, outside visual Refs. The literal helper has no audio-role parser; check audio words/speaker separately and manually verify no audio-only source leaked into visual bindings. Literal PASS does not prove semantic inventory completeness, source authenticity, tool attachments or visual QC.

## Board prompt

For a full board compile nine equal horizontal 16:9 cells, 3 columns x 3 rows, row-major order, narrow consistent gutters. If fewer useful shots exist, report unused capacity and use a partial sheet or explicitly empty slots, not repeated shots or another scene. Overall default target 3840x2160; verify actual output; a 4K board is not nine 4K shots. No rendered text by default unless the user asks for shot IDs. For existing labelled boards preserve requested labels.

Give tool references explicit numbered roles: identity, costume, prop, architecture, lighting/style or edit target, with an explicit cell-to-reference map. Share applicable format/style locks, then give numbered self-contained action instants containing only that cell's necessary information and bindings. A board's reference pool is the union needed by its cells, not every cell's allow-list. Repeat essential local subject/location bindings; keep absent subjects absent. Preserve approved architecture, light direction and axis; don't fill cells with the next scene.

For underfilled panels, report useful shots and unused cells; only fill with justified details/reactions when authorized. Supplemental pickup panels carry destinations in planning and use distinct IDs; do not append them as chronological story progression.

## Image-to-video prompt

Resolve the approved SINGLE shot frame as opening or ending evidence from the user’s stated role; use it as starting evidence only when it is a start frame. Focus primarily on motion and temporal continuity; do not re-describe every visible garment. A contact change or scene not present in the image needs explicit staging or a separate shot.

Build this clip's visual tag/input set from its actual frame and authorized progression, not the whole panel or scene. With strict start/end frames, preserve both endpoint compositions, identities, positions and contacts and describe only compatible motion between them. A new entrant/reveal needs explicit authorization and exact approved mapping; story context alone does not introduce it. Do not append all still/scene tags to `Refs`. Keep requested offscreen audio roles separate from visual tags, and retain a partial shoulder/head owner's tag when that body edge is actually visible. Select exact existing location views for the shown angle; unknown or unseen variants remain unresolved.

Portable production handoff:
```text
[0-<duration>s] @<shot-id> [<SIZE>]: From <actual starting pose/contact>, <exact subject tag executes one coherent action beat: trigger, path/vector, pace, support/contact and settling, with visible emotional change>. Camera: <starting height/framing, one move, path/speed/end framing>. Focus: <fixed/follow or A-to-B rack, sharp target and soft layers>. <Relevant environmental response>. End: <pose/position/prop/contact/emotional state for next shot>. <Supported sound, vocal performance and reaction onset>.
Refs (continuity): <exact relevant locked tags>
DIALOGUE: @<speaker>: "<exact supplied line, only when provided>"
```

Timecodes describe intended beats, not frame-accurate guarantees. Do not divide every second into contradictory events. Separate edited scene runtime from tool clip length. Keep natural locomotion, joint limits and contact: probe step with cane before weight transfer; retain joined hands and right/left ownership; feet contact actual tread. Specify ahead/behind and leader/follower relative spacing, not only left/right.

For follow-focus, name moving target. For rack focus specify sharp A, soft B -> sharp B, soft A; keep camera fixed unless compatible movement is motivated. Do not confuse actor moving with camera moving. End on a usable stable edit state when appropriate.

### Preserve camera position, timing and reference roles

Keep camera translation, lens zoom, focus and subject playback speed separate. A requested slow zoom tightens framing from the same camera position; do not silently turn it into a dolly, orbit or shoulder pass. Slow motion changes visible action pacing and does not by itself request a camera move, rack focus, changed voice speed, extra duration or an invented frame-rate setting. When both slow motion and a slow zoom are requested, describe both explicitly. Preserve normal dialogue delivery unless an audio retime is authorized; unresolved picture/audio compatibility stays pending.

For OTS, name the shoulder owner, the focused subject and the camera's permitted path. If the source says only Naina's shoulder is visible, retain that soft edge and keep the specified speaker sharp. When the camera must remain behind a standing shoulder, hold its world position during a zoom; it does not advance through/past the shoulder while the foreground character stays still. An explicitly requested travelling OTS is a different valid move. A departing subject may recede as the lens gently tightens; do not promise constant subject size without reconciling those two rates.

Preserve ordered performance beats and their dialogue onset. A seated character who must stand, search ahead to each side, then speak cannot begin standing, search behind, speak before the search, or acquire extra walking beats. If the requested duration cannot support the exact line plus actions, flag timing as provisional or split only at an authorized edit; do not delete/rewrite words to force a fit.

For a supplied reference video, separate motion/visual-language reference from start-frame, identity, costume, geography and colour references. Inspect the video before claiming its actual camera motion or timing was matched. Transfer only the requested aspects compatible with the approved shot; retain exact tags, action, ownership, focus and tone. An unavailable video permits a prompt based on the user's stated motion, with reference matching unverified. Merge a requested reference-video instruction into the same executable prompt rather than returning only a generic instruction and dropping the shot.

## Text-to-video prompt

Supply absent starting visuals before motion:
```text
@<supplied-shot-id> <Shot size, angle/height and composition>. <Subject appearance/reference identity, setting and light>. <Starting state and one coherent action beat with direction, pace, support/contact and emotional progression>. <Camera path and start/end framing>. <Focus behavior and environment response>. <Supported sound and vocal performance>. <Usable end state and concise essential continuity constraints>.
DIALOGUE: @<speaker>: "<exact supplied line, only when provided>"
```

Use one continuous scene per short clip. Translate abstract emotions into visible posture, gesture, expression and timing. Separate mutually incompatible moves into different clips. Treat reference images as identity/world constraints only when the target actually supports them.

## Editing prompt

Use exact selected source and verified selection/mask. Describe requested change, bounded region/cell and replacement; enumerate critical invariants. Ask when selection is unavailable rather than guessing. Repair faults selectively, not redesign accepted shots. Never replace an inaccessible target with another conversational image.

## Cast/costume reference prompts

Use `cast-and-costume.md` for the distinct identity/look/scene-state contract and sheet/revision prompt structures. Do not treat a four-view costume sheet as four story beats or force it into a nine-cell board. Bind identity and garment references to separate roles, preserve exact approved tags and side-specific wearing anchors, and compile only visible relevant outfit/state facts for a scene. Use the appropriate single inspected view for image-to-video when required; a contact sheet is not automatically a valid start frame. For costume-only edits keep face/age/hair/body, unrequested garments, layout and approved tone unchanged.

## Performance, action and review handoff

Keep rich direction in the production record; compile only necessary visible details and supported model controls into the executable prompt. Do not include unspoken acting notes in quoted dialogue or force a still to contain temporal performance.

Optional dialogue direction when requested:

`Speaker/tag | Exact line | Addressee/intention | Emphasis/pause/breath/pace | Body/face transition | Listener response | Audio route and timing evidence`

Optional action/instant record:

`Shot | Entry pose/support | Trigger | Action phases/contact | Exit state | Selected still phase | Coverage keyframe or generation start | Camera/focus | Edit/sound connection`

Preserve one coherent beat; split independent actions or impossible contact changes. Lip-sync/supplied-audio directions use verified tool workflows and observed audio timing. If no model/audio specified, deliver portable direction with the route unresolved, not an unsupported tool promise.

For pickup panels return a narrative assembly map outside executable prompt blocks. Mapping Agent verifies exact tag/asset binding before compilation; QC Agent checks plan/prompt and inspected output separately using `mapping-and-qc-agents.md`. Keep unknown visual, temporal or audio evidence PENDING.

## Examples and QC

Example still, with tags only if locked for the active scene:
```text
@s1p6s2 [ECU]: 16:9 realistic cinematic tactile insert of @naina-01's fingertips resting on the silken clothing of @laddu-gopal-idol, supported inside its lap basket. 100mm macro look, camera at basket-rim height, oblique side view, 0-degree roll. Fingertips and fabric sharp; the active approved costume and temple background softly defocused. Warm morning side light; natural clean fingers and stable miniature brass proportions.
```

Example portable video direction:
```text
[0-5s] @s1p1s5 [ECU]: @naina-01 probes the next stone tread with @wooden-stick, confirms its edge, then places one bare foot on it and transfers weight in a measured upward step. Camera tracks parallel at 8cm above @krishna-temple.outer-steps.ground, keeping foot and stick tip framed. Follow focus stays on the stepping foot and tread; background remains soft. End with foot planted and body balanced. Natural bell ambience.
Refs (continuity): @naina-01 @wooden-stick @krishna-temple.outer-steps.ground
```

Runway-style motion-only compilation of that shot, if the start frame actually supports it: The girl probes the next stone step with her cane, then takes one measured upward step. A ground-level camera tracks beside her foot; focus follows the planted foot and cane tip. Background stays soft.

QC before delivery: each cell/clip's necessary information and exact tag/input set; no scene-wide context leakage; strict-frame crop/layout/inventory/focus and endpoint compliance; exact tag strings and asset binding; active costume/prop source; exact dialogue and performance intent; correct scene/instant and valid input pose; no premature reveal; frame height/angle actually visible; primary action/contact evidence readable; focus target explicit; camera versus subject motion separate; optical/physical compatibility; anatomical hand ownership/support; axis/light; one coherent action beat; model/audio workflow checked; adjacent edit state matches; no claimed generation, measured sync or native dimensions without evidence.

### 1 November shortcut expansion

`fx c` is the composition-only branch of `fx`: keep the scene beat and locked blocking, but boldly redesign framing, viewpoint, geometry, depth, focus, crowd readability and motivated lighting. It requires a visual preview before the revised prompt. Preview means actual cinematic reference-frame images/thumbnails, not ASCII or a text diagram.

`ah`, `dh`, `ah+dh`, and `ch` are priority modifiers. `dh` also refines emotion/voice tags automatically while preserving exact dialogue wording. `ch` cannot override a locked STATIC camera. `fm + dh` keeps the supplied frame and allows only restrained compatible handheld tremor unless the user requests a camera change. The dialogue block remains the absolute final content of a video prompt.
