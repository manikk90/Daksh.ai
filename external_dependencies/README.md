# External mapped dependencies

These dependency entrypoint snapshots were read from the current skill resource API on 1 November 2026. They are readable source text, with punctuation normalized for this export, not byte-for-byte provider-plugin backups. No user writing examples, credentials or private account exports were copied.

## Confirmed direct mapping

| Registered alias | Current resource | Snapshot |
|---|---|---|
| `data-analytics:index` | `skills://plugins/data/index/skill.md` | `data/index/skill.md` |
| `write-like-me:write-like-me` | `skills://plugins/writing-style/write-like-me/skill.md` | `writing-style/write-like-me/skill.md` |

Evidence for the mapping: `../skills/daksh/assets/agent-registry.json` and `../skills/daksh/references/specialists.md`.

## Data: conditional transitive routes

The Data index routes to the following provider skills according to the task. Listing them is not a claim they are permanent separate agents or that their full directories are contained in this archive. Fetch the applicable live skill in its original host before execution.

| Workflow | Purpose | Current provider URI |
|---|---|---|
| `product-business-analysis` | Business or product decisions | `skills://plugins/data/product-business-analysis/skill.md` |
| `metric-diagnostics` | Metric changes and drivers | `skills://plugins/data/metric-diagnostics/skill.md` |
| `kpi-reporting` | KPI/business review | `skills://plugins/data/kpi-reporting/skill.md` |
| `design-kpis` | Success metrics and guardrails | `skills://plugins/data/design-kpis/skill.md` |
| `market-sizing` | Market and opportunity size | `skills://plugins/data/market-sizing/skill.md` |
| `analyze-data-quality` | Dataset quality | `skills://plugins/data/analyze-data-quality/skill.md` |
| `validate-data` | Calculation/source/claim audit | `skills://plugins/data/validate-data/skill.md` |
| `answers-follow-up` | Optional follow-up suggestions | `skills://plugins/data/answers-follow-up/skill.md` |
| `build-report` | Narrative artifact | `skills://plugins/data/build-report/skill.md` |
| `build-dashboard` | Interactive monitoring/exploration | `skills://plugins/data/build-dashboard/skill.md` |
| `visualize-data` | Durable chart authoring | `skills://plugins/data/visualize-data/skill.md` |
| `jupyter-notebooks` | Requested notebook | `skills://plugins/data/jupyter-notebooks/skill.md` |
| `convert-to-doc` | Existing Data app to document | `skills://plugins/data/convert-to-doc/skill.md` |
| `convert-to-slides` | Existing Data app to slides | `skills://plugins/data/convert-to-slides/skill.md` |
| `report-to-pdf` | Report export | `skills://plugins/data/report-to-pdf/skill.md` |
| `share-artifact-summary` | Requested artifact sharing | `skills://plugins/data/share-artifact-summary/skill.md` |
| `publish-artifact-to-sites` | Requested Sites publication | `skills://plugins/data/publish-artifact-to-sites/skill.md` |
| `schedule-refresh-jobs` | Authorized recurring refresh | `skills://plugins/data/schedule-refresh-jobs/skill.md` |
| `onboarding` | Data onboarding | `skills://plugins/data/onboarding/skill.md` |
| `customize-data-plugin` | Reusable Data working context | `skills://plugins/data/customize-data-plugin/skill.md` |

## Not contained in these two snapshots

Provider shared-reference directories, provider runtimes, templates and execution infrastructure remain external. Relative links within the preserved Data entrypoint refer to that original provider layout and intentionally do not resolve inside this export. `dependency_registry.json` records this distinction.

The eight custom source directories and the Skill Creator support snapshot have separate exact-copy/hash coverage; do not confuse that stronger claim with these transcribed plugin entrypoints.
