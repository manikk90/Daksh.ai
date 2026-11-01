# AI Location Agent controller

## Contents

- Scope and runtime
- Stages and approval gates
- Lead and specialist roles
- Worker handoffs
- Persistent run state
- Revisions and completion

## Scope and runtime

Run the active assistant as the location lead using this skill and available source/search/image/3D/viewer/storage tools. This is reusable agent orchestration, not a hosted service, custom account agent or forever-running background process. Do not create subscriptions, deployments or scheduled work to satisfy this controller.

Select `researched-agent` when explicitly requested. Preserve `master-first` for one-image-first work. A user asking to configure an agent authorizes updating the workflow; it is not automatically a request to generate a new project location. State the distinction concisely when needed without withholding requested work.

## Stages and approval gates

1. **Context:** read the actual screenplay, supplied brief and approved references; record region, period, people/lifestyle, dramatic function, routes, required surroundings, inherited tags and constraints. Mark missing evidence; retain accepted context.
2. **Research:** investigate only unresolved design facts. Build a source-backed shortlist of architectural/material/vegetation cues and what each will change in the plan. Keep factual claims, creative interpretation and proposals separate.
3. **Plan candidate:** produce one recommended design with architecture, zones/connections, near/reverse surroundings, routes, approximate scale, master camera/look, useful view coverage, 360 scope and capability limits. State new design assumptions and the deliverable scope. Keep alternatives limited to a materially different unresolved choice.
4. **Plan approval:** present the concrete plan and ask for the requested creative approval only if not already authorized. Save approval evidence, plan ID/version and allowed production scope. Pending approval allows independent source inventory/mapping but no dependent master generation unless the user explicitly waives the gate.
5. **Master candidate:** generate exactly one main location image from the approved plan. Inspect and repair within that plan. Show the actual result; do not substitute a prompt or claim an unseen image is approved.
6. **Master approval:** bind the accepted image ID/version and dimensions. Preserve accepted features during requested revisions. Approval of the plan does not automatically approve the generated image; approval of a full-image revision applies to that current candidate. Follow explicit user delegation when present.
7. **Remaining layout questions:** ask at most one or two material questions if they were not resolved by context, plan or master. Examples: scene-required interior, exact continuation of a side lane. Skip repeats and waived questions. If a decision would materially change the approved plan, present only that change, not the entire plan again.
8. **Production:** build the shared layout, connected sublocations, camera references, requested images/panoramas/viewer and scene-specific surfaces. For props included in the plan, produce the same asset's four detailed Front/Back/Left/Right studio photos on neutral grey as specified in `props-four-views.md`. After accepted master and resolved essential sources, complete the authorized pack autonomously. Do not ask approval at each angle, prop view or sublocation covered by the plan.
9. **QC and repair:** review exact tags, layout, connections, appearance and requested interaction with evidence. Apply routine authorized repairs and recheck affected dependencies. Never alter locked architecture simply to satisfy a generated error.
10. **Delivery:** save actual final artifacts, present access and truthful verification status. Hand off environment records to the directing workflow. Keep incomplete required items visible.

If a gate requires a pause, name/link the actual skill instruction and quote its relevant gate rule, explaining that it implements the user's requested creative approval. Do not invent another safety or publishing gate. Prior authorization and explicit user overrides take precedence.

## Lead and specialist roles

| Role | Responsibility | Write authority |
|---|---|---|
| Location Lead | User context, creative choice, gates, scheduling, generation, repairs and final handoff | Canonical manifest and approved outputs |
| Context Researcher | Source-backed setting facts, gaps, rationale and regional/period mismatch risks | Read-only findings; no approval or design replacement |
| Spatial Designer | Proposed zone layout, connections, routes, scale and camera coverage | Candidate only unless modeling scope explicitly delegated |
| Asset/Tag Mapper | Exact approved tags/assets, missing sources, per-view binding | Read-only mapping report; lead adopts valid evidence |
| QC Reviewer | Plan/output assessment against raw source, approved design and relevant cameras | Read-only findings; no prompt rewrite, generation or approval |

Do not launch a full team for one door repair or repeat already verified research. With authorized collaboration, delegate independent research/mapping or independent QC where useful. Preserve order: plan before plan QC, exact references before reference-dependent generation, artifact before output QC. Run independent read-only work concurrently where appropriate; serialize dependent image/geometry edits and canonical writes.

Reuse existing Reference Mapper/QC skills when their scope covers location work; discover them rather than hard-coding a changing installed path. Otherwise use the scoped role prompts below. Do not label role passes as separately running agents unless actual workers ran.

## Worker handoffs

Pass only relevant raw source, exact approved references and the candidate/version to assess. Never pass the desired verdict or a prior finding as ground truth. Specify the actual available tools and a read-only scope. Keep credentials and unrelated conversation content out of worker context.

Research task:

```text
Use the location skill's context-research rules for [location/version]. Raw scene/brief: [relevant text]. Approved reference/constraints: [actual sources]. Research question: [specific design gap]. Return source-backed setting findings and unresolved uncertainties for run [ID], location [ID/version], candidate [ID]. Read-only; do not generate assets, change locked design or approve anything.
```

Mapping task:

```text
Map exact approved environment/prop tags and available assets for [view scope]. Raw locks and files: [sources]. Candidate: [plan/camera records]. Return verified bindings, missing bytes and conflicts for run [ID], location [ID/version], candidate [ID]. Read-only; do not rename tags or substitute assets.
```

QC task:

```text
Assess candidate [ID] for run [ID], location [ID/version]. Raw scene/brief: [sources]. Approved plan/master and manifest: [versions]. Candidate artifacts/camera references: [actual files]. Return scoped evidence-based PASS/FAIL/PENDING findings for tags, geometry/connections, appearance and requested viewer behavior. Read-only; no rewriting, generation or new approvals.
```

Use an envelope with `run_id`, `location_id`, `location_version`, `candidate_id`, `candidate_version`, `role`, `status`, `findings` and `evidence`. For each finding record the affected object/view, check, evidence and severity. Record what files were inspected and which domains were unavailable. Reject a report bound to another candidate/version or location version; request the correct scoped recheck. Keep accepted reports in `reviews` and raw report paths if saved. Mark superseded reviews `state: stale`; do not apply their verdicts to the current candidate.

## Persistent run state

Keep production checkpoint state outside this installed skill, in the authorized project destination. Persist:

- Run/mode/location/version and current stage.
- Sources, inspected references, current research findings and actual citations.
- Plan ID/version/path, scope and approval evidence.
- Master ID/version/path, actual pixels and approval evidence.
- Shared objects/zones/connections, geometry/material/state versions and cameras.
- Exact tag register, output/anchor IDs and dependencies.
- Reviews bound to candidates, QC, unresolved issues and next action.

Record approval as `approved` or `delegated`, with evidence from the user instruction, and `approved_version` matching the current artifact's `version`. `pending`, assistant QC or elapsed time are not approval. Do not fabricate user evidence to satisfy a validator. Resume from current state instead of rebuilding an approved set.

## Revisions and completion

For a routine master-image correction within the approved plan, retain plan approval and create a new master candidate; master acceptance stays pending until accepted or delegated. For a changed location concept or connection scheme, increment the plan version and invalidate its approval plus dependent master/outputs. For a final-view drift repair, retain accepted plan/master; update that output and affected dependency checks.

If new research conflicts with the approved design, report a specific optional correction for the user rather than overwriting it. Recheck whether a plan change is necessary at all. Respect stylized or deliberate exceptions as user choices.

Keep plan approval, image approval, structural validation and visual QC distinct. Report real worker use and actual output tests. A passed JSON schema is not a finished agent run or verified architecture.
