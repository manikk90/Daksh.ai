# Eval runs

These are model-run reports from `skills/brain-evals/scripts/run_evals.py run`. Each JSON file holds every trial's full output, its failed checks and the pass rate per condition (`with_skill` vs `baseline`). Runs that hit an infrastructure error (an empty output or a usage limit) are marked `error` and excluded from the pass rates.

## 2026-11-01-baseline-all.json: PARTIAL, not a verdict
- 12 cases × 2 conditions × 3 trials = 72 runs. **57 runs hit the account's 5-hour Claude usage limit** and were excluded.
- Only 2 cases have valid runs in both conditions: `dir-dialogue-last` (with-skill 67% vs baseline 0%) and `dir-blank-line-before-dialogue` (100% vs 0%). `dir-no-refs-line` passed with the skill (3/3), but it has no valid baseline run.
- The earlier first attempt also exposed grader false-failures: notes after the prompt block, negated phrases, and cue parentheticals inside dialogue. These were fixed before this run, in commit "brain-evals: grade code-block deliverable...".
- **Next:** re-run after the limit resets with fewer workers (`--workers 2`), or one skill at a time. Model runs share the same account usage as normal Claude work.
