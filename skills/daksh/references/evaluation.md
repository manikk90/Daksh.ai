# Evaluation

Validate the skill with Skill Creator's quick_validate.py. Validate materialized state with `python scripts/brain.py validate <path>` and run `python scripts/test_brain.py` after utility changes. These checks establish structural/runtime properties, not truth, approval or media quality.

For master-controller changes run `python scripts/test_orchestrator.py` and validate `assets/run.template.json`. Check independent parallel readiness, dependency gating, final-review coverage, duplicate/cyclic plans, permission and write-target conflicts, stale revisions/assignments, source invalidation, failure/retry budgets, cancellation, reviewer identity and idempotent completion. Use a fresh task with raw sources/artifacts to check actual routing, merge and QC behavior; procedural role/tool restrictions are not an OS sandbox. A successful ledger transition does not prove a worker ran or an artifact is correct.

For behavioral forward tests use a fresh worker only when permitted/useful. Give skill plus raw task artifacts, without expected answers/diagnosis. Keep tests read-only and free of live communication, production mutations or paid generation. Inspect actual results; label author self-review separately.

Important cases: narrow tone edits preserve exact words and reuse context; bag corrections remain scoped; inferred preferences/assistant drafts do not become user facts; business ideas get falsifiable tests rather than invented metrics; inaccessible weekly sources/writes remain partial/unapplied; mimicry does not authorize sending or passive monitoring; source conflicts remain explicit; stale state writes fail; identical appends are idempotent and conflicting IDs do not overwrite.

Measure elapsed time, repeated reads, corrections, accepted/requested outputs and cost only when observed. Unknowns are null. Compare equal scope before claiming improvement. Retire only the regressing new rule and preserve prior accepted behavior. Do not call a text check an audio listening test, verified geometry, full-history review or successful publication.


After memory/continuation changes run `scripts/test_brain_extensions.py` with the existing brain/controller tests. Cover stale/proposed recall, cross-project/shot leakage, supersession links and atomic retry, real task ownership, closure evidence, immutable owners, terminal tasks and unsupported capability claims. A software pass does not establish a fresh independent behavioral review.
