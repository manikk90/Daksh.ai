# Daksh Brain

**One accountable AI controller. All agents, skills and tools work under Daksh Brain.**

The human user sets goals and authority. Daksh Brain understands the task, retrieves relevant context, plans dependencies, delegates to specialists, controls budgets and permissions, reviews outputs and verifies delivery. The maniik founder/style persona is an advisor under Daksh Brain.

```text
Human user
  └─ Daksh Brain — context, planning, routing, QC, memory, recovery
       ├─ Founder/style advice · Research · Business · Knowledge
       ├─ Writer · Native Director · Reference Mapper · Location
       ├─ Music · Suno · Dubbing · Fashion · Socials · Design
       ├─ Engineering · Data · Documents · Work Operations
       ├─ Sales · Support · Finance · Legal · People
       └─ Independent QC · Brain Evals · Tools/Connector Operator
            └─ Relevant skills → currently authorized tools → verified artifacts
```

## Start here

- **[AI-film production and Mann editor](docs/daksh-brain/AI_FILM_INTEGRATION.md)** — pinned upstream module, Daksh role mapping, executable CLI bridge and three workflow templates.
- **[Complete architecture and workflow index](docs/daksh-brain/README.md)** — system design, diagrams and source links.
- [Architecture](docs/daksh-brain/ARCHITECTURE.md) · [Workflows](docs/daksh-brain/WORKFLOWS.md) · [Handoffs/QC](docs/daksh-brain/HANDOFFS_AND_QC.md).
- [All skills](catalog/SKILLS.md) · [All tools](catalog/TOOLS.md) · [Skill/tool activation design](docs/daksh-brain/SKILLS_AND_TOOLS.md).
- [Memory/learning](docs/daksh-brain/MEMORY_AND_LEARNING.md) · [Learned operating rules](docs/daksh-brain/LEARNED_OPERATING_RULES.md) · [Operations](docs/daksh-brain/OPERATIONS.md).
- [Coverage and provenance](docs/daksh-brain/COVERAGE_AND_PROVENANCE.md) · [Validation report](docs/daksh-brain/VALIDATION_REPORT.md).
- **[Repository operating instructions](AGENTS.md)** — current hierarchy and precedence for assistants.

## What is included

| Component | Contents |
|---|---|
| [28 agent contracts](agents/contracts/) | Mission, inputs, responsibilities, source locks, outputs, completion checks and escalation |
| [30 workflow templates](architecture/workflows.json) | Creative launch/film, location, tags, audio, fashion, socials, code, research, business, documents, data, planning, scoped learning and three AI-film workflows |
| [AI-film module](modules/ai-film/) | Pinned production CLI and Mann editor; [61 upstream skill entrypoints](catalog/AI_FILM_SKILLS.md), 47 imported formats and source/approval/coverage checks |
| [Complete skill inventory](catalog/skills.json) | 669 readable skill-source records; 11 bundled repo skills plus external metadata, versions and ownership |
| [Session skill manifest](catalog/session-skill-manifest.json) | 390 session-listed sources; disk-only and policy-disabled sources remain separate |
| [Tool inventory](catalog/tools.json) | 628 advertised capability records, with no credential or account-readiness claims |
| [Machine contracts](architecture/contracts/) | Task, handoff, artifact and memory candidate JSON Schemas |
| [Policy and compatibility](architecture/) | Authority, budgets, concurrency, recovery and existing role-ID mapping |
| [Existing production source](skills/) | 11 original skill roots, runtime scripts, validators and existing regression suites |

Inventory is a dated 7 November 2026 snapshot. External skill implementations are not bulk-vendored; catalogued metadata does not imply installed/connected/authorized runtime capability. This is a private working repo.

## Validate and preview locally

Use Python 3.12 or newer. Install validation/test dependencies in a virtual environment:

```bash
git clone --recurse-submodules https://github.com/manikk90/Daksh.ai.git
cd Daksh.ai
# Existing checkout: git submodule update --init --recursive -- modules/ai-film
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install pytest pyyaml pillow numpy 'jsonschema>=4.20,<5'
python3 tools/daksh_architecture.py validate
python3 tools/ai_film.py validate
python3 tools/ai_film.py film --help
python3 tools/ai_film.py mann doctor
python3 tools/daksh_architecture.py plan screenplay-to-film \
  --inputs architecture/examples/film-inputs.json --max-parallel 3
python3 -m pytest -q -p no:cacheprovider tests/
```

The architecture utility validates the specification and prints an offline plan. It launches no workers, spends no credits, creates no schedules and makes no provider calls. The AI-film bridge runs the pinned upstream CLI for production records and editing; upstream script/storyboard approval gates remain intact. Provider adapters and an autonomous runtime broker remain implementation work. The existing strict ledger at `skills/daksh/scripts/orchestrator.py` remains unchanged.

## Existing source and history

The V5.1 creative agent dossiers, source skills, strict frame/dialogue locks, brain/eval utilities and historical records remain available. [Previous README](https://github.com/manikk90/Daksh.ai/blob/4c7276d9388817c175ad7ad85caa3130d6ca912c/README.md), [existing agent/skill mapping](AGENT_SKILL_MAP.md), [existing skill catalogue](SKILL_CATALOG.md), [brain source](brain/README.md), [shared rules](shared/COMMON_RULES.md) and [V5.1 report](reports/V5_1_CONTENT_AUDIT.md) preserve that context.

The user's 7 November instruction supersedes the older maniik-above-Daksh hierarchy. Historical snapshots are retained and do not override the active master contract. AI Writer's dossier remains explicitly reconstructed; no missing original skill or inaccessible conversation is invented.
