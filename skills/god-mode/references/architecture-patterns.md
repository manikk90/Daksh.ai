# Architecture and hack patterns: starting vocabulary

These are durable design patterns for AI systems, used to frame God Mode research quickly. They are **not** evidence that a specific tool, model or price is current. Verify those per run and date them.

## Agent topologies
| Pattern | Use when | Watch out |
|---|---|---|
| Single agent + tools | The task fits one context; there are few steps | It degrades on long multi-domain work |
| Router → specialist | The domains are clearly separable (this brain: Daksh → Director/Music/Dubbing...) | Routing errors; keep routes explicit |
| Orchestrator → parallel workers | The subtasks are independent (research tracks, per-language dubs) | Merge conflicts; you need one canonical writer |
| Pipeline / DAG | Stages depend on each other (Writer → Director → Dubbing → Edit) | Upstream changes must invalidate downstream work |
| Evaluator–optimizer loop | The quality is checkable (prompt audits, cue QC, captions) | The loop needs a stop condition and a budget |
| Independent reviewer | High-stakes output | The reviewer must not see the producer's verdict |

## Memory layers
- **Working context:** only what the current task needs. Load references incrementally; never dump all agents into one context.
- **Canon and locks:** approved project facts, read-only by default (shot IDs, character tags, location geometry).
- **Ledger:** dated lessons and corrections with scope and status. The repo already uses `learning-ledger.json` in several skills.
- **Brain index:** a searchable summary of what exists (`gm_scan.py`). Rebuild it from files, never by memory.
- **Research store:** dated findings with sources (`research/`). Reuse them before searching again.

## Capability packaging
- **Skill:** instructions plus references, scripts and assets behind a precise description. This is the unit of reuse here.
- **Script plus tests:** use for anything deterministic (validation, QC, indexing). Prefer code over prose rules whenever a check can be automated.
- **Tool / MCP server:** use for live systems (Slack, Drive, generation APIs). The skill says when to call it; credentials never live in skill files.
- **Scheduled loop:** nightly or weekly learning and research. Use a single coordinator owner, and check live state before claiming one is active.

## Founder hacks (generic leverage moves)
- **Reuse before build:** extend an existing skill's reference file before creating a new agent.
- **Template once, generate many:** lock one approved example, then vary only the scoped variables (the shot shorthand `fx`, `fm`, `pm` already does this).
- **Automate the check, not just the output:** a validator script catches drift on every run for free.
- **Cheap model drafts, strong model reviews:** route bulk drafting to fast models and review with the strongest one.
- **Parallel tracks plus one merge owner:** speed without conflicting edits.
- **Kill signals up front:** define what failure looks like before you spend time or credits.
- **Distribution is a feature:** a socials or caption step at the end of every production pipeline compounds reach.

## Gap → new skill checklist
1. A clear trigger description: what it does and when to use it.
2. An input contract and an output contract.
3. Locks and boundaries inherited from `shared/COMMON_RULES.md`.
4. Its handoffs to and from existing agents.
5. At least one deterministic check script with tests, where possible.
6. A registry entry (Daksh) and a line in the README brain map.
