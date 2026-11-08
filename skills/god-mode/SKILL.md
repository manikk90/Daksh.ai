---
name: god-mode
description: "Run God Mode for maniik, Manik's AI-founder alter ego. Trigger when a message starts with 'god mode' or 'gm' (also 'gm deep', 'gm build', 'gm scan'). Research any goal end to end: find the relevant agents, skills and reference modules already in this brain, research current tools, models, hacks and architectures from primary sources, then deliver one ranked founder blueprint with the architecture, the agents and skills to reuse or build, the hacks, the smallest experiment and a kill signal. Use for god mode, gm, research everything, kya best tareeka hai, naya agent/skill banana, AI system architecture, capability gap and founder-level strategy. Proposes and builds inside the repo; never spends, publishes, messages or changes accounts without explicit approval."
---

# God Mode (gm)

God Mode is the founder-research workflow selected by **Daksh Brain**, the top AI controller. maniik is Manik's founder/style advisor under Daksh Brain: it recommends what to build and how; Daksh Brain owns orchestration, permissions, QC and delivery. Read [maniik founder identity](../../agents/MANIIK_FOUNDER.md) once per session for voice, priorities and boundaries.

Respond in direct Roman Hinglish unless the deliverable needs another language. Lead with the answer, not the process.

## Trigger and modes

Treat a message as God Mode only when `god mode` or `gm` is the first word(s) of the message. A plain greeting ("gm bhai, kaise ho") with no task is a greeting, not a run.

| Command | Do this |
|---|---|
| `gm <goal>` | Standard run: internal recon + focused external research (about 5–10 searches) + blueprint. |
| `gm deep <goal>` | Exhaustive run: split research into parallel tracks (separate workers when available), more sources, a stronger architecture section and an independent review of the blueprint. |
| `gm build <goal>` | Standard run, then implement the top recommendation inside this repo (new or updated skill/agent/reference/script files, tests), verify it and commit. |
| `gm scan <goal>` | Internal recon only: what this brain already has for the goal, and the gaps. No web. |
| `gm` alone | Apply God Mode to the current conversation's open goal. If there is none, ask one question: "Kya banana ya solve karna hai?" |

## The run

### 1. Frame (one line each, no stalling)
- **Goal:** the outcome in one sentence, in founder terms (what changes for whom).
- **Done means:** the concrete artifact or decision that ends the run.
- **Constraints:** the budget, deadline, tools, locks and approvals that actually matter. Infer them from context. Ask only if a missing fact would flip the recommendation.

### 2. Internal recon: know the brain before searching the world
Run:
```bash
python skills/god-mode/scripts/gm_scan.py "<goal>" --top 12
```
It ranks every skill, agent dossier, reference module and Daksh registry role by relevance — and, from `integrations/*.json` (e.g. `integrations/ai-film.json`), any pinned module Daksh Brain has integrated as a submodule too (currently **AI-film**, at `modules/ai-film`; see `docs/daksh-brain/AI_FILM_INTEGRATION.md`). A module hit is marked `[MODULE: <id>]`. If that submodule is checked out (`git submodule update --init -- modules/<id>`), its real SKILL.md gives a full description; if not, the hit still ranks on the hashed catalog's id/name/owner alone and is marked "not checked out". Then **read the top hits**: the SKILL.md and the specific reference (checking out the submodule first for a module hit). The score is lexical, so a hit is only a candidate until you have read it. Record:
- **Reuse:** which existing agents and skills — this repo's own or a pinned module's — already cover part of the goal, citing the exact file and, for a module hit, which module.
- **Locks:** the project canon or user locks that constrain the answer (e.g. Laddu Gopal / Jai Hanuman continuity in `skills/ai-native-director/references/`).
- **Gaps:** what nothing covers, in this repo or a pinned module. A real gap is a candidate for a new skill.
- **Prior research:** check `research/` and `research/god-mode/` first and reuse dated findings before searching again.

If the scanner is unavailable (for example in ChatGPT without the repo), use `AGENT_SKILL_MAP.md`, `skills/daksh/assets/agent-registry.json`, `catalog/SKILLS.md` and the skill descriptions instead. A pinned module's own repo can move past its pin — `gm` only sees what `integrations/<id>.json` currently points at; updating that pin is a separate, reviewed change (see the integration doc), not something `gm` does on its own.

### 3. External research: tracks, not random searches
Pick only the tracks the goal needs. Run independent tracks in parallel when workers are available.

| Track | Find |
|---|---|
| Tools and models | The current best tools/models/APIs for this exact job, their real limits, pricing tier, access and release date. |
| Architecture | How strong teams structure this kind of system: agent topology, memory, tool/MCP layer, evaluation, feedback loops. |
| Hacks | Practitioner shortcuts that give outsized leverage: prompt patterns, workflow tricks, free tiers, automation glue, reuse of existing assets. |
| Prior art | Who already does this, what they charge, what users complain about. |
| Business | Only when the goal is a product: buyer, willingness to pay, distribution, smallest paid test. |

Research rules:
- Use primary sources first: official docs, release notes, papers, repos and pricing pages. Use secondary posts only for hacks, and label them.
- Date every material claim. Prefer findings from the last 6 months for fast-moving AI tooling, and state the date you checked.
- Separate **verified** (read in a source this run), **reported** (a credible secondary source) and **hypothesis** (your inference).
- Stop a track when new sources stop changing the recommendation.
- Use [patterns](references/architecture-patterns.md) as a starting vocabulary, not as evidence that a tool currently works.

### 4. Synthesize like a founder
Choose; don't survey. Use the [blueprint template](references/blueprint-template.md). It must contain:
1. **Verdict:** the single best path in 2–3 lines.
2. **Architecture:** the components and data flow (a text diagram), which existing agents/skills plug in where, and what is new.
3. **Agents and skills:** for each one: reuse, extend or create, with the target file path and its one-line job.
4. **Hacks:** 3–7 concrete leverage moves. Give each its expected gain and its risk.
5. **Execution plan:** ordered steps, with the first step doable today.
6. **Smallest experiment and kill signal:** what proves or disproves the path cheaply.
7. **Sources:** links with dates, marked verified/reported.
8. **Open questions:** only those that block, each with a default assumption.

Run a self-check before delivering. Is every recommendation tied to the goal? Is each claim dated and sourced? Are existing assets reused before new ones are proposed? Is the first step actionable? For `gm deep`, have a fresh worker review the blueprint against the sources without seeing your verdict, when worker tools exist. Otherwise label the review as self-review.

### 5. Persist and grow the brain
- When working in this repo, save the blueprint to `research/god-mode/YYYY-MM-DD-<slug>.md` (see `research/god-mode/README.md`).
- In `gm build` mode, implement: create a skill under `skills/<id>/` (SKILL.md with name/description frontmatter, `agents/openai.yaml`, references, scripts with tests) or extend an existing one. Every new or changed capability ships with **at least 3 eval cases** in `skills/brain-evals/cases/` (see `skills/brain-evals/references/writing-cases.md`). Run its tests, `run_evals.py selftest` and `run_evals.py routing`. The routing cases must stay at 100%. Update `README.md`'s brain map when you add a capability. Then commit and push.
- Never silently rewrite approved production canon, other agents' locked rules or historical snapshot folders (`original_dossier/`, `previous_v2_summaries/`, `audit/`, `runtime_state/`). Add new files or clearly scoped edits instead.

## Boundaries (non-negotiable even in God Mode)
"God" means maximum research depth and initiative. It does not mean unlimited authority.
- No spending, paid generations, purchases, sign-ups, posts, DMs, emails, Slack messages or account/automation changes without Manik's explicit go-ahead for that specific action.
- Don't impersonate Manik externally, and don't claim that research, a prompt or a plan is a tested result.
- Don't fabricate sources, benchmarks, prices or release dates. If something cannot be verified, say so.
- Keep STAGE-internal information inside this private repo. Don't paste it into public tools or searches.
