# Eval runs

These are model-run reports from `skills/brain-evals/scripts/run_evals.py run`. Each JSON file holds every trial's full output, its failed checks and the pass rate per condition (`with_skill` vs `baseline`). Runs that hit an infrastructure error (an empty output or a usage limit) are marked `error` and excluded from the pass rates.

## 2026-11-01-baseline-all.json: PARTIAL, not a verdict
- 12 cases × 2 conditions × 3 trials = 72 runs. **57 runs hit the account's 5-hour Claude usage limit** and were excluded.
- Only 2 cases have valid runs in both conditions: `dir-dialogue-last` (with-skill 67% vs baseline 0%) and `dir-blank-line-before-dialogue` (100% vs 0%). `dir-no-refs-line` passed with the skill (3/3), but it has no valid baseline run.
- The earlier first attempt also exposed grader false-failures: notes after the prompt block, negated phrases, and cue parentheticals inside dialogue. These were fixed before this run, in commit "brain-evals: grade code-block deliverable...".
- **Next:** re-run after the limit resets with fewer workers (`--workers 2`), or one skill at a time. Model runs share the same account usage as normal Claude work.

## 2026-11-02-full.json: FIRST VALID RUN
- 12 cases × 2 conditions × 3 trials = 72 runs, **0 errored** (`--workers 2`).
- **With skill: 100% (36/36 runs). Baseline (no skill): 41.7%. Lift: +58.3 points.** This meets the GM experiment bar (≥ 90% and ≥ 20 points above baseline).
- Where the skill makes the difference (baseline 0%, with skill 100%): DIALOGUE last, blank line before DIALOGUE, Naina's 20% eyelids, exact dialogue words, the `captions do` grouping, the single `caption do`, and the Suno 800-character cap.
- No difference (baseline was also 100%): the no-Refs line, exact Mukund/Pooja tags, both crowd-tag cases and the Dubbing word lock. The task text already supplies the needed tags or words, so these cases guard against regressions but don't measure lift. Harder variants could be added later.
- Scope: this proves format and lock compliance only, not creative, visual or audio quality.
