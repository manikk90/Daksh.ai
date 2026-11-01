# Persistent learning and research review

## Contents

- Learning scope and storage
- User correction loop
- Scheduled research loop
- Candidate testing and adoption
- Rollback, consolidation and handoff
- Research review response

## Learning scope and storage

Improve the agent's stored instructions, prompts, reference handling and QC from evidence. This is workflow learning; do not describe it as training or modifying the underlying model. The user has authorized periodic relevant research and learning from their corrections. Routine tested internal improvements need no new permission; this does not authorize unrelated projects, account changes, messaging recipients or automatic generation of new scene packs.

Keep reusable lessons in `assets/learning-ledger.json`, backed by this skill's Git persistence. Keep exact scene/output evidence and project-specific state in the authorized project ledger. Do not copy private attachments, credentials or full conversations into the skill. Save concise relevant excerpts, artifact IDs, source links and check outcomes.

Give every lesson a stable ID, source type and evidence, scope, triggering condition, failure description, prevention rule, status, version and regression cases. Scope may be global workflow, tool/interface version, project, location or shot. A cosmetic change for one shot is not a rule for every future location. A user's specified regional look is a project design lock, not a botanical assertion about an entire state.

Before using a lesson, confirm its scope fits the current project/tool and it has not been superseded. Research rules that depend on a vendor model/interface must include that version/availability. Do not reapply deprecated controls after a documented breaking change. Keep fewer useful rules rather than an ever-growing collection of copied advice.

Load only each lesson's current top-level version. `version_history` retains historical snapshots; their embedded prior status/rules are not additional active instructions. Previous chat/schedule records are history and do not revive superseded bindings.

## User correction loop

1. Capture the user's actual correction and the affected plan/image/geometry/tag/version. Distinguish an error from a new creative preference.
2. Inspect available evidence and diagnose the cause: layout, camera, projection, tag/reference binding, material, generated drift, incomplete checking or misunderstood scope.
3. Apply the authorized correction to the smallest affected artifact. Preserve all other locks and retest connected/opposing views as appropriate.
4. Record the local design change in the project manifest. Extract a short prevention rule only at the justified scope; keep uncertainty explicit.
5. Add a reproducible case: input/context, the failure to detect, expected behavior, and an example boundary where the rule should not apply. Store actual test evidence, not an assertion that the agent has learned forever.
6. Save the lesson. At the next applicable task, load it before prompt compilation and check it during QC. If saving fails, retain the correction in the current run and report that persistence is pending.

Honor current explicit user decisions over older preferences. When an older lesson is intentionally changed, increment its version or mark it superseded; do not keep two contradictory active rules. Do not repeatedly ask permission to remember a correction under this already-authorized learning mechanism.

Examples of justified learning:

- Wrong regional vegetation in an approved village shot -> bind the project's approved vegetation/surroundings; do not globally ban that species.
- Reverse stairs climbing in the wrong direction -> derive elevations/run from shared geometry and inspect opposing views; do not assume all temple entrances have the same terrain.
- Cut pillar stumps in a floor image -> preserve physical support geometry; normal framing crops remain permitted.
- An overhead is oblique -> verify the camera's actual top-down orientation; keep oblique overview as a separately labeled view.
- Seam repair changes the village -> preserve world identity during local repair and inspect geometry as well as the join.
- Flat image called interactive -> deliver a working viewer and record an actual interaction test before that claim.

## Scheduled research loop

Use the newer user-specific Location Agent Midnight Learning task `6ada57d13a3c8191b9d598e886ee8f46`, observed enabled on 23 October 2026 with daily `DTSTART;TZID=Asia/Kolkata:20261024T000000`. Its daily 00:00 Asia/Kolkata trigger supersedes the older shared 23:00 binding for this skill. The weekly research branch is Monday 00:00 IST, meaning Sunday night ending, not calendar-Sunday 00:00. Retain that actual task and exclude Location from the Daksh coordinator run; do not create a second midnight/Sunday task. The prior three-day Location task was confirmed paused and remains in schedule history. A configured task is not proof that any run completed, and a start time is not a guaranteed finish time. Keep unobserved future schedule changes pending.

For each nightly run load the latest skill, lessons and chat checkpoint first; use supported history retrieval and supplied user excerpts since the previous chat review, with focused gap/conflict queries only where needed. Deduplicate against saved lessons. Distinguish direct excerpts, retrieved summaries, prior assistant assertions and query restatements. Record covered window, source anchors, inaccessible media, unresolved prior coverage, adopted/deduplicated/pending lessons and actual save outcome in `chat_review_checkpoint` and chat review history. A covered window is not an exhaustive archive scan. Preserve previous checkpoints and unresolved evidence; do not invent per-chat watermarks. Chat-only or no-change reviews do not advance `last_successful_review` for web research.

Only the Monday 00:00 branch, Sunday night ending, performs the scheduled internet review below; other nights review accessible chats without live web research unless separately requested. Use the scheduled local date for delayed runs, rather than the later execution date, when selecting this branch. The task's observed configuration is the source of scheduled execution, not a sentence in this skill.

Load the latest skill/lesson ledger and review checkpoint. Browse developments since the previous successful review; on the first review, examine a reasonable recent window and existing authoritative baselines. Keep release/event/documentation dates separate. Undated baseline documentation is not a new announcement.

Research only subjects with concrete location-continuity impact:

- Reference fidelity, camera-guided generation and supported depth/edge/mask conditioning.
- Four-view prop reference fidelity, genuine side asymmetry, material/detail preservation and shared asset identity between studio photos and scene placement.
- Consistent novel views, multi-view environment creation and camera calibration.
- Renderable 3D blockouts, shared scenes, transforms and scene/asset interchange.
- 360/equirectangular/cubemap generation, seam/pole checks and interactive viewers.
- Spatial/appearance QC, versioned references and repair methods.
- Relevant architectural/region research workflows where they solve current recurring mistakes.

Prefer official documentation/changelogs, original papers, reproducible repositories and direct demos with inspectable claims. Inspect the actual source. Treat vendor claims, experimental research and available tool capabilities separately. Do not adopt viral posts or marketing claims as verified techniques. Do not infer user's account access from a public launch.

If no useful change is verified, record a no-change review with sources/date and leave rules intact. Avoid padding the review with general AI news or repeatedly presenting unchanged baselines. Keep pending candidates for future testing without claiming they improved output.

## Candidate testing and adoption

For each candidate record problem, proposed rule/change, exact source/date, applicable interface/version, expected benefit, test conditions and observed result. Compare against the current workflow on a relevant case; maintain master design and all other variables. Use text/structural tests, available local rendering or inspection of already authorized outputs as appropriate. Do not create paid generations or new location packs merely to fill a research review.

Test both the failure case and a boundary case where the candidate must not alter behavior. Retest known failures in `assets/learning-ledger.json`: exact tags, relative world positions, stair levels, overhead labeling, shared boundaries, seam identity, viewer claims and versioned approvals.

Adopt a candidate only with direct user authority for its exact scope or supporting primary-source evidence plus a passed relevant test. Documentation can verify a syntax/capability rule; a quality/performance improvement needs observed comparison. Label the type of validation precisely. If evaluation is unavailable, keep the candidate pending; do not invent improved percentages or test outputs.

Apply the smallest targeted instruction/prompt/QC change. Run skill validation, learning-ledger validation and relevant manifest/behavior tests. Independent QC may use a scoped worker when authorized and available; do not pass a desired PASS. Commit only this skill's changes and push the current Skills branch. Treat successful push/materialization as the completed save, not a local edit or task narrative.

## Rollback, consolidation and handoff

Keep candidate/lesson status as pending, active, superseded or rejected, with version and evidence. If a new rule introduces a regression, restore the prior rule/version and mark the candidate rejected with its observed failure; preserve user's design locks. Do not force-push or roll back unrelated skill commits.

Consolidate repeated lessons by trigger and scope, preserving evidence and regression cases. Link a superseded rule to its replacement. Keep source novelty checks so each review does not adopt the same update again. Record successful review date, sources, adopted/pending changes, validation type and save outcome in the ledger.

If a scheduled runtime lacks skill-write/Git access, provide the exact scoped proposed patch or rule, source and test result in the task response, marked unapplied. On the next location-agent invocation, retrieve that saved task result only through supported authorized access, revalidate it against the current version and persist it. Do not claim automatic installation during the unavailable run. Update the review checkpoint only for work actually performed and saved.

## Research review response

Return a short Hinglish update: reviewed window; useful verified sources; adopted changes versus pending candidates; actual tests and save status; one practical effect on location production. Keep it brief when nothing changed. Do not notify Slack/email or other people unless separately instructed. Do not claim all user feedback was read if only the current run and saved ledger were available.
