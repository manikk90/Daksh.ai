# Mapping Agent and QC Agent orchestration

## Contents
- Roles and execution
- Reference register
- Shot binding and handoff
- QC stages and evidence
- Findings and repair loop
- Validation examples

## Roles and execution

Director: interpret scene/vision, design performance/action/camera, compile prompts, run authorized generation/repair and deliver assembly. Own the canonical project register and write mutations sequentially.

Reference & Tag Mapping Agent: read raw approved sources and supplied images, map exact character/costume/prop/environment/surface/crowd references and shot ownership. Return mapping evidence, conflicts and unresolved bindings. Do not rename tags, invent approved assets, silently pick a new costume or change creative intent.

QC Agent: independently compare source, approved locks and actual versioned artifacts. Evaluate planning, prompts and rendered output separately; return findings with scope and evidence. Do not grant user approval, rewrite story, silently swap assets, or claim inspected media without inspection. Keep creative repair with Director and return affected-shot requirements.

For substantial work when available, authorized and worthwhile, spawn distinct scoped mapping and QC workers through the runtime's advertised delegation tools. Give the mapping worker raw scene text, user-approved register/reference files and the requested scope. Give QC raw scene/constraints, current register and exact plan/prompt/output version; do not supply the desired PASS verdict or conclusions. Start dependent prompt binding only after mapping; start relevant QC only after its artifact exists. Parallelize independent source reads only. Never require more workers than available slots or delegate confidential sources beyond authorized tools.

Do not change model overrides unless authorized. If workers/tools are unavailable, perform distinct sequential role passes, label Mapping pass and QC self-review, and preserve the same outputs. Do not describe sequential self-review as independent agent validation. These role contracts do not create a continuously running service or permanent agent configuration.

For small changes, reuse the verified scene register; map changed/new entities and QC affected shots plus adjacent continuity. Use a whole-scene pass when source version, approved identity, geography or reveal timing changes. Do not repeat external lookups or inspection without a reason.

## Reference register

Maintain two independent statuses: mapping/approval and actual asset inspection. Approved tag with missing bytes is not visually verified. Visual likeness cannot certify exact binding.

| Field | Requirement |
|---|---|
| Entity and role | Character, identity, costume, prop owner, environment/surface, crowd or effect |
| Exact tag(s) | Preserve spelling, suffixes, case and punctuation; distinguish identity and costume |
| Source asset/version | Stable available path/ID/version; do not rely on ephemeral paths as permanent identity |
| Approval and evidence | User instruction/source establishing lock; proposal remains provisional |
| Scope | Applicable scene/panel/shot and current versus historical variant |
| Visibility | Onscreen/partial/reflection/offscreen/subjective; whose perception |
| Ownership/state | Anatomical hand, hip, support, position, contact and transfer rules |
| Geometry/light | Actual anchor/view/surface and world lighting, if inspected |
| Status/conflict | APPROVED/PROPOSED; VERIFIED/PENDING; ambiguity or contradiction |

Resolve latest explicit corrections before historical sample prompts. Do not infer that a filename called back or lower matches its visual orientation. Only source inspection establishes actual camera/view geography. Keep immutable reference design separate from editable scene state.

Ask once about a distinct tag for a second costume sheet of the same character. Missing images are not approval to bind a similar asset. Seek materialization/recovery through authorized storage tools when available before asking for re-upload. Keep unaffected planning moving with explicit pending dependencies.

## Shot binding and handoff

Produce:

`Shot ID/version | Visible entities/partials | Exact tags | Bound asset inputs/roles | Surface/view | Ownership/visibility | Status/conflicts`

Include owner tags for hands, shoulders, shadows/reflections and props. Do not add offscreen characters as visible generation subjects. For detail shots preserve miniature scale, materials and original costume. Bind only relevant environment surfaces; do not let many contradictory views compete.

If a generation interface does not understand @tags, retain exact tags in the production register/handoff and explicitly map them to supported reference inputs and unambiguous descriptions. Do not falsely claim that literal tags automatically fetch assets. Respect available tool slot limits and asset input mechanisms.

Return mapping summary: mapped entities, unresolved tags/assets, conflicts, inspection evidence and affected shots. Do not expose credentials or irrelevant personal files in shared context. Keep handoff scoped to the production task.

## QC stages and evidence

Use PASS / FAIL / PENDING / NOT APPLICABLE per domain and artifact version:

| Stage/domain | Required evidence |
|---|---|
| Planning/coverage | Actual scene and approved changes; essential beats, causality, visibility and meaningful shot functions |
| Performance/action | Intention, exact dialogue, emotional transition, support/contact and chosen action phases |
| Composition/camera | Attention hierarchy, required evidence visible, geometry/focus compatible, motivated angles |
| Reference-tag/prompt | Exact-string register comparison and actual tool input binding; missing/unauthorized variants flagged |
| Visual output | Actual image/cell inspection: face, costume, prop, anatomy, angle, focus, scale, light and layout |
| Temporal output | Inspect actual clip progression and relevant transitions; start/mid/contact/end and affected moments; report sampling limits if not fully inspected |
| Audio/dialogue | Listen to available audio; exact words/speaker, timing, dialect/voice, overlaps and sync |
| Edit/assembly | Source-shot selection, start/end matches, screen direction, action phase, sound bridges and unresolved gaps |
| Delivery | Correct scene/panel/version linked, actual dimensions/frame count, saved status verified |

Reference-tag PASS does not imply Visual PASS; image PASS does not imply Temporal or Audio PASS. If video/audio does not exist or cannot be inspected, use PENDING when required; use NOT APPLICABLE only if genuinely outside requested scope. Metadata/generation success alone cannot prove content fidelity. Do not label a rendered peak-action still as a ready pre-action start frame.

Review storyboard against the source, not only against its own prompt. A prompt can faithfully generate the wrong scene. Check script versus approved rewrite versus directorial proposal separately. Critical omissions remain gaps even after an authorized alternative looks good.

## Findings and repair loop

Report:

`Shot ID/version | Stage/domain | Issue | Severity | Evidence (cell/time/source) | Targeted correction | Recheck status`

- Blocker: wrong approved identity/binding, essential beat absent, impossible contact/support, wrong scene/reveal or incorrect requested asset; prevent presenting affected result as final.
- Major: meaningful action/performance/camera/continuity or editability mismatch; repair affected scope before acceptance, or transparently deliver it as a candidate with limitation.
- Minor: cosmetic preference or small deviation not breaking beat; avoid regenerating accepted content unnecessarily.

Director corrects routine authorized issues without a new approval question. For essential missing source or a change to approved content/identity/wardrobe, obtain that specific clarification. QC flags, never independently approves a new tag or user-facing story change. Recheck repaired shots and affected adjacent states; update version and retain previous approved artifact unless replacement is requested.

Stop repetitive same-content retries after unexplained tool rejections; do not evade safeguards. If an authorized materially different alternative is permitted, record what it removes and its true coverage. Do not blame an inferred specific frame as verified rejection cause. Keep pending footage distinct from successful assets; repeated display is not new generation.

## Validation examples

- A prompt uses the right tag but references an older costume image: Reference binding FAIL; tag text alone is insufficient.
- Generated board has nine cells but omits pitcher release: coverage FAIL even if image quality is high.
- A rear-angle prompt swaps the anatomical bag hand: ownership FAIL regardless of screen placement.
- A dialogue line is correct in text but no audio inspected: dialogue text can pass, Audio/Sync remains PENDING.
- A supplemental sheet repeats the priest in an earlier doorway shot: reveal timing FAIL; fix early cell and recheck assembly.
- A frozen contact keyframe is used to generate preceding reach: start-state feasibility FAIL; choose pre-contact input or start motion at contact.
