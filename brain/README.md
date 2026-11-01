# Live brain

`DAKSH_BRAIN.json` here is the **live, versioned memory** of the maniik brain. The repo is the source of truth from 2026-11-01. It was seeded from `runtime_state/DAKSH_BRAIN.json` (revision 77, 2026-10-30), which stays as an untouched snapshot.

## Use it only through `brain.py`
It enforces the schema, scopes, supersession and revision guards. Never hand-edit the JSON.
```bash
B=brain/DAKSH_BRAIN.json; S=skills/daksh/scripts/brain.py
python $S validate $B
python $S summary  $B                      # shows the current revision
python $S retrieve $B "Naina eyelids"      # scoped recall
python $S agenda   $B
python $S append    $B lessons record.json --expected-revision <rev>
python $S supersede $B <old-id> record.json --expected-revision <rev>
```
Every write needs the current `--expected-revision`. A stale writer fails instead of overwriting someone else's change.

## Rules
- Only Manik's explicit instructions or corrections, saved records and observed outcomes become `memory`/`lessons`. Inferences stay `proposed`, as `skills/daksh/references/memory-and-actions.md` defines.
- When a new lock becomes a lesson, add a matching case in `skills/brain-evals/cases/` in the same commit.
- **ChatGPT Library copy:** the older ChatGPT-side `DAKSH_BRAIN.json` is now a mirror. When it gets newer records, reconcile them into this file by record ID with `supersede` and `append`, then commit. Don't overwrite one whole file with the other.
- No secrets or credentials, and no private personal data beyond what the skills already scope.
