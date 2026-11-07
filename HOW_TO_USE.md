# How to use this audited bundle

> Current master edition: [Daksh Brain architecture](docs/daksh-brain/README.md) and [complete installed skill inventory](catalog/SKILLS.md). Daksh Brain is the top AI controller; this existing source catalogue remains a compatibility/reference record.

For the current AI-film production CLI, viral studio and Mann editor, follow [the integration guide](docs/daksh-brain/AI_FILM_INTEGRATION.md). Initialize `modules/ai-film` with `git submodule update --init --recursive`, then use `python3 tools/ai_film.py film --help` or `python3 tools/ai_film.py mann doctor`. The audit instructions below describe the historical bundle.


1. Open audit/AUDIT_REPORT.md to understand what was checked and what remains missing.
2. Choose the relevant agents/*.md. Its opening clarifications govern this export; full original source modules follow with explicit provenance. Do not load all agents for a tiny task.
3. Use the original skills/ folder for executable scripts, exact templates, structured data and byte-exact source recovery. Paths inside quoted source instructions are relative to their original skill root.
4. Treat runtime_state/ as dated source snapshots, not current account state. The Writer patch is unapplied evidence, not a recovery script to execute automatically.
5. Use previous_v2_summaries/ only for comparison. Use original_dossier/ as historical backup.
6. Run `python verification/verify_export.py .` from the extracted bundle root to verify file hashes and nested ZIP integrity. Run `python verification/verify_content.py .` for the bounded source-inclusion/content-marker checks. Neither command runs agents or verifies output quality.

The individual skill.zip packages are unchanged original snapshots. This task did not install or synchronize any skill. External Data/Writing Style dependencies remain snapshots/mappings rather than full provider bundles. AI Writer still has no recovered original installer.
