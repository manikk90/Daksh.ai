# Daksh Brain: operations and recovery

**Operational design: 7 November 2026.** This is a proposed runbook layered on the repository's existing local controllers and skill sources. Commands identified as existing CLI examples must be run in the correct checkout with actual task files. Other procedures describe behavior to implement and verify; they do not imply that a service, scheduler, model gateway or deployment is running.

## 1. Operator responsibilities

Daksh Brain owns the outcome and final report. `capability-operator` diagnoses current environment/access/tool issues. Domain specialists own their artifacts. `independent-qc` checks outcomes against raw sources. `brain-evals` owns applicable deterministic/evaluation gates. `operations` owns authorized coordination and maintenance state.

One canonical writer owns each shared file or store. Actual host/tool availability determines execution capacity. Keep scheduled maintenance ownership separate from interactive task workers; a role in a registry is not an active timer.

## 2. Preflight before a substantial run

| Check | Evidence | If missing |
|---|---|---|
| Objective and finish condition | Actual requested artifact/count/format and delivery destination | Infer routine choices; ask only for a material essential ambiguity |
| Correct project/repository/account | Current source location, account identity, branch/head and permitted target | Stop dependent mutation and resolve the target |
| Source context | Supplied/authorized sources, versions, exact applicable locks | Retrieve relevant evidence; preserve explicit gaps |
| Skills | Current entrypoint and required resources resolve | Use declared competent fallback or block that capability |
| Tools and connectors | Read-only capability/access probe in current host | Report unavailable operation and continue independent work |
| Local environment | Required runtime/dependencies, disk and permissions where relevant | Diagnose before expensive jobs or broad process changes |
| Permissions | Existing authorization covers the concrete action/resource | Complete authorized preparation; request only genuinely missing authority |
| Budget | Current price/credit info where relevant, remaining approved envelope | Do not treat unknown cost as zero or silently exceed limit |
| Plan | Acyclic dependencies, disjoint writes and actual capacity | Repair plan before dispatch |
| Checks | Artifact-specific acceptance criteria and reviewer capability | Keep required check pending if it cannot run |
| Recovery | Run/effect IDs, checkpoint and bounded retry policy | Establish before non-idempotent or expensive work |

Use the smallest adequate preflight. A one-line supplied-text rewrite needs no full infrastructure audit.

## 3. Current local controller commands

The repository's ledger is a local state controller, not a worker launcher. Copy/adapt the template to the authorized task workspace first; use actual source revisions, locks, write paths and checks. Inspect `--help` in the installed checkout before commands whose options may have changed.

```bash
# Existing memory validation and deterministic eval entrypoints.
python3 skills/daksh/scripts/brain.py validate brain/DAKSH_BRAIN.json
python3 skills/brain-evals/scripts/run_evals.py selftest
python3 skills/brain-evals/scripts/run_evals.py routing

# Existing run ledger: use a prepared task-owned file, not the template itself.
python3 skills/daksh/scripts/orchestrator.py validate /absolute/task/run.json
python3 skills/daksh/scripts/orchestrator.py ready /absolute/task/run.json
```

The schema version 1 ledger accepts exact fields and defined states. Never add proposed runtime budget, hook, API or provider fields directly to it and assume compatibility. Introduce extensions through a versioned adapter/controller change and tests.

For actual assignments, retain the returned assignment token, source snapshots and dependency assignments. Result packets must match them exactly. A finished result includes every declared check once with `pass`, `fail` or `not_run` and evidence. The controller must not accept a failed or unrun required check as a completed node.

## 4. Normal execution loop

1. Resolve objective, authority and current context.
2. Classify the bottleneck as Prompt, Context or Harness.
3. Create a DAG only when task complexity benefits from durable coordination.
4. Probe necessary skills/tools and select capability-based models.
5. Dispatch only ready independent nodes within actual capacity and budget.
6. Persist actual worker/assignment/effect identities.
7. Inspect outputs before accepting result packets.
8. Invalidate dependent work when relevant inputs change.
9. Run appropriate independent QC when available/required.
10. Save/deliver the requested artifact under existing authority and verify the result.
11. Capture an authorized minimal scoped lesson if useful.
12. Report confirmed output, checks, limitations and exact pending blockers.

Keep users informed with useful progress and concrete findings, not repeated unchanged status. Long external jobs should yield/poll within host constraints so user steering and cancellation can be handled.

## 5. Readiness, stop conditions and health

A future deployed runtime should separate liveness from readiness. “Process alive” does not prove that sources, queue, credentials, required models or artifact storage work. Readiness should report only the capabilities needed for the requested operation.

| Signal | Meaning |
|---|---|
| Controller process responsive | Liveness only |
| State store read/write healthy | Can update ledger; not proof of remote effects |
| Capability probe succeeds | Named operation/account/resource works at probe time |
| Dependency artifact current | Required input exists and matches accepted revision |
| Budget available | Reservation fits current authorized envelope |
| Reviewer available | Actual context/modality/tool access can support required QC |
| Delivery readback succeeds | Requested external/local result is observed |

Stop only dependent work for a localized failure. A broken image-generation capability need not stop text packaging; a missing exact reference must stop an output that claims exact reference fidelity. A failed mandatory security/approval hook blocks the gated action.

## 6. Incident severity and response

| Severity | Example | Immediate response |
|---|---|---|
| P0 | Credential exposure, unauthorized side effect or harmful access expansion | Stop affected actions, preserve minimal evidence, notify owner, use authorized containment |
| P1 | Duplicate paid job, wrong-repo mutation, corrupted canonical state | Freeze affected writers/queue, reconcile actual remote state, recover known-good version |
| P2 | Missing skill/source, stale result, hook/plugin failure or unavailable required tool | Block affected node, diagnose, preserve unaffected output and report exact failure |
| P3 | Nonessential quality improvement or slow optional branch | Continue main deliverable; track a scoped improvement if useful |

Severity measures impact, not the amount of log output. Do not disable safety controls to make a failing run appear healthy. Recovery should retain original failure evidence and distinguish repaired, retried, verified and unresolved states.

## 7. Runbook: interrupted conversation or crashed controller

**Trigger:** host restart, context compaction, disconnected session or interrupted tool call.

1. Read the current task/run contract, ledger revision, source versions and accepted artifacts.
2. Query actual surviving worker/process/provider state with available tools.
3. Reconcile ambiguous external actions before any retry.
4. Preserve accepted unaffected outputs; do not rebuild the whole task unnecessarily.
5. Reject late results whose assignment tokens or inputs were superseded.
6. Resume only within the existing authority and remaining budget.
7. Report the actual resumed stage and material unresolved dependency.

An aborted tool may have partially completed. A missing local response is not proof that the external action failed. Do not relaunch a paid render, send or remote mutation simply because the chat lost its receipt.

## 8. Runbook: source or approved lock changed

**Source revision changed, same contract:** stop affected actual workers, record the current state, then use the controller's source invalidation operation. Recompute downstream readiness; retain unrelated artifacts after rechecking their input scope.

**Exact word/tag, permission, deliverable or finish criterion changed:** preserve and cancel the intact old contract; create a replacement run with a new run ID and current sources. Do not hand-edit static locks/history to make old results validate. Old assignment tokens cannot finish the replacement run.

If the change affects a published/delivered artifact, first identify the concrete existing result and available correction path. A local invalidation cannot retract an external post or undo a sent message.

## 9. Runbook: stale or concurrent write

**Trigger:** expected revision/head mismatch, conflicting canonical file edits or duplicate record ID.

1. Stop the dependent writer; preserve its proposed patch.
2. Reload latest canonical state and inspect the actual conflict.
3. Reconcile by record/file identity and current source authority.
4. Preserve unrelated accepted changes from other writers.
5. Revalidate affected output and retry with the new observed revision/head.
6. Read back the final state and record the new identity.

Never remove a revision guard or use a force push as routine conflict resolution. Local file locks do not serialize another machine or remote GitHub writes. Use expected-head updates and a single canonical writer.

## 10. Runbook: provider timeout or unknown paid outcome

**Trigger:** no response after a request may have reached an external service.

1. Mark the effect outcome unknown rather than failed-by-assumption.
2. Query using the existing provider request ID, idempotency key or output identity.
3. If completed, attach the result and reconcile actual spend.
4. If definitely rejected before execution, retry within limits.
5. If still ambiguous, keep that action blocked; continue independent work.
6. Explain the precise unknown state and what would resolve it.

If a provider supports no idempotency/status lookup, duplicate risk is a real constraint. Do not create a second paid job or message merely to obtain a clean local log.

## 11. Runbook: Hookify or another hook/plugin fails

**Observed failure class:** a configured hook command references a missing script such as `hooks/stop.py`, or its interpreter/dependency cannot be resolved. A hook error identifies a harness/plugin problem; it does not by itself prove that GitHub or all tools are unavailable.

### Diagnose visibly

1. Capture the hook name, event, reported command path, exit status and first useful error. Avoid repeated copies of full logs.
2. Determine whether the hook is advisory or a mandatory policy/security gate.
3. Inspect the configured plugin identity/version and resolve the referenced path read-only.
4. Check whether a package update moved the cache path, a reinstall is incomplete, or an interpreter/dependency is missing.
5. Probe an unrelated authorized read-only operation if useful to determine actual scope of the failure.

### Recover without bypassing

- For a stale/missing package, use the supported plugin update/reinstall or configuration repair path under applicable authority. Verify the expected script belongs to the correct trusted package/version.
- Do not create an empty success-returning replacement script, change errors into passes, remove approval checks, suppress mandatory hook output or edit a runtime cache merely to fake success.
- If a mandatory gate cannot run, keep its gated action blocked. Complete independent authorized work and state exactly which operation remains unverified.
- If an optional plugin must be disabled for recovery, obtain/confirm applicable authority and explain the concrete effect; never silently disable a security gate. Disabling is not a repair.
- Re-run the relevant hook/readiness check after repair and verify the originally blocked operation independently.
- After one clear failure report, deduplicate unchanged repeat events and stop automatic retry storms. Record the repeated event count internally; notify again only on a meaningful change or required user action.

A user-facing failure message should identify the failed component, observed error, impact, preserved work and next concrete recovery action. Do not assert that every connector is blocked without a live failed connector check.

**Example:** “The stop hook refers to a missing plugin script. That hook is unverified. Repository read access succeeded independently; the gated completion step remains pending until the plugin is repaired.” Use only statements supported by the actual checks performed.

## 12. Runbook: connector or repository access changed

1. Resolve the intended account and exact repository/resource from the user request.
2. Probe the current connector read-only; record the actual account/resource result.
3. Distinguish repository not found, unauthorized account, missing app installation, branch missing and stale connector session.
4. Verify actual write scope before a mutation; do not infer it solely from an earlier permission observation.
5. Use the relevant purpose-built connector where sufficient; fall back only when needed and disclose material limits.
6. Never copy tokens, private account details or installation IDs into reusable examples/logs.

A repository link does not identify a feature branch unless it contains one or the user names it. “All repositories” installation scope is different from which repository the current task is authorized to modify. Least privilege should be implemented through the actual installation/account settings, not a text promise in the Brain.

Architecture/documentation work does not authorize uninstalling other accounts or altering repository access. If the user explicitly requests an access change, prepare and apply that concrete supported change within scope, then verify the saved installation and live connector independently.

## 13. Runbook: missing or reconstructed skill

1. Check the current skill path/package and declared source status.
2. Search a narrow trusted source if the known path is stale.
3. Keep reconstructed documentation labelled reconstructed.
4. If required exact source is unavailable, do not claim a full installation or complete source export.
5. Use a competent documented fallback only if it can satisfy the outcome within scope.
6. Preserve useful independent work and record the exact missing resource.

A provider package reference is not a copied source package. A tool listing is not a skill. A readable agent dossier is not proof that a worker ran.

## 14. Runbook: missing preview/reference control

Exact creative inventory work requires the actual source/preview interaction specified by the owning skill. Overview card metadata alone cannot prove a preview tag or directional view.

1. Resolve the actual project and asset/version.
2. Check live click/control and preview access.
3. Open each required preview and re-read the current accessible/UI state after navigation.
4. Record exact tags, costume/view/left-right-centre details and scene mapping where requested.
5. If control is unavailable, block the exact-inventory claim; do not guess from overview text.
6. Keep broader unverified suggestions distinct from the requested verified inventory.

This is an operational fidelity rule. Text validation cannot establish that a location render has the required regional appearance; inspect the actual render before claiming a fix.

## 15. Runbook: memory save or learning update failed

1. Keep the candidate rule/patch separate from active memory.
2. Record source, exact scope, previous revision and error without secrets.
3. Verify whether a partial write occurred before retrying.
4. Reconcile current canonical state through the guarded controller.
5. Run affected regression and routing checks when a reusable rule/skill changes.
6. Read back the persisted record and report its actual state.

Do not say “I will remember” or “saved” when persistence failed. A local draft is prepared, not durable across every host. Existing memory maintenance permission does not expand into external sends, account changes, paid spending or scheduler activation.

## 16. Runbook: budget exhaustion

1. Stop dispatching new paid jobs that cannot fit the remaining authorized envelope.
2. Reconcile active reservations and observed spend; do not cancel a completed charge by changing local state.
3. Preserve completed artifacts and produce the best authorized package possible.
4. Identify optional work that can be skipped without misrepresenting completion.
5. Ask for a concrete budget change only if necessary to finish a required paid operation.

Do not silently increase generation count, resolution, model tier or evaluation trials. An architecture catalogue listing a premium capability does not authorize using it.

## 17. Runbook: independent reviewer unavailable

1. Verify actual worker/modality access, rather than assuming a reviewer from the registry.
2. If the task allows self-review, run relevant checks and label the result self-reviewed.
3. If independent review is a required gate, keep the gate pending and preserve the reviewable artifact.
4. Never invent a reviewer identity, independent verdict or fresh context.
5. Distinguish structural/text checks from direct inspection of image/audio/video.

When fresh workers are supported, give the reviewer raw sources, exact acceptance criteria and artifacts. Do not pass the producer's preferred diagnosis/verdict as an instruction to agree.

## 18. Runbook: scheduled maintenance or notification issue

Before changing a schedule, query actual current jobs, timezone, owner, paused state and last result. A dated source's intended cadence is not current scheduler state. Preserve separately owned jobs and avoid duplicates.

Use a stable schedule identity and last-success checkpoint for authorized reviews. Record partial/inaccessible coverage. Do not advance a checkpoint past work that was not actually retrieved or persisted. Keep routine monitors quiet when state is unchanged unless the user requested periodic status.

Sending to Slack/email/WhatsApp and creating/resuming timers require actual authority and live connector support. Never turn a learning review into a new outbound communications workflow without that scope.

## 19. Release and repository push procedure

For an authorized repository update:

1. Verify correct repository/account and current branch/head.
2. Check local changes and isolate task-owned paths; preserve unrelated work.
3. Keep historical snapshot folders intact unless explicitly asked to revise them.
4. Review diff for hierarchy conflicts, stale claims, broken links, credentials and private data copied unnecessarily.
5. Run meaningful affected checks, existing relevant eval gates and structural validation.
6. Use one commit writer and an expected-head/fast-forward-safe push.
7. Read back the remote commit/files and report branch, commit and actual result.
8. If a PR is used, distinguish branch pushed, PR opened, checks passed and merged.

The requested push authorizes that repo deliverable, not deployment, publication of private material, access-policy changes or modifications to unrelated repositories. Paid model evaluations are separate from deterministic local checks and must fit authorized usage policy.

## 20. Backup and disaster recovery design

Start with version-controlled configuration and a verified backup of task/runtime state where needed. Define recovery objectives only after measuring the actual system; do not promise a zero-loss or instant-recovery service from a diagram.

| Asset | Recovery source | Verification |
|---|---|---|
| Agent/skill/config source | Known-good repository commit and original package provenance | Hash/diff and relevant tests |
| Curated memory | Guarded canonical store plus authorized backups | Schema/provenance validation and revision reconciliation |
| Run state | Ledger/event checkpoint | Assignment/source consistency and external effect reconciliation |
| Artifacts | Workspace/object-store backup and manifests | Content identity and required open/render/play checks |
| Secrets | Actual credential manager recovery procedure | Access test without logging values |
| Derived retrieval index | Canonical source rebuild | Source coverage, access filtering and sample retrieval |
| Schedules | Actual platform configuration export/readback | Correct owner/timezone/paused state and no duplicates |

Exercise recovery with synthetic data before trusting it with production. A backup file existing is not proof that restore works. Include crash-after-provider-dispatch, stale-revision write, partial export, revoked connector, late-worker result and failed mandatory-hook cases.

## 21. Evidence and final reporting

Useful final status is concise and verifiable:

- What artifact/behavior changed and where it was saved.
- Which checks actually ran and what they establish.
- Which required checks remain unrun and why.
- Whether a branch was pushed, PR merged, deployment observed or only a draft produced.
- Any concrete blocker, ambiguous external outcome or user action needed.

Do not repeat every internal tool call. Do not claim a production agent platform was built when the delivered work is architecture, registries and source references. Do not claim all user chats, all installed tools or all private accounts were exported. Report coverage by the inspected sources and declared gaps.

See [Architecture](ARCHITECTURE.md) and [Memory and Learning](MEMORY_AND_LEARNING.md) for the contracts these procedures enforce.
