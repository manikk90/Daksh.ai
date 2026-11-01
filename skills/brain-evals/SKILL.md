---
name: brain-evals
description: "Test whether maniik's agents and skills actually follow Manik's locks and route correctly: run deterministic lock-compliance evals (DIALOGUE last, exact tags, no Refs line, Naina eyelids, word-locked dubbing, shared IG/FB caption, Suno 800 chars), routing evals, and with-skill vs baseline model runs that measure each skill's lift. Use for brain evals, test my agents, kya skill kaam kar rahi hai, regression check, eval gate before merging a skill or lesson change, and turning a new user correction into a test case."
---

# Brain evals

This is the eval gate for the maniik brain. A skill edit, a new lesson or a `gm build` capability is only "done" when its evals pass. Respond in direct Roman Hinglish.

## Commands
```bash
# 1. Graders correct? Every case's pass/fail fixtures (no model, run in CI)
python skills/brain-evals/scripts/run_evals.py selftest
# 2. Do skill descriptions route correctly? (no model, run in CI)
python skills/brain-evals/scripts/run_evals.py routing
# 3. Grade one saved agent output
python skills/brain-evals/scripts/run_evals.py grade dir-dialogue-last output.txt
# 4. Real behavior: with-skill vs baseline, N trials (costs model usage)
python skills/brain-evals/scripts/run_evals.py run --skill ai-native-director --trials 3 \
    --agent-cmd "claude -p" --out research/evals/YYYY-MM-DD-<skill>.json
```

## Gate rules
- **Regression cases** (`kind: regression`) encode explicit, approved user locks. Any change to the owning skill must keep its with-skill pass rate at ≥ 90%. A drop blocks the change.
- **Lift:** if the with-skill rate is not clearly above the baseline (no skill) over at least 3 trials, the skill text isn't doing work for that case. Shorten or rewrite it before adding more rules.
- **Routing cases** must stay at 100%. If a new skill steals routes, tighten its description.
- Model runs are non-deterministic. Never judge from a single trial, and report pass rates, not anecdotes.

## Add a case from a new correction
Read [writing cases](references/writing-cases.md). In short:
1. Quote the lock's source file.
2. Write a self-contained task that would tempt the old mistake.
3. Choose the smallest deterministic checks.
4. Add one pass fixture and one fail fixture.
5. Run `selftest`.

Each `gm build` capability ships with at least 3 cases.

## Boundaries
These graders check format and lock compliance. They don't judge creative quality, likeness, acting, audio or lip sync, so don't claim those from an eval pass. Only Manik's explicit locks become regression cases. Assistant suggestions don't. Cases must not contain secrets. They may contain project tags because the repo is private.
