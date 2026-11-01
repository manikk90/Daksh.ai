# Prompts, reference binding and directing handoff

## Master-image prompt

Use available image-generation tools for photographic assets. For local references, inspect them before passing them according to the tool's supported reference mechanism. Do not use fabricated image paths or substitute similar assets.

Build one production prompt from:

```text
One [aspect ratio] photorealistic overall location photograph of [location], for [verified project/scene or user brief]. Preserve [approved reference identity, if any]. Architecture: [building scale, silhouette, openings, roof, materials]. Spatial layout: [key objects and relative world positions]. Scene support: [clear routes, thresholds and contact surfaces]. Surroundings: [required approach/reverse context; mark new design in the manifest]. Camera: [one readable viewpoint, height, direction and lens intention]. Lighting: [time and motivated light direction]. Empty environment unless specified; clear geometry, realistic material detail. Avoid [scene-specific likely errors]. Requested output [dimensions if supported; verify result].
```

Do not render explanations, tags, UI panels, floor-plan lines or dimensions into the master image unless requested. Keep generation prompt text separate from approval and uncertainty notes.

## Angle-reference prompt

Bind reference roles, not an unlabeled collection:

1. **Geometry/composition target:** exact camera render from the current shared scene.
2. **Appearance reference:** approved master and relevant material/detail assets.
3. **Connection reference:** shared opening/stair/boundary when visible.

Use:

```text
Generate one [view ID] image of [location/zone] from the supplied camera reference. Preserve the reference camera composition, building silhouette, opening counts, fixed object positions, scale and occlusion. Match the approved appearance reference for [materials and asset identity]. Visible here: [camera-derived visible elements in foreground/midground/background]. Camera: [pose/lens/aspect intention]. Light/state: [locked preset]. Change only visual finish where requested. Avoid [specific drift: relocated tree, extra doorway, mirrored layout, changed stairs, duplicate prop, invented background].
```

Use supported geometry-guidance inputs if available; record which were actually passed. If a tool accepts only images and text, disclose that it is reference-guided and still requires visual layout inspection. Do not mention a control channel that was never supplied.

Keep prompts for location stills to one instant. Scene movement requirements determine the layout but do not become multiple actor time states inside an empty reference image.

## Panorama generation and repair prompt

For actual 3D render, use camera settings and geometry rather than an image prompt. For an AI-only draft, request one full-sphere 2:1 equirectangular texture, exact fixed anchor, single scene, stable landmark positions and continuous wrap/poles. Record that it remains a draft until checked.

For a seam repair, identify the failed region, preserve the approved surroundings and all asset IDs, and repair the join locally. Offset the texture for inspection where supported, without altering world identity. Never delete buildings, add a new boundary wall, mirror the village or relocate a tree to make the seam simpler. Reinspect original and repaired geometry, wrap and poles.

## Tag/asset mapper responsibility

Maintain exact strings: approved location tag, sublocation tag, surface/view tag and prop tag. Keep internal asset IDs separate from generation-platform tags. A proposed tag must not be described as installed or approved.

For each camera record both visible asset IDs and their verified tag bindings. Include partial objects, foreground occluders and reflections when relevant. Do not add an out-of-view shrine merely because it belongs to the same complex. Keep geometry version, reference file and tag agreement independent of visual similarity.

Build the visual prompt and actual reference-role inputs from that camera/frame-local inventory, not the whole scene/global register. Include only the actual relevant visible entities and exact selected location/surface; remove stale other-frame cast, props, crowd and alternative location tags from visual text, Refs and attachments. Review untagged prose as well as @tags. An offscreen character/bag does not belong in visual Refs to state absence; keep such continuity separately. An explicitly on-frame crowd and partial/reflected owner remain included. Requested offscreen dialogue/sound and its exact source token belong in an audio handoff without adding a visual subject. The corrected 23 October cart-only frame uses exactly `@nandu-s-cart` and `@village-alley.ground`; separate Nandu-plus-cart frames retain their own actual inventory. Never normalize location aliases or invent an unresolved cast tag.

Never rename `.background`, `.front-wall` or `.left-side` to fix an interpretation error. Explain and map the tag's actual view direction. If a tag/source conflict is unresolved, preserve existing locks and mark tag QC PENDING; resolve before reference-dependent generation.

## AI Native Director handoff

Use a compact record:

```text
Location/version: [ID; geometry/material/state versions]
Scene coverage: [verified scenes/zones and remaining needs]
Master: [actual asset, approval evidence]
Tags/assets: [exact mappings and pending bindings]
Camera: [IDs, positions, targets, lens/sensor, height, aspect]
World locks: [objects, dimensions, connections, elevations]
Movement: [entry/exit route, contact surfaces, supported clearances]
Occlusion/reveal: [what each camera can/cannot see]
Lighting/state: [preset; door/prop states]
QC: [structural, tags, geometry, appearance, viewer; evidence]
Unresolved design: [hidden/proposed areas and capability limits]
```

Pass immutable environment locks into still and video shot prompts. Let the director determine actors, emotion, dialogue, hand/prop ownership, action axis and timing within this geography. Return an impossible route or camera position for revision instead of moving architecture silently.
