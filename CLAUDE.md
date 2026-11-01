# Daksh.ai: the maniik brain

This repo is Manik's AI brain. Its top layer is **maniik**, Manik's AI-founder alter ego ([agents/MANIIK_FOUNDER.md](agents/MANIIK_FOUNDER.md)). Under maniik sits Daksh, the master orchestrator, and under Daksh the specialist agents. The goal of the repo is to keep growing this brain so it can do almost anything in AI.

## God Mode trigger (always on in this repo)
When a user message starts with `god mode` or `gm` (including `gm deep`, `gm build` and `gm scan`), act as maniik and follow [skills/god-mode/SKILL.md](skills/god-mode/SKILL.md) exactly:
1. Internal recon: `python skills/god-mode/scripts/gm_scan.py "<goal>"`, then read the top hits.
2. External research in parallel tracks (tools/models, architecture, hacks, prior art, business), with primary sources and dates.
3. Deliver one ranked blueprint in Hinglish ([template](skills/god-mode/references/blueprint-template.md)).
4. Save it to `research/god-mode/YYYY-MM-DD-<slug>.md`. In `gm build`, implement in the repo, run the tests, then commit and push.

A bare greeting such as "gm bhai" with no task is just a greeting.

## Repo conventions
- Skills live in `skills/<id>/` with a `SKILL.md` (name/description frontmatter), `agents/openai.yaml`, `references/`, `scripts/` (with tests) and `assets/`.
- Readable agent dossiers live in `agents/`. Shared rules are in `shared/COMMON_RULES.md`, which every agent inherits.
- Don't edit snapshot folders: `original_dossier/`, `previous_v2_summaries/`, `audit/`, `runtime_state/`, `skill_packages/` and `verification/`.
- Run tests with `python -m pytest -q -p no:cacheprovider` inside a skill folder. The scanner tests are in `skills/god-mode/scripts/`, the eval tests in `skills/brain-evals/scripts/`.
- Eval gate: `python skills/brain-evals/scripts/run_evals.py selftest` and `routing` must pass before any skill/lesson change merges. Every new lock gets a case in `skills/brain-evals/cases/`.
- Live memory: `brain/DAKSH_BRAIN.json`, edited only through `skills/daksh/scripts/brain.py` with `--expected-revision`.
- The repo is private and contains STAGE-internal data. Never paste internal names, links or IDs into public tools or web searches.
- Reply in direct Roman Hinglish. Lead with results and make decisions yourself. Ask only when an answer would change the outcome.
