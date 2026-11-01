# Four-view prop photography

## Extract and bind the prop

Read the scene/brief and identify the requested props, including hero objects, handhelds, movable furniture and vehicles. Distinguish them from permanent location architecture. Record object/prop ID, exact existing tag, source/approval, scene use, owner/contact, dimensions if known, material, colour, construction, distinctive marks and variants. Do not invent physical measurements from one photograph.

Use the same prop identity in studio references, location placement and storyboard/video handoffs. A charpai shown under the neem must have the same frame, weave and proportions in its four-view studio set. A bag keeps its strap, seams and closures. A vehicle keeps its genuine left/right hardware. Preserve any supplied exact plate text or markings; do not fabricate serials to make the image look detailed.

Separate fixed design from scene state: an open bag, deployed stand, bent/damaged stick or blood-stained fabric can be an authorized variant, not a different unnamed prop. Keep one selected state through all four views. Record any approved design change and stale dependent photos.

## Define the four views

Choose the prop's intrinsic front from the approved reference or its function and record the convention. Use object-relative viewing directions:

| View | Default angle from intrinsic front | Show |
|---|---|---|
| Front | 0° | Full front face and major design identifiers |
| Back | 180° | Actual rear construction, closures, seams and hardware |
| Left | -90° | True physical left profile, depth and left-side features |
| Right | +90° | True physical right profile and right-side features |

Keep upright axis, prop state, camera elevation, scale and reference distance consistent. Use direct frontal/profile views with minimal perspective distortion; do not substitute three-quarter glamour angles unless explicitly requested. An oblique or top detail is an optional additional view. Identical-looking symmetric sides are acceptable if they are correct actual sides; do not invent asymmetry for visual variety.

Keep closure and visible contents as part of that selected state. In the 22 October Purana Jhola brief, the requested old bag has no label/tag artwork, while the tied bundle has only a small knot gap revealing part of a gold necklace. Do not merge those objects, open the bundle fully, expose contents through an unseen reverse or invent a production @tag. Preserve the actual source prop and state across the four neutral-grey views; project/tag binding remains pending until the source establishes it. These details are local to that brief, not defaults for other bags or bundles.

If a 3D asset exists, use it for all views and verify it against the approved source. Otherwise bind the same verified reference and prior QC-passed views to the generation tool and inspect generated geometry; image guidance alone does not guarantee a precise turnaround. Hidden rear details remain a proposed reconstruction unless source evidence or an approved design establishes them.

## Grey-background photographic spec

Use one uniform neutral grey studio backdrop/floor, with no scenery, gradient poster treatment, characters, hands, packaging, comparison objects or extra props unless requested. Allow a restrained natural contact shadow; keep studio equipment and supports out of frame without making the prop physically incoherent. Use soft controlled light, neutral white balance and consistent exposure. Maintain sharp readable material detail throughout the prop, without harsh glare, shallow-focus detail loss, artificial plastic surfaces or exaggerated sharpening.

Keep the entire object visible, centred, with sufficient margin. Preserve proportion and a common scale across views; a side profile may naturally occupy less width. Do not enlarge a thin profile to fill the frame, crop a tall stick's tip, stretch a bike or compress a bag. Use a longer-lens product-photo intention where useful, with restrained perspective; do not claim a calibrated lens if the generator does not provide one.

Default per-view canvas is 1:1 when unspecified; use the existing requested ratio for that prop if established. Request supported high-detail output and verify pixels. Do not claim native 4K from a prompt or describe a low-resolution four-cell sheet as four separate 4K photographs.

Provide four individual image files by default. For a standard four-side combined sheet, use exactly four cells, one per view in Front/Back/Left/Right order. An explicit custom view list/layout overrides this default; register it using the custom-sheet contract in [production-runtime.md](production-runtime.md). Keep per-cell aspect, scale and backdrop consistent; separate cells clearly. Put labels in metadata/filenames unless in-image labels are requested. A combined preview can accompany individual images but must not inflate the delivered view count.

## Approval and execution

For an already approved prop, use the current source immediately. For a new prop, create one design seed and inspect it; reuse the approved location plan's prop design authority where provided. Ask about only an unresolved material design/identity decision. Do not impose a new location plan/master gate on a standalone prop-photo request.

After the design is locked or explicitly delegated, generate the four views without approval at every angle. Reuse the accepted front seed as the Front output when it already meets the grey-background spec; do not count it as a fifth view. Keep unrelated props out of the pack unless the screenplay/approved plan includes them.

Use supported image-generation tools and their reference rules for photographs. Do not replace requested raster photos with schematic drawings. Tool completion does not prove design consistency; inspect the actual outputs before using them as downstream references.

## Prompt template

Use one prompt per primary view when delivering separate photographs:

```text
Generate ONE detailed photorealistic studio reference photograph of [prop ID/exact tag], [Front/Back/Left/Right] view, at [object-relative direction]. Input reference is the approved design; preserve the exact object shape, proportions, construction, material, colour, wear, markings and [selected state]. Show the complete object centred with consistent scale and margins, sharp readable texture and minimal perspective distortion. Plain uniform neutral grey backdrop and floor, soft controlled studio light, neutral exposure and a restrained natural contact shadow. Visible in this actual view: [side-specific features supported by references]. No redesign, mirroring, extra components, cropped ends, hands, people, scenery, labels, collage or watermark. Requested [ratio/pixels if supported; verify actual output].
```

For repairs, name the specific mismatch and preserve the remaining design. Do not require a feature to appear through an opaque object from a side where it is occluded.

## Registry and validation

Add a `props` list to the location manifest; older location manifests may omit it. For an isolated prop pack set `mode: props-only`; its prop-design acceptance replaces a location-master gate. Use stages `prop_draft`, `prop_design_locked`, `prop_views`, `qc` and `delivered` as applicable. Retain the general versioned manifest/output/QC records; do not fabricate an approved location master. Each prop record uses `id`, `version`, `name`, `source_path`, optional `object_id`, `design_status`, `sheet_status`, `intrinsic_front`, `background`, `view_order` and `views`. Set `background` to `neutral-grey`, default `view_order` to `front/back/left/right`, and each view to its `angle` plus `output_id`. For explicitly requested custom angles add `custom_view_evidence` and use that exact ordered angle list. For a single combined image set `delivery_layout: combined-sheet` and unique `cell_id` per view; its views may share the one sheet output ID.

Use `sheet_status: identified` before coverage is registered, `planned` after allocating all four output IDs, `draft` while images are being checked, and `approved` only after all four are accepted. Record each output's `prop_id`, `prop_version`, file path, actual pixels, status and applicable global versions. Add all four to `required_output_ids` when the set is requested. Tags can bind the prop ID or its existing geometric object ID; preserve their exact strings.

Store studio pose records inside the prop's view records with an explicit object-relative coordinate namespace. Keep world camera/placement records separate; never make the grey photo studio a fictional scene sublocation. Optional detail outputs have their own IDs and do not enter the four-view primary mapping.

Run the manifest validator for IDs, required angles, shared version and output binding. These checks do not certify photographed geometry, grey colour, view direction or readable detail. Inspect those visually.

## Prop QC and handoff

Check all four photos together:

- Same silhouette/proportion, thickness, components, materials and selected state.
- Real front/rear/left/right orientation; no mirror shortcuts or duplicate-angle substitution.
- Consistent grey background, photographic lighting/exposure, scale and framing.
- Intact complete object, readable texture/important markings and no extra items.
- Correct visible/occluded asymmetric features; continuous wear and material boundaries.
- Exact asset/tag/version agreement with the prop inside its location.

Repair failed views selectively; a shared design change may require updating all four. Record image QA separately from structural validation. Hand the director the approved prop ID/tag, chosen state, view files, dimensions/scale evidence, grip/contact points and placement constraints. Retain learned prop-specific mistakes at their justified scope.
