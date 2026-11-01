# QC evidence contract

Return compact human tables unless structured output requested. Required domains vary by task; unsupported/unavailable evidence is PENDING, not automatically NOT_APPLICABLE.

Envelope:
```json
{
  "run_id": "run-id",
  "scene_version": "scene-v1",
  "artifact_id": "plan-v1",
  "stage": "qc",
  "reviewer": "filmmaking-qc",
  "execution": "independent",
  "reviews": [{
    "domain": "reference_binding",
    "status": "FAIL",
    "evidence": ["candidate input binds superseded asset"],
    "inspection_extent": "text and supplied binding manifest"
  }],
  "findings": [{
    "shot_id": "shot-id",
    "domain": "reference_binding",
    "severity": "Blocker",
    "evidence": "exact source/candidate mismatch",
    "correction": "bind approved current source; preserve tag",
    "recheck": "PENDING"
  }]
}
```

Domains: planning, reference_binding, performance_action, composition_camera, visual, temporal, audio_sync, edit, delivery. PASS requires scoped evidence; generation metadata alone does not verify visible content. `execution` is independent only for a distinct reviewer process; otherwise self_review.

Blocker: essential beat missing, wrong approved identity/source, impossible required contact, wrong scene or premature reveal, wrong requested artifact. Major: meaningful performance/action/camera/edit mismatch or unsupported material output claim. Minor: nonessential cosmetic difference. A repaired artifact has a new version and requires recheck; old PASS does not transfer blindly.

When source evidence is partial, check what can be checked and flag the rest. Do not pretend to measure timing without audio/video. Model-rejection cause remains unknown if not specified. Report omitted content rather than falsely proving complete coverage.

For every executable shot, compare visual text and actual visual reference bindings with a source-derived frame-local required/allowed inventory. A globally valid but off-frame character, prop, crowd or alternate location is still an extra-tag/binding failure. Do not include hidden subjects in Refs to state absence. Preserve actual partial/reflected owners and explicitly on-frame crowd; keep requested offscreen dialogue/sound separate from visual bindings. Use the literal auditor for visible tag omission/extra detection, then check audio roles and attachments manually; a global scene-register allow-list cannot certify this gate.

Use recheck PASS, FAIL or PENDING. Keep resolved findings in the review history; report active findings against the current artifact. Name the requested domains in the handoff scope. A valid partial-domain envelope does not prove that omitted required domains passed; the Director must reconcile the review with the task's required gates.

If returning optional `overall_status`, use FAIL if any reviewed domain fails; otherwise PENDING if any reviewed domain is pending; otherwise PASS when at least one domain passes; otherwise NOT_APPLICABLE. Overall PASS cannot conceal pending media checks.
## Composition evidence

For a composition-bearing task, apply `shot-composition.md` to first-read target, essential secondary evidence, crop/tangencies, physical support and reflected ownership, approved geometry/axis, perception/reveal locks and target ratio. Check movement visibility only when the movement was inspected. A pattern match or attractive frame does not prove beat coverage; an essential unreadable hand/contact is a coverage failure. Preserve separate text, visual, temporal and audio inspection extents.

Check each cell/clip for scene-context or adjacent-beat leakage in prose, tags and actual inputs. Strict source-frame crop, inventory, layout/focus and supplied video endpoints take priority over optional 2S/OTS experiments. A relevant soft shoulder/head edge retains its exact owner; an absent/decorative extra is a failure. Verify the shown location view, preserved axis and readable essential reactions/contacts; blur and a valid tag alone do not satisfy this gate.

## Cast/costume evidence

For a reference-sheet task, apply `cast-and-costume.md` to each requested view and the approved identity/look sources. Name actual cell/view inspection, cross-view identity and outfit defects, anatomical-side/prop support, native output evidence and any requested scene-state tests. Preserve separate specification, binding, visual and approval states. An uninspected view cannot inherit another view's PASS, and a sheet's overall dimensions do not establish per-view 4K. A text-only workflow evaluation does not establish visual consistency.
