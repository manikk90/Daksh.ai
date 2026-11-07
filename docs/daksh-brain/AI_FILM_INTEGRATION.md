# AI-film under Daksh Brain

AI-film is the production and editing module at [`modules/ai-film`](../../modules/ai-film), pinned to upstream commit `2c096fe562340ccb8b4a313e6a313d919db6a407`. It supplies an executable screenplay-to-shot CLI, the Mann editor, studio procedures and style references. Daksh Brain owns intake, assignments, source versions, final review and delivery. This integration does not launch workers or connect providers.

## Get the complete checkout

```bash
git clone --recurse-submodules https://github.com/manikk90/Daksh.ai.git
cd Daksh.ai
# For an existing checkout:
git submodule update --init --recursive -- modules/ai-film
python3 tools/ai_film.py validate
python3 tools/ai_film.py film --help
python3 tools/ai_film.py mann doctor
```

The submodule URL is public and contains no credentials; the parent remains private. AI-film's source, relative links, third-party attribution, importer and own Git history stay together. There is one pinned module, rather than copied skill bodies or another root controller. `daksh-ai` inside the imported formats is a format engine, not a competing Daksh Brain.

`validate` checks the gitlink, URL, exact checkout revision, tracked-source cleanliness, skill inventory hashes and role/workflow references. An absent module produces the initialization command and exit 2. No initialization, update, package install, generation or approval happens automatically. A source-valid result does not establish provider access, media quality or owner approval.

## Route the existing agents

| AI-film procedure | Daksh owner | Source in the module |
|---|---|---|
| Production controller / viral studio | Daksh Brain | `skills/film-production/`, `.claude/skills/viral-studio/` |
| Writing and screenplay breakdown | Writer | `skills/ai-writer/`, `skills/screenplay-breakdown/` |
| Creative direction, shots, boards | Native Director | `skills/creative-direction/`, `skills/shot-continuity/`, `skills/storyboard-keyframes/` |
| Character and costume references | Reference Mapper | `skills/character-costume-design/` |
| Locations and props | Location Director | `skills/location-prop-design/` |
| Tool bundles / real take import | Tools/Connector Operator | `skills/video-tool-handoff/` |
| Source coverage and clip review | Independent QC | `skills/coverage-quality-audit/` |
| Mann editing and style study | Native Director, with scoped Mann worker when available | `.claude/skills/mann-edit/`, `.claude/skills/mann-style-lab/` |
| Research / social / sound | Research, Socials, Music, Dubbing specialists | Upstream studio role briefs plus existing Daksh skills |
| Studio feedback | Action/Style Learning | `.claude/skills/studio-learn/` |

The original missing Writer source remains missing. AI-film includes a distinct usable writer implementation; it does not restore that original. Existing Daksh identity, dialogue, frame-local inventory, camera and project locks still apply. Read upstream `AGENTS.md`, `studio/LEARNINGS.md` and the relevant skill before production; scoped current user instructions retain precedence.

The [supplemental inventory](../../catalog/AI_FILM_SKILLS.md) records 61 upstream entrypoints, including 47 imported formats. The original 669-source catalog and session manifest remain dated inventories. These counts describe sources, not active workers or globally installed plugins. The module also contains 67 draft film styles and 50 catalogued editing styles; catalogue presence is not tested cinematic quality. Imported format copies are maintained through upstream `studio/import_skills.py`, with the original MIT/GSAP notices preserved.

## Commands from Daksh

Use `film` for production records and `mann` for editing. The adapter uses the pinned module code while preserving the caller's current working directory, path arguments, output streams and exit code. Run from the Daksh root for the examples below. Outputs belong in ignored `projects/` and `exports/`; keep production media out of commits.

```bash
python3 tools/ai_film.py film init modules/ai-film/examples/screenplay.txt projects/demo
python3 tools/ai_film.py film set-plan projects/demo modules/ai-film/examples/plan.json
python3 tools/ai_film.py film audit projects/demo
python3 tools/ai_film.py film export-shot projects/demo SH001 exports/demo-SH001-v1 \
  --profile modules/ai-film/profiles/portable-text.json
python3 tools/ai_film.py mann styles
python3 tools/ai_film.py mann --help
```

The sample audit intentionally returns **1**, because the synthetic example has no real accepted takes. **0** means the requested CLI operation succeeded (or the recorded audit passed), and **2** means invalid input/operational error. A successful export is a portable handoff, not generated footage. FFmpeg/ffprobe are needed for media import and render; `mann doctor` reports optional editing dependencies. Do not run the upstream installer automatically as part of this integration.

## Three design-time workflow previews

```bash
python3 tools/daksh_architecture.py plan ai-film-production \
  --inputs architecture/examples/ai-film-production-inputs.json
python3 tools/daksh_architecture.py plan ai-film-viral-studio \
  --inputs architecture/examples/ai-film-viral-studio-inputs.json
python3 tools/daksh_architecture.py plan ai-film-mann-edit \
  --inputs architecture/examples/ai-film-mann-edit-inputs.json
```

Examples are synthetic placeholders, not approved project inputs. Previews show dependency batches only. They do not execute approval nodes, instantiate workers, submit jobs or write an upstream project. A real run must bind actual files, approval evidence, assignments and available tools.

Production preserves source lines, semantic beats, immutable assets, shot IDs, input order, bundles, take versions and full-clip review evidence. It remains useful through manual export/import without provider credentials. Newly written scripts require a separate writer, independent critique, revision and explicit owner approval before voice, music, picture or rendering.

Viral studio retains script/format, look/music and final-cut gates, then delivers a real video plus one supporting ZIP containing the NLE editor package and other files, within upstream size limits. Mann retains style, script lock and exact-EDL storyboard approval before full rendering. Changed edits invalidate affected approvals through upstream code. No integration, plan preview, silence or reviewer verdict constitutes the owner's approval.

## Memory, actions and updates

`brain/DAKSH_BRAIN.json` stays the guarded Daksh memory. Upstream `studio/LEARNINGS.md` and `editor/rules.json` retain their own scope and source history. Do not overwrite one store with another or treat historical host/network observations and nightly intents as current environment/scheduler state. The integration starts no schedules, external messages or paid jobs.

To update AI-film, first select and inspect an upstream commit, then update the submodule checkout, `integrations/ai-film.json` pin and `catalog/ai-film-skills.json` hashes in one parent change. Reconcile role mappings, source gates and notices. Run the checks below, review both diffs, and commit the gitlink. Do not silently follow upstream `main` or edit imported format copies. Durable changes to AI-film code belong in its own reviewed upstream change before the parent pin moves.

## Compatibility fixes in the pinned revision

[AI-film PR #8](https://github.com/manikk90/AI-film/pull/8) restores cached clip frame rates for FFmpeg transitions, bounds sparse storyboard extraction without dropping its exact-frame check, and supports explicit `AIFILM_CHROMIUM_EXECUTABLE` selection in both canvas renderers. The module pin includes this reviewed branch commit; the upstream PR need not be merged for a recursive checkout to retrieve it.

The current managed environment blocks Playwright browser downloads and blocks `file://` rendering in its installed Chromium. Local browser-render tests are therefore pending; no browser policy was bypassed. Hosted CI installs its own Playwright/Chromium dependencies and still runs the unchanged full upstream suite.

## Checks

Observed local results and browser limitations: [AI-film validation](AI_FILM_VALIDATION.md).

```bash
python3 tools/ai_film.py validate
python3 tools/daksh_architecture.py validate
python3 -m pytest -q -p no:cacheprovider tests/
(cd modules/ai-film && python3 -m unittest discover -s tests -v)
python3 -m compileall -q tools modules/ai-film/aifilm
```

CI initializes submodules and runs the integration and upstream suites with FFmpeg. These are structural/workflow and synthetic-media checks. They do not certify vendor settings, inspect a real film or grant production approval.
