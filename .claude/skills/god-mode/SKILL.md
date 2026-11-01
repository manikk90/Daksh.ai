---
name: god-mode
description: "maniik's God Mode. Use whenever the user's message starts with 'god mode' or 'gm' (gm, gm deep, gm build, gm scan): research the goal across this repo's agents and skills plus current external tools, hacks and architectures, and deliver a ranked founder blueprint; in gm build, implement it in the repo."
---

Follow the canonical skill at `skills/god-mode/SKILL.md` (repo root) exactly. Read it now, along with `agents/MANIIK_FOUNDER.md`.

The Claude Code tools for each step:
- **Internal recon:** run `python skills/god-mode/scripts/gm_scan.py "<goal>"`, then use Read on the top hits.
- **External research:** load WebSearch and WebFetch via ToolSearch. For `gm deep`, launch parallel research subagents, one per track, in a single message.
- **Independent review (`gm deep`):** use a fresh subagent that gets the sources and the blueprint, but not your verdict.
- **Persist:** write `research/god-mode/YYYY-MM-DD-<slug>.md`. In `gm build`, create or extend files under `skills/` and `agents/`, run the tests, then commit and push.
