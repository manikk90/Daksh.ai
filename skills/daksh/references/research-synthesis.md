# Research synthesis

Use this branch for internet research, synthesis-brain requests and research-driven file updates. Keep one canonical `DAKSH_BRAIN.json`; its `synthesis` section indexes decisions, not a second personal memory database. This is a reasoning workflow with a record validator, not an autonomous crawler, trained model or deployed agent service.

## Source to decision

1. Read the latest saved brain and relevant source spans. Identify the practical gap and compare existing findings before searching.
2. Read load-bearing primary pages. Preserve checked date separately from publication date; use null when a publication date is unavailable. Record interface, model and account limitations. Do not treat a documentation recheck as a new release.
3. Extract the supported finding, then state the task-specific inference separately. Compare current user locks and exact source scope. Record contradictory documentation as a conflict; do not choose the more convenient capability.
4. Decide `adopt_rule`, `prepare_test`, `no_change`, `defer` or `reject`. Name the receiving agent and exact target. A no-change result is valid; avoid adding rules to unrelated agents.
5. Define an observable test and failure signal. Keep expected effects separate from measured results. Documentation permits an interface/preflight correction; identity, dialect, emotion, geometry and performance gains need actual relevant outputs.
6. Validate records with `python scripts/synthesis.py BRAIN.json`. This checks declarations and links, not source truth or successful installation. Save the same brain/file identities with version guards. Install skill rules only through their real save workflow; retain unresolved tests and access gaps.

Each synthesis record retains `id`, `checked_on`, `source_ids`, `evidence_level`, `verified_finding`, `application`, `agents`, `decision`, `application_status`, `target_files`, `test` (kind, status, observable plan and failure signal), and `recheck_trigger`. Use `installation_evidence_id` only for an observed skill save; use `test.evidence_id` only for an executed test. Do not close customer validation with desk research.

## Three practical checks

**Compaction:** Distinguish summary retention from retrieval recovery. Freeze a small answer key, probe a fresh context using only the compacted packet, then separately test source-pointer recovery. Preserve exact identifiers, latest corrections, unresolved dependencies and uncertainty. The Anthropic cookbook demonstrates these distinct mechanisms; it does not prove Daksh's recall. Source: https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools (20 March 2026; checked 29 October 2026).

**Resume:** Keep reusable knowledge separate from task progress and action receipts. Inspect the actual current output before replaying a possible side effect. LangGraph documents thread checkpoints and cross-thread stores; adopting fields in JSON does not install its runtime or provide exactly-once execution. Sources: https://docs.langchain.com/oss/python/langgraph/persistence and https://docs.langchain.com/oss/python/langgraph/checkpointers (publication dates unavailable; checked 29 October 2026).

**Evaluation:** Use deterministic checks for literal contracts, evidence-aware semantic review for meaning and human corrections to check the rubric. A fresh reviewer is independent critique, not calibration. Retain unknowns, false accepts/rejects and scope. Sources: https://www.anthropic.com/research/demystifying-evals-for-ai-agents (9 January 2026) and https://www.langchain.com/resources/llm-as-a-judge (10 March 2026); checked 29 October 2026. Without human-labeled outcomes call the exercise a rubric or fixture check, not human calibration.
