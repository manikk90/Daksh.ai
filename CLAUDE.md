# Daksh.ai: Daksh Brain

Read [AGENTS.md](AGENTS.md) first. **Daksh Brain is the highest AI controller; the human user retains final authority.** All specialists, skills and the maniik founder/style advisor operate under Daksh Brain. This is the user's 7 November 2026 hierarchy, superseding the previous maniik-above-Daksh description.

## Entry points

- [Master system map](docs/daksh-brain/README.md)
- [Agent registry](architecture/agents.json) and [role contracts](agents/contracts/)
- [Workflow DAG templates](architecture/workflows.json), [policies](architecture/policies.json), [handoff schemas](architecture/contracts/)
- [All skills](catalog/SKILLS.md), [all tools](catalog/TOOLS.md), [operations](docs/daksh-brain/OPERATIONS.md)

## God Mode

When a message starts with `god mode` or `gm` (including `gm deep`, `gm build`, `gm scan`), Daksh Brain selects [skills/god-mode/SKILL.md](skills/god-mode/SKILL.md) and uses maniik as its founder/research advisor. Preserve existing command behavior, source research and budget boundaries. A greeting such as `gm bhai` without a task remains a greeting. No advisor may grant itself new permissions or overrule current user scope.

## Existing conventions

- Skills live in `skills/<id>/`; readable dossiers in `agents/`; all inherit `shared/COMMON_RULES.md`.
- Do not edit source snapshots: `original_dossier/`, `previous_v2_summaries/`, `audit/`, `runtime_state/`, `skill_packages/`, `verification/`.
- Existing skill tests run separately inside each skill folder with `python3 -m pytest -q -p no:cacheprovider`.
- Grader `selftest`, `routing` and brain validation must pass for affected rule/skill changes. New master-spec checks run with `python3 tools/daksh_architecture.py validate` and `python3 -m pytest -q -p no:cacheprovider tests/`.
- Live memory edits use `skills/daksh/scripts/brain.py` with `--expected-revision`, only within actual scoped authority. Do not change memory/schedules as a side effect of reading the architecture.
- Existing `orchestrator.py` is a strict local ledger, not a worker launcher. Keep new conceptual task/handoff schemas separate until an explicit adapter exists.
- Private STAGE content, links and IDs must not be sent into public searches or unrelated tools.
- Reply in direct Roman Hinglish; finish authorized work, preserve exact locks and report evidence/status honestly.
