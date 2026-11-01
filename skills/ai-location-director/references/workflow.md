# Staged location workflow

## Contents

- Approval and resumption
- Source-to-location map
- Master image and questions
- Coverage and capabilities
- Output pack
- Worked production example

## Approval and resumption

Record state transitions in the manifest:

`brief_ready -> master_draft -> master_review -> master_locked -> layout_questions -> layout_ready -> blockout_ready -> camera_references -> final_views -> qc -> delivered`

This is the `master-first` path. In `researched-agent` mode prepend `context_ready -> research_ready -> plan_review -> plan_locked` between `brief_ready` and `master_draft`. Use the controller reference for versioned plan/master approvals and worker coordination. An approval request concerns the concrete plan or image already presented; a routine research action needs no extra gate.

Allow branches `revision_requested` and `capability_limited`; store the last completed stage and next required action. A generated master is a draft until user acceptance or explicit delegated design authority. Approval of the master authorizes preserving its visible design; it does not prove unseen construction or scale. Carry existing authorizations forward.

If the user says “good, ab saare angles banao,” bind the accepted image/version, check any already answered layout questions and continue within that instruction. If the user says “pehle sirf ek image,” stop after producing and checking that one image. If the user asks only for prompts, provide prompts without generating assets. If the user explicitly changes the flow, honor that change and record it.

For “resume,” read state and existing outputs; inspect files that remain available, recover important sources through supported access and complete the missing stage. Do not restart, regenerate all views or mark completion from an earlier assistant statement alone.

## Source-to-location map

Create a compact working table:

| Scene/beat | Required zone | Interaction/route | Must-visible anchors | Adjacent geography | Evidence |
|---|---|---|---|---|---|
| Supplied scene | Named or proposed zone | Who moves where; support/contact surface | Doors, steps, furniture, trees | Start/end location and connection | Script/user/image/proposal |

Cover the scenes that use this location, including entrances and exits. Do not merge similar settings just because their props resemble one another. Keep mutable scene state separate from persistent architecture: an open door, moved stool, crowd or different time of day is a state preset, not a replacement building.

Use script facts to determine design: a couple must rise from a charpai and join a passerby; a blind character needs plausible walking/contact surfaces; a procession needs enough route width; a reveal needs a real occluding wall. Hand character performance to the directing workflow.

## Master image and questions

Make the master sufficiently wide to read meaningful distances and routes, but do not force an entire complex into one distorted frame. A large temple can use an architectural overview as its master plus connected zone seeds after approval. Keep master composition and architecture distinct: a required camera composition must not be changed merely to make the layout easier.

After master acceptance choose up to two questions with highest downstream impact. Example question pair in Hinglish:

1. “Ghar ke liye exterior aur aangan hi chahiye, ya screenplay mein andar ka kamra bhi cover karna hai?” Recommend the scope supported by the scenes; offer exterior-only or connected interior as appropriate.
2. “Ghar ke saamne aur side lane ka environment existing reference se lock karein, ya same gaon ke hisaab se main design karun?” Recommend existing reference if available; otherwise recommend a restrained consistent design.

Other high-value questions: a route's unresolved destination, a courtyard-to-sanctum opening, the level difference between gate and shrine, shared wall versus separate building, a disputed unseen side or required night/day coverage.

Do not ask “kitne angles?” when scene coverage can determine it, “same colour?” when already approved, “4K?” when already established or “kahan save karun?” when the destination is known. Do not ask questions to fill a quota. Keep the stage to one short batch, with recommended options and their effect on scope.

For optional unanswered choices, proceed with stated defaults and mark unseen design as proposed. For actual conflicting constraints, do not silently choose one; clarify only that conflict. Build independent inventories and camera coverage while waiting.

## Coverage and capabilities

Define a finite production boundary covering camera sightlines, movement destinations, approach/reverse views and key occluders. “Poora area” means the documented set and its required surroundings, not an infinite world. Near geometry visible in reverse shots needs explicit design; distant background can be an approved backdrop if parallax is irrelevant to planned movement.

Use a capability table internally:

| Capability | Execution | Claim boundary |
|---|---|---|
| Image generation available | Generate/edit with exact available references | Inspect output; tool success is not continuity PASS |
| 3D engine available | Build and render the scene, save editable source | Actual camera geometry; reconstruction may still be provisional |
| No 3D engine | Save coordinate model and code/SVG schematics as supported | Reference-only branch; do not call it camera-verified 3D |
| Conditioning available | Apply supported camera render/depth/edge/mask inputs | Record actual tool input; a prompt cannot substitute for a conditioning channel |
| Viewer supported | Embed actual texture, wire touch/drag/zoom, test | Interactive only after runtime/interaction check |
| Viewer cannot be tested | Deliver supported preview/source and precise pending status | Do not assert verified seamless viewing |

Do not install software, build an external account workflow or change unrelated project content solely because the preferred branch is unavailable. Use the best authorized supported branch, complete independent work and disclose the specific limitation. Obtain critical references when exact matching requires them.

Choose views by need. The reusable exterior set often includes overall, front, reverse, left, right, ground and top-down; the master already supplies overall, so avoid counting it twice. A tiny doorway may only need both sides and a contact detail. A sanctum may need its wall directions, floor and ceiling; define which camera sees which wall. Always honor explicit named views and inherited tags.

Generate front/reverse or the most important opposing pair first. Check shared anchors and boundary before dependent details. Group by zone in the manifest, not by separate disconnected worlds. Record useful scene-specific camera records such as route-tracking start/end or child-height insert, without inventing actors in empty location references.

## Output pack

Keep only useful production artifacts:

- Approved master with version and verified dimensions.
- Location manifest and source/approval/asset register.
- Editable actual 3D source when built, plus top-down and 3D overview.
- Connected zone map and camera records.
- Camera-specific references, supported guidance maps and requested final images.
- Requested anchor panoramas and interactive viewer with test status.
- QC record, repair dependencies and exact pending items.

Use stable names, e.g. `<location-id>-v01/<zone-id>/<view-id>.png`. Keep superseded outputs outside the approved set. A 3840x2160 image is 16:9; a full-sphere panorama normally needs a 2:1 canvas such as 4096x2048. Do not call a 16:9 resize a full sphere or assert these dimensions if the tool did not return them. Follow actual tool size support; record requested, native and exported dimensions separately.

## Worked production example

Use the Sharda–Avdhesh home example only as a method example, not universal project facts. In the visible conversation, the approved visible design is a modest old mud-brick/plaster house, window left, wooden door centre-right, one neem and one charpai front-left, clay pot near door, open dusty forecourt and village path/side lane. Scene references must still be verified from the actual supplied script in a new project.

Finalize the master; ask whether an interior is needed and how unseen reverse surroundings should be designed. Set a ground origin in the forecourt. Create the house shell, actual door/window openings, neem, charpai, pot and both lanes with fixed positions. Make the front/reverse, diagonal, low and top-down views come from that model. Attach any needed room through the same doorway. Keep a clear charpai-to-road route.

Choose forecourt, charpai and lane-junction anchors only if useful. Do not invent multiple photoreal panoramas independently and then call them one world. Preserve the approved village surroundings during seam repairs. Save camera positions and reference IDs so the storyboard workflow can use the same geography.
