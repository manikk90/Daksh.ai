# Shared spatial contract

## Contents

- World coordinates and evidence
- Objects, appearance and scene state
- Connected zones and openings
- Coverage boundary and movement
- Cameras
- Panorama anchors
- Changes and tolerances

## World coordinates and evidence

Use metres and a right-handed world: +X east, +Y north, +Z up, unless the existing project already uses a documented convention. Put origin on the ground in a useful central open area. Keep the origin stable after lock; a panorama anchor is a camera location, not a new origin. Record whether compass orientation is geographic evidence or a design convention.

Store all object and camera positions in world coordinates. If the modeling application uses local transforms, resolve them to this world before export. Keep parent relationships for ownership without assuming a second coordinate convention. Never mix local and world positions silently.

For each significant asset record dimensions, pivot convention, rotation, material reference, source, design status and exact asset/tag. Treat measured, estimated, proposed and approved scale differently. A single photograph often cannot establish depth or hidden faces uniquely. Maintain uncertainty until the layout is adopted as a production design.

## Objects, appearance and scene state

Give each physical object a stable unique ID: wall, opening, threshold, steps, roof, window, neem, charpai, well, railing or altar. Do not add duplicate geometry because an asset belongs to two zones. Reuse one material and shape definition across all cameras.

Define real openings in the walls when a camera or actor must pass or see through them. Door surface, doorframe and wall opening are related but different physical components. Give the assembly a shared ID that both sides use. Model thickness, sill/threshold level and swing where relevant. State whether a door is closed/open per scene preset.

For stairs record start/end elevations, riser/tread count and dimensions, run direction and landings. Separate temple gate steps from shrine steps. Check that the ascent/descent direction in a reverse is derived from geometry, not the word “reverse.” For overheads, use a camera looking straight down; label oblique overview separately.

For appearance, lock large material regions and distinctive landmarks before small decorative texture: exposed brick patch, broken parapet corner, door crossbar, one shuttered window, canopy/trunk shape. When closeups matter, use explicit detail assets. A coarse blockout cannot determine every carving or crack; do not label detail matching as verified unless inspected against its reference.

Keep two state layers: persistent architecture/assets and scene-specific changes. Encode lighting, door angle, moved prop and crowd configuration in a state preset. Do not bake an actor into the empty location master or force a furniture position to remain fixed when a scene explicitly moves it.

## Connected zones and openings

Represent sublocations as regions within the shared scene with stable zone IDs, memberships and parents. Distinguish:

- **Same-place views:** different cameras seeing one area.
- **Attached sublocations:** rooms, stairs, courtyard and lanes joined physically.
- **Separate story locations:** do not assign shared geometry without evidence.

Every physical connection records the two zone IDs, one shared boundary/opening object, and endpoints in the same world coordinates. For a doorway endpoint pair, the points must coincide within the documented assembly tolerance; floor/step transitions remain explicitly modeled. A corridor or stair route can have different endpoints connected by a path, not a false coincident-doorway assertion.

Save opening width/height, boundary orientation, floor elevations and transition type. Keep both sides' materials, scale and visibility consistent. A shrine's interior doorway must map to the same entrance seen from the courtyard. Door and portal centrelines are useful QC landmarks.

Use records like these as shapes, not project facts; replace example IDs and values from the approved layout:

```json
{
  "object": {"id": "shared-entry", "position_m": [0, 0, 0], "dimensions_m": [1.2, 0.25, 2.1], "rotation_deg": [0, 0, 0], "pivot": "bottom-centre", "parent_id": null, "design_status": "proposed", "material_ref": "approved-door-detail"},
  "zone": {"id": "room", "parent_id": null, "object_ids": ["shared-entry"]},
  "connection": {"id": "yard-room", "type": "opening", "from_zone": "yard", "to_zone": "room", "shared_object_id": "shared-entry", "from_point_m": [0, 0, 0], "to_point_m": [0, 0, 0], "tolerance_m": 0.01}
}
```

Add a route record with `id`, `points_m` and its actual clearance/contact evidence. Record external image files separately from geometric dimensions. Dimensions of a bounding box do not replace an opening mesh or a collision check.

## Coverage boundary and movement

Use a finite boundary around required camera/actor paths plus visible foreground, background and adjoining areas. Model near occluders and geometry in shot sightlines. Include enough side/rear geometry for planned diagonals, reverse angles and height changes. Avoid an infinitely large set when only one house and adjacent streets are required.

Record important movement paths as world points plus start/end zones, clearances and contact surfaces. Check passage around furniture, through openings, across thresholds and up/down steps. Use actor scale references and required crowd width from the brief; do not invent numerical clearance standards as universal facts.

Track moving props and background extras separately from permanent anchors. At a blocking handoff, give the director a supported path, floor levels and occlusion opportunities, not a vague direction such as “towards the temple.”

## Cameras

For each reference view record:

- Stable camera/view ID, zone, explicit purpose and exact existing tag if any.
- Projection: perspective, orthographic or equirectangular.
- World position and target, documented up vector/roll, clipping.
- Lens focal length, sensor width and sensor fit for perspective; ortho scale for orthographic.
- Aspect ratio and requested/actual output pixels.
- Light and scene-state preset; visible and intentionally occluded asset IDs.
- Geometry/material/master version, render path and downstream dependencies.

Store target-based pose or a documented orientation representation consistently. With the adopted convention, top-down uses target below the camera; use an appropriate horizontal up vector, avoiding collinearity. A viewpoint name is not its orientation: derive screen-left/right from the actual camera. An actor's action axis is a separate editorial constraint supplied by AI Native Director.

When importing reconstruction/research camera poses, record source pose direction, quaternion order, camera axes, source units and source-world-to-project alignment before using them. For the documented COLMAP `images.txt` image pose only, `(qw,qx,qy,qz)` is a Hamilton world-to-camera rotation and `t` is not camera position: derive `C=-R^T t`. Camera-local axes are right/down/forward; derive visual up from negative camera Y, then apply a documented world-alignment transform to centres, directions and geometry consistently. Do not assume SfM coordinates are geographic or metre-scaled, guess `xyzw`, or reuse this rule for unresolved rig/body or camera-to-world poses. Keep missing alignment/scale/landmark verification pending; never move approved architecture to accommodate an import error. The optional read-only helper in `production-runtime.md` checks arithmetic only. Source: [COLMAP output format](https://colmap.github.io/format.html#images-txt), baseline documentation checked 2026-10-20, not a new release or measured quality improvement.

For manifest perspective cameras use `id`, `zone_id`, `position_m`, `target_m`, `up`, `projection`, `lens_mm`, `sensor_width_mm`, `sensor_fit`, `aspect`, `light_id`, `state_id` and `visible_object_ids`. For an anchor use `id`, `zone_id`, `position_m`, `zero_heading_deg` and optional `panorama_output_id`. For outputs use `id`, `status`, `path`, camera/anchor ID, `pixels`, geometry/material/state versions and `depends_on_output_ids`. Keep `planned` outputs before generation; advance only after inspection.

Pick lenses for a readable location reference, not shallow-focus actor portrait style. Keep geometry QC references sharp enough to see anchors. Save cinematic focus/blur as a separate shot choice so it cannot hide missing or incorrect geometry.

For calibrated pinhole references, bind pixel intrinsics `K` to the exact source resolution and preprocessing record. Resize/crop/padding changes pixel coordinates, not world geometry: record the actual source-to-output pixel map `A` and derive `K_output = A K_source`. For crop-then-scale with origin-scaled coordinates, `fx'=sx*fx`, `fy'=sy*fy`, `cx'=sx*(cx-left)+pad_x`, `cy'=sy*(cy-top)+pad_y`; other resamplers can require pixel-centre offsets. Do not guess the convention or reuse stale intrinsics merely because lens/pose or output dimensions match. Preserve the original and its approval; version the processed derivative. Keep alignment pending when preprocessing/calibration is unknown. Do not apply this pinhole rule to equirectangular, fisheye, undistortion or generative reframing; those require their own mapping/model. See the read-only helper in `production-runtime.md`. This is a mathematical consequence of the [OpenCV 4.13.0 pinhole projection and resize documentation](https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html), checked 2026-10-17; it is baseline documentation, not a new release or measured image-quality gain.

## Panorama anchors

Place anchors in useful accessible positions at documented eye height: courtyard centre, charpai side, gate landing or sanctum. Keep them away from geometry intersections. Each anchor records position, zero-heading/longitude orientation, camera height, world version, state/light preset and render provenance.

Render full-sphere equirectangular textures with 360° horizontal and 180° vertical coverage and a 2:1 canvas. Other panoramic formats need their own explicit projection. Set orientation for a recognizable landmark and maintain it across viewers. Do not stretch a normal wide-angle photo and call it equirectangular.

Treat a panorama as a rotational view at a fixed point. Changing anchor requires a separately rendered view. Reprojecting or cropping a single panorama does not recreate translated viewpoints or hidden surfaces. A clickable tour moves between anchors, while an actual 3D viewer can move cameras through the geometry; label the mode accurately.

Prefer anchors from the shared scene. AI-only panorama drafts need separate layout, wrap and pole verification. Assess image resolution by actual visible detail after viewport projection, not the width number alone.

For an interactive viewer, include the actual texture and working touch/drag plus zoom. Verify initial heading, up/down orientation, full wrap and layout on narrow screens. Test the seam in perspective, not only as a flat image. A seamless join cannot validate that all surroundings match the master.

## Changes and tolerances

Before comparing renders, document useful tolerances for that set and camera: anchor position, silhouette, door/step count, actor scale and image alignment. Define numeric image tolerances only when the camera is calibrated and the method is actually computed. Do not invent a similarity percentage from visual inspection.

Keep stable object IDs while increasing geometry/material/state versions. Record who authorized the change and its scope. Determine affected outputs through visibility, connection and dependency records. Mark those stale; regenerate required views and anchors, then inspect the corresponding opposing/boundary views. Preserve unaffected approved files.
