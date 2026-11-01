# Production runtime

## Route, reuse and timing

Use direct response for micro-edits, scoped execution for one asset/zone and full execution for new connected worlds. Reuse inspected, unchanged sources and active approvals. Retrieve only the scene/location records needed. Read all relevant fields once, batch independent checks and generate geometry-dependent views after their sources pass QC. Never run diagnostic or history tools merely to fill the workflow.

Populate `attempts` with actual `id`, `output_id`, `phase` (retrieval/planning/generation/qc/repair), `elapsed_seconds`, `result` (PASS/FAIL), `failure_signature` on failure, `reference_versions` and `method`. Do not invent durations. Use `location_runtime.py telemetry manifest.json` to locate observed bottlenecks. Compare equivalent tasks before claiming faster or better performance.

After two consecutive attempts with the same output failure signature, change the relevant camera, reference binding, prompt constraint or supported method before another attempt. Do not repeat the same generation indefinitely. If no supported alternative remains, preserve approved work and report the specific blocked deliverable. This is not permission to abandon other authorized work.

## Reference register

For each source store `id`, `path` or recoverable artifact ID, `version`, `role` (appearance/geometry/connection/colour/detail), `status` (proposed/approved/superseded), `approval_evidence`, optional `sha256`, related `zone_ids`, camera orientation and inspection evidence. A hash proves file identity, not approval. Never invent a verified asset binding from a similar image. Bind `reference_ids` on cameras and outputs. If the exact source is unavailable, recover it or mark matching pending; continue independent work.

## Scene coverage and Director handoff

Add one `scene_coverage` row per required action/shot purpose: `id`, `scene_id`, `action`, `surface_ids`, `route_ids`, `camera_ids`, `output_ids`, `excluded_object_ids`, `feasibility_status`, `feasibility_evidence`. Include actor scale/contact needs, reveal/occlusion constraints and action axis when supplied. Do not invent scene IDs for brief-only work; use explicitly named brief IDs with provenance instead. Check framing and walkability in the source scene; a declared visible-object list is not a raycast. Record impossible cameras/routes and revise within delegated design scope without moving approved architecture silently.

Run `python scripts/location_runtime.py audit manifest.json` in addition to the existing validator. Its pending results remain unverified, even if structure passes. Empty draft fields are allowed; a delivered claim cannot hide pending coverage checks. Hand the Director the scene row, source versions, supported camera and route, contact surfaces, exclusions and outstanding checks.

## Lighting and state

Each light preset records `id`, world-space light direction, design time-of-day, source type, white balance Kelvin, exposure reference ID, intensity convention and shadow intention. Distinguish estimated/design light from measured values. State presets bind `light_id`, door angles, movable props and crowd configuration; cameras must use matching state/light. Create day/night variants only when requested, preserving architecture and versioned material identity. Wireframe helpers do not implement lighting: inspect actual beauty renders or generated images for shadow direction, exposure, colour and practical light sources.

## Shared blockout execution

`python scripts/location_runtime.py blockout manifest.json --out /absolute/diagnostic-directory`

This dependency-light branch exports a real `blockout.obj`, source `scene.json` and wireframe PNG cameras from the same solid-box geometry. Explicitly set objects to `geometry_kind: box`, `pivot: centre`, positive dimensions and Z-only rotation. Decompose walls around openings into jamb/header solids; do not export a solid wall across a doorway. The helper refuses unsupported primitives rather than pretending to model trees, carving or doors. Perspective wireframes require horizontal sensor fit; orthographic scale is horizontal width. Use the existing validator first.

Use the mesh in an available real renderer for occlusion, materials and accurate beauty/panorama rendering. This helper has no hidden-surface removal, near-plane edge clipping, collision or photometric lighting. Wireframes are geometric diagnostics, not final location photos, calibrated reconstruction, master-match verification or a free-roaming viewer. Inspect the matching-master camera before dependent packs. When a required renderer is unavailable, keep the actual verification level reference-based; do not mark `model.master_match` PASS because an OBJ exported.

## Visual comparison

`python scripts/compare_views.py reference.png candidate.png --output-dir /absolute/diagnostics [--landmarks points.json]`

Use only aligned same-camera images at equal dimensions. Preserve originals. The helper creates overlay/difference diagnostics and optional landmark displacement. Landmark format: `{"reference":{"gate":[0.2,0.4]},"candidate":{"gate":[0.23,0.44]}}`; coordinates are normalized image positions, with identical point IDs. Different viewpoints need geometric correspondence first; do not compare raw pixels as fidelity. Exposure/material changes can increase pixel error without geometry errors. No reported statistic is an automatic visual PASS or similarity percentage. Inspect overlays and final images for object/step counts, silhouette, framing, reference colours and stable landmarks; record actual evidence and limitations.

## Calibrated image preprocessing

For a known COLMAP `images.txt` image pose, run `python scripts/inspect_colmap_pose.py pose.json`. Example input: `{"format":"colmap-images-txt-world-to-camera","qvec_wxyz":[1,0,0,0],"tvec":[1,2,3]}`. Expected source-world camera centre is `[-1,-2,-3]`, not `[1,2,3]`. This diagnostic returns centre and camera directions in the source frame; it does not import a scene, infer metric scale/geographic axes, resolve rig/body transforms or certify matching. The explicit convention is required; input quaternion must be unit within rounding tolerance, with normalization reported. Bind the subsequent project-frame/scale mapping and landmark checks separately. Existing project-native cameras need no conversion or new approval.

Run `python scripts/transfer_intrinsics.py record.json` only when known pinhole calibration and the actual pixel map exist. Input example: `{"camera_model":"pinhole","source_pixels":[1920,1080],"output_pixels":[960,540],"K":[[1000,0,960],[0,1000,540],[0,0,1]],"pixel_transform":[[0.5,0,0],[0,0.5,0],[0,0,1]],"pixel_convention":"u_out=0.5*u_in; v_out=0.5*v_in"}`. The read-only report transfers intrinsics through explicit positive scale/translation. Crop/padding and half-pixel offsets must be supplied in that map; dimensions alone cannot establish it. This helper neither estimates calibration nor checks that the caller's map matches actual pixels. It rejects unsupported camera models/rotation/warps and never resamples images, changes approved geometry, or certifies visual alignment. Keep unknown preprocessing pending; rerender from the shared scene when a genuinely new viewpoint is needed.

## Change propagation

`python scripts/location_runtime.py impact manifest.json --kind object --ids tree-id`

Supported kinds: object/reference/light/state/prop/camera/output. Use visible and `boundary_object_ids` on cameras, reference bindings and output dependencies. Register scene prompts as outputs too, so image changes invalidate downstream prompts. Review `unmapped_output_ids`; incomplete visibility mapping cannot establish unaffected status. Add opposing and boundary cameras explicitly. Stable global geometry versions remain conservative: if the existing validator requires refreshing all approved outputs after a global version change, revalidate/rebaseline unaffected outputs with evidence rather than silently relabeling their versions.

`python scripts/location_runtime.py invalidate manifest.json --kind output --ids source-id --out revised-manifest.json`

This writes a separate reviewable manifest, marks affected generated outputs stale and their QC pending, and invalidates their reviews. It never deletes files, approves changed geometry or overwrites the source manifest. Apply authorized design/version changes separately, then regenerate and inspect the affected views plus connected boundaries. Bind approval to exact changed versions.

## Custom prop layouts

Explicit user layout overrides default four separate sides. For custom requested angles store `custom_view_evidence`, exact `view_order`, and each view's `angle`/`output_id`. A combined sheet uses `delivery_layout: combined-sheet` and unique `cell_id` per view; multiple views may bind the same image output. Keep source, prop-version and final image checks. Extra driver/macro views do not silently replace requested exterior views. Default four-side packs retain their existing validation.


## Box visibility and route checks

Run the existing manifest validator first, then use:

`python scripts/spatial_checks.py visibility manifest.json`

This casts camera rays to a supported target box's centre and eight corners, with frustum checks for horizontal-fit perspective cameras. Supply `probe_object_ids` or the camera's existing `visible_object_ids`; the helper never changes visibility locks automatically. Opaque, collidable boxes occlude rays; set `opaque: false` for glass and `collidable: false` only for deliberately omitted solids. A box proxy for foliage is approximate and needs its own documented geometry. Unsupported geometry remains pending. Nine blocked/out-of-frame probes cannot prove an entire object is invisible; use a proper scene renderer for exact image coverage. Never mark final visibility PASS solely from probes.

`python scripts/spatial_checks.py routes manifest.json`

Route records add `actor_radius_m`, `actor_height_m`, `points_m` (feet positions) and `support_object_ids`. Use actual project scale evidence; do not invent standard body dimensions. Each route segment is tested continuously against Z-rotated boxes expanded by a square horizontal actor envelope and vertical height, avoiding sample-step tunneling through thin obstacles. The envelope is conservative: corner contact may be a false positive for a round body. Support objects are explicitly excluded from obstacle checks, not verified as traversable. Ground adhesion, stair climb, balance, articulated hands/limbs, vehicles and moving crowds remain separate checks. Never claim a route physically safe/walkable from obstacle clearance alone.

## Prop function and interaction records

For each approved prop store `allowed_states` (such as closed/open/held), moving-part limits with source evidence, `grip_points` (`id`, prop-local position, intended contact, source) and scale evidence. Keep the same design/version across states. Do not infer an unseen mechanism or weight as fact.

Add `prop_interactions`: `id`, scene/shot binding, `prop_id`, `prop_version`, `state`, `grip_id`, `actor_id`, `actor_profile_evidence`, anatomical `hand` (left/right/both/none), optional `support_object_id`, `scale_evidence`, `contact_evidence`. Run:

`python scripts/spatial_checks.py interactions manifest.json`

This detects stale prop versions, undefined states/grips and missing identity/scale/contact records. Record-complete is explicitly not a physical fit PASS. Let the Director control performance; verify rendered grip, hand ownership, body reach, prop scale, support contact and requested moving-part action in actual references/outputs.

## Offline panorama viewer

`python scripts/build_panorama_viewer.py panorama.png viewer.html --title "Location panorama"`

Supply an inspected genuine equirectangular full-sphere texture. The builder checks 2:1 pixels and embeds it into an offline WebGL spherical viewer with mouse/touch dragging, pinch/wheel zoom, arrow keys and reset. It refuses overwriting existing output. No external packages are loaded by the HTML. WebGL/browser texture limits still apply; building HTML does not certify that it loads or works on the user's device.

Test actual image load, full yaw wrap, pole orientation, pitch/zoom controls, reset and narrow-screen layout for every delivered viewer. Use recognizable reference landmarks to verify orientation. A synthetic test proves control implementation only; it cannot certify a real panorama's seam, poles, reference identity or translated viewpoints. Keep viewer checks separate from content checks and save the requested user-facing HTML/texture through the authorized artifact destination. Do not create unsolicited panoramas while updating this skill.
