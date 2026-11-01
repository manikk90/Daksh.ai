# Performance, dialogue and physical action

## Contents
- Character performance profiles
- Performance and dialogue contract
- Voice and lip-sync routing
- Body and interaction mechanics
- Special actions and effects
- Select the storyboard instant
- Examples and continuity

## Character performance profiles

Before planning any named character action or dialogue, resolve the exact approved identity tag and load that character's saved project performance profile. Reuse the profile across storyboard, individual image prompts, video prompts and revisions. A character name alone does not supply traits absent from the screenplay or approved history. Store profiles in authorized project records; until such a record exists, use sourced project-reference entries and mark missing fields PENDING. Do not silently invent a complete cast bible.

Keep each profile compact and versioned. Use `assets/character-performance.template.json` as an optional project-record shape; store actual profiles in the authorized project destination, not as private cast data in the reusable template. Index by project plus exact tag and record source/profile revision, so an alias or costume variant cannot silently select another character.

Keep these fields:

| Field | Store |
|---|---|
| Identity and evidence | Project, exact approved character tag, source/date, confirmed facts versus provisional interpretation |
| Physical baseline | Age/physical constraints, habitual posture, gait/rhythm, weight shifts, movement speed, hand use and prop habits |
| Individual mannerisms | A few distinctive sourced gestures, head/shoulder habits, facial response or characteristic stillness; frequency/context rather than a tic repeated every shot |
| Speaking action | Language/dialect, vocal pace/register, breathing and pauses, emphasis, mouth/jaw/head/hand coordination while speaking |
| Listening and reactions | Attention channel, processing rhythm, interruption/turn-taking and characteristic visible response |
| State and relationships | How emotion, fatigue, injury, status and specific relationships change the baseline; arc/scene overrides |
| Boundaries | Prohibited behavior, reveal/visibility limits, source gaps, latest user corrections and scope |

Compile in this order: exact character -> saved baseline -> current intention/relationship/emotion -> physical start/contact/prop state -> requested action -> shot-specific performance -> storyboard instant and video progression. Preserve identity while letting performance change under grief, fear, anger or a new relationship. Distinctiveness does not require inventing an eccentric gesture for every character.

For a still, select one observable character-specific posture, expression or gesture instant; omit vocal delivery and multi-stage action instructions from the still prompt. For video, direct motion rhythm, gesture preparation/contact/settling and, when requested, exact dialogue with the character's speaking-action style. Include only profile details that materially affect this shot. A locked camera, occupied hands and an offscreen speaker constrain which mannerisms can appear.

QC each affected prompt against its loaded profile: wrong-character mannerism, generic performance replacing a known trait, forbidden visual tracking, unsupported new habit, impossible free-hand gesture, repeated tic, and reset emotion/contact across cuts. Track profile/version in the planning record, outside executable copy blocks. Save new user corrections to the affected character and scope; do not promote a one-scene emotional reaction to a permanent personality trait.

## Performance and dialogue contract

Read the exact scene and approved changes. For each meaningful turn identify objective, addressee, obstacle, tactic and subtext; distinguish what is said from what the character wants to achieve. Preserve wording, dialect, order and speaker unless rewriting is authorized. Use playable intention verbs (reassure, tease, conceal, warn, persuade), not an adjective inventory.

Retain requested English bracketed delivery/emotion tags in tagged dialogue handoffs, as well as every spoken word, repetition and the exact speaker token. Bind each tag to its intended phrase; preserve supplied tags unless the user changes that delivery. An explicit newer intention such as teasing may replace conflicting hesitant/curious direction within that shot, without rewriting the Hindi. Keep tags as non-spoken direction. Separate a visual identity tag from a supplied dialogue-speaker token when they differ; record that source mapping rather than silently renaming either. For a named generation tool, compile supported delivery controls or separate direction as its verified interface requires; a portable `[teasing]` cue is not proof of native model support.

For each beat record:

| Field | Direction |
|---|---|
| Stimulus | Preceding line, touch, sound, discovery or decision |
| Emotional entry | Actual state carried from preceding shot |
| Intention/subtext | Desired effect on a specific listener; concealed thought if relevant |
| Voice | Pace, relative volume, register, stressed words, breaths and purposeful pauses |
| Body | Support, posture, tension, gesture path and attention through sight/hearing/touch |
| Expression | Small observable transition in face; avoid contradictory simultaneous extremes |
| Listener | Who hears/sees it, when they process it, and visible response |
| Emotional exit | Changed feeling/decision and settling gesture carried into next shot |

Choose only relevant details for the prompt. Do not animate every facial muscle or make every line a new cut. Avoid default permanent smiles, constant crying, generic anger and synchronized reactions. Quiet acting can be stillness, delayed response or interrupted gesture. Do not treat a mouth pose in a still as verified pronunciation or lip-sync.

Use a cause chain: stimulus -> processing/listening -> visible response -> next action. Mark anticipation only when the character already knows what is coming; otherwise do not react before the stimulus. Motivate pauses with thought, listening or breath rather than arbitrary slow delivery. Scale vocal/body performance to character age, relationship, setting and visibility convention; do not infer disability behavior solely from appearance.

## Voice and lip-sync routing

Establish the applicable route before promising output:
- Native generated dialogue: name the speaker, exact utterance and language/dialect, performance and on/offscreen status; verify model audio support. Prevent speaker swapping. Mark wording/timing fidelity unverified until audio is listened to.
- Supplied recorded audio: inspect/listen where possible; use actual duration, pauses and emphasis as timing reference. Align visible mouth/gesture and listener response to that track; do not estimate measured timing from word count alone. Use a supported audio-driven workflow, not an invented audio input.
- Separate dubbing/lip-sync: plan picture, speaker shot, reference voice/audio and downstream synchronization separately. Generated silent talking is not a verified match to a later recording. Preserve cut handles and stage faces readable for the selected sync tool.
- Offscreen dialogue/voiceover: keep visible non-speakers listening or otherwise acting; do not animate their mouths to the line. Use voice tool tags only if supported; keep technical tag text outside spoken words.

Multilingual versions preserve intention and action beats; performance and duration may differ. Do not shorten/rewrite approved dialogue merely to fit an arbitrary clip. Split at motivated pauses or report a duration mismatch. Audio QC checks exact words/order, speaker identity, pronunciation, dialect, emotional contour, synchronization, overlap and ambience balance.

## Body and interaction mechanics

Record action as one coherent beat, not one frozen verb:

`start pose/support -> trigger -> anticipation -> movement path -> contact or weight transfer -> follow-through -> recovery/end state`

Specify only mechanics the shot needs: support foot/hand, body orientation, travel vector, balance/centre of mass, joint range, torso/shoulder response, hand path, speed/easing and ground/object support. Keep limb laterality separate from screen-left/right; a camera reverse does not change anatomical hands.

| Action | Required mechanical checks |
|---|---|
| Walk/stop/turn | Step rhythm, planted support foot, modest weight shift, torso turn, start/stop settling |
| Climb/descend step | Real tread geometry, foot clearance/contact, weight transfer before trailing foot follows |
| Blind navigation | Approved individual performance; modest cane sweep/probe, tactile confirmation before transfer, upright listening attention; no invented visual tracking |
| Sit/stand | Seat/support visible, approach/turn, bend and supported weight transfer; no teleport between levels |
| Reach/grasp/place | Clear target distance; fingers approach, contact/grip, load transfer, release, stable support |
| Carry heavy object | Load supported by hands, elbows/torso respond to weight, small natural sway |
| Adjust tiny object | One hand stabilizes, other manipulates, miniature scale and supported prop remain consistent |
| Joined hands | Initiating hand, receiving hand, contact/grip, relaxed pressure, travel spacing and release state |
| Leader/follower | Who is ahead, half-step/relative spacing, pace, maintained contact, no unintended pulling |
| Listen/react | Sound source direction, processing delay, head/ear turn, eyes follow actual sight convention |

Contact continuity is explicit: free -> approaching -> touching -> gripping/supporting -> releasing. Split into shots when a contact change cannot be represented reliably. Do not morph a held prop into a hand: metaphorical substitution requires a cut or approved transition. Avoid simultaneous incompatible hand tasks or unsupported floating props.

## Special actions and effects

Direct fictional physical action through observable staged phases and editorial coverage; do not provide practical stunt execution or dangerous real-world rigging instructions. Preserve approved content and apply applicable safety rules. Do not circumvent a tool rejection.

| Action/effect | Coverage and logic |
|---|---|
| Throw/catch | Preparation, release/trajectory, receiving contact, recoil/settling; stable object identity and ownership |
| Drop/bounce | Release, descent, first contact, rebound and rest; gravity, surface direction and sound linked |
| Fall/impact | Loss of support, travel direction, contact, follow-through/aftermath; split coverage, preserve axis/scale |
| Recoil/collision | Named impulse/source, body response and recovery; avoid repeated unmotivated impacts |
| Jump/flight | Start support, launch, travel and landing/hover convention; physical or divine mechanism explicit, no invisible climbing |
| Animal action | Species-consistent anatomy, body continuity, surface contact, plausible scale; do not replace a required action with an unrelated pose |
| Divine/subjective reveal | Who perceives it, physical anchors, reveal onset, light/material changes, continuity back to reality |
| Transformation | Before/after identities, visibility, transition method, which props persist; separate complex stages |
| Weather/particles | Motivated direction/strength and delayed response of cloth, hair, leaves, dust, water |

Distinguish real-world physics, approved stylization and supernatural rules. Do not silently invent supernatural exceptions to repair ordinary physical errors. VFX preserves the foreground performance and lighting anchors. Background/crowd reacts only to events it can perceive.

## Select the storyboard instant

For every shot name the selected action phase and its editorial purpose. Choose a single unambiguous state that reads at board size and supports the intended video start. Do not prescribe several poses or focus states in one cell.

| Need | Preferred instant |
|---|---|
| Explain anticipation/intent | Preparation just before movement, recognizable target/gesture |
| Reveal first evidence | First readable emergence; keep later revelation absent |
| Explain action/contact | Clear contact or near-contact with support and object ownership visible |
| Show consequence | Settled outcome after the action; do not imply it is still pre-action |
| Emotional turn | First readable change following the stimulus, not generic neutral portrait |
| Exact motion generation | Valid actual start pose; optionally separate approved end keyframe if supported |

Label `coverage keyframe` versus `generation start frame` when they differ. A peak-impact or already-released object image cannot automatically animate a preceding wind-up/release. Choose a separate pre-action frame, start at the shown phase, or report the missing starting state. Never reverse the event accidentally to force an input image.

Prefer one clear contact instant over extreme blur that hides evidence. A motion arrow/annotation belongs in a requested planning overlay, not automatically in the photoreal cell. Avoid adding another action solely to fill the nine-cell grid.

## Examples and continuity

Naina's affectionate line: intention = tease a trusted friend; voice soft/conversational; small pause after “सखा”; shoulders relaxed; fingers explore clothes then reach crown on the pagdi cue; small amused question at the end; brief waiting hold. Unseeing eyes remain consistent with the active reference; attention uses touch/listening.

One upward step: support weight on lower tread -> cane confirms next tread -> leading foot lifts/clears riser -> foot plants -> weight shifts -> trailing foot follows. Choose a still at visible planting/contact if illustrating movement; choose pre-lift if generating the whole step from that input. Keep camera tracking instructions separate from the subject mechanics.

Across cuts preserve voice/breath phase, tension, emotion, gesture stage, hand contact and prop state. Store the next shot's required entry state. Do not restart a gesture or dialogue phrase in each generated clip. Start/end edit handles are useful pauses, not mandatory dead time for every shot.
