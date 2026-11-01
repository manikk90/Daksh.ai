# Continuity QC and repairs

## Evidence and status

Keep source/tag QC, manifest structure, 3D layout, final appearance, delivered pixels and viewer testing separate. PASS requires an executed relevant check with evidence. FAIL identifies an observed mismatch. PENDING identifies an unexecuted or unresolved check. N/A needs a scope reason. Tool success, a prompt description or a prior assistant statement is not a PASS.

The structural validator checks the manifest contract and references. It cannot determine whether a photograph matches geometry, whether a path is clear, whether a reconstructed wall is accurate, or whether a viewer works. Run those checks separately.

Populate `required_output_ids` with the authorized deliverables at coverage planning. Keep camera/anchor outputs in `outputs` even when planned, so a missing requested artifact cannot disappear from the completion count. For each executed QC record set `id`, `category`, `status`, `evidence`, `required` and `output_id` when applicable. An approved final image needs relevant tag, geometry/appearance and file checks; a requested interactive panorama also needs executed viewer QC. Do not reduce these checks to one generic PASS.

## Checks by stage

| Stage | Inspect | Failure examples |
|---|---|---|
| Master | Script requirements, visible architecture, count, route, reference identity | Wrong regional vegetation, extra idol, blocked walkway |
| Blockout | Matching master camera, building silhouette, scale, coordinates, openings | Added window, wrong depth, staircase going wrong way |
| Connections | Both sides of shared opening/steps, elevations, adjoining environment | Door leads to unrelated room, discontinuous landing |
| Camera render | Pose, lens/sensor convention, occlusion, foreground/background | Camera inside wall, false top-down, accidental mirrored view |
| Final image | Compare to exact camera render and appearance master | Moved neem, enlarged charpai, vanished well, extra door |
| Prop photos | Four true sides, neutral grey, identical asset/state, scale and detail | Mirrored side, duplicate angle, different strap/hardware, cropped tip |
| Angle set | Opposing and neighboring views, shared landmarks and material identity | Correct-looking singles that disagree as a set |
| Scene route | Start/end surfaces, passage, contact heights, actor scale | Invisible support, blocked exit, child/adult scale change |
| Panorama | Anchor placement, projection, wrap, poles, actual world surroundings | Sky stripe, floor pinching, duplicated house, changed village |
| Viewer | Actual image loads; drag/zoom and full rotation work; narrow width | Flat bitmap, inverted look direction, blank canvas, seam at wrap |
| Delivery | Files decode, dimensions, names, versions, durable save | Truncated PNG, incorrect 4K claim, stale output in approved set |

Use overlays with aligned camera references where possible. Compare landmark positions, silhouettes and occlusion rather than expecting all textured pixels to match a gray blockout. Inspect significant texture/detail locks against the approved appearance reference. Keep any numerical alignment metrics tied to an actual recorded method.

## Critical failures

Do not deliver an approved pack with any of these unresolved:

- Unauthorized master/reference/tag change.
- Missing required zone or scene route.
- Changed opening/step/object count or a shared boundary that does not connect.
- Camera-dependent world mirroring, misplaced key anchor or impossible floor level.
- Different surroundings in a connected reverse view.
- “Seamless” claimed without wrap/pole checks, or “interactive” claimed without a working viewer.
- Essential camera/frame mismatch hidden by blur, crowd or crop.
- Corrupt deliverable or unsupported resolution/save claim.

Minor texture differences still need a specific note when they remain. Promote them to critical if they affect hero detail shots, story clues or matching landmarks. Do not invent an allowed percentage of drift.

## Repair loop

1. Record output/view/version, failed criterion, visible evidence and dependencies.
2. Determine whether the cause is geometry, camera, scene state, material, asset/tag binding or generative drift.
3. Repair the actual cause. A wrong camera render needs a camera fix; an accurate render followed by a shifted door needs a final-image repair.
4. Preserve approved architecture and stable IDs. Change the design only if the user authorizes that change or it falls within delegated unapproved design scope.
5. Regenerate the smallest affected set; do not launch dependent generations from a failed image.
6. Inspect the repair plus its relevant opposing/adjacent view and boundary.
7. Mark accepted, superseded and stale files explicitly. Update status and save.

Avoid repeated identical requests when the same error persists. Diagnose the constraint, reduce competing prompt detail, supply a tighter supported reference or switch to a supported direct render. If still limited, report exactly which property remains unverified without overstating completion.

## Panorama inspection procedure

Inspect a horizontal wrap by showing the original edge join in the middle of an offset inspection image where supported. Test a perspective view through that join, zoomed enough to reveal geometry and exposure discontinuities. Look straight up/down to check pole artifacts. Look back to the approved house/temple landmarks to ensure the repair did not change the world.

Run a full 360-degree drag/turn cycle, vertical look and zoom in the actual viewer. Verify correct initial landmark orientation and narrow mobile layout. Save the test result or screenshot/trace path. If runtime inspection is unavailable, record PENDING instead of inferring success from static code.

Use image-generation tooling for generative repairs according to its rules. Format conversion, texture offset and projection inspection do not justify replacing the approved environment. Keep diagnostic files distinct from final output.

## Completion report

State the smallest useful result: accepted master/version, requested versus delivered views/zones, actual 3D versus schematic status, requested panorama/interaction test status, significant pending items and direct deliverable access. Do not bury a critical failure under “all complete.”
