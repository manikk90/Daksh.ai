# Manik | All Agents, Mapped Skills and Content Audit v3

**Private working export | 1 November 2026**

> **Latest: V5.1 (2 November 2026)** — Director aur Socials ke latest locks skill source aur agent MDs dono mein sync ([V5.1 audit](reports/V5_1_CONTENT_AUDIT.md), [V5.1 manifest](reports/V5_1_MANIFEST.json)). Base update: **V5.** `agents/` aur `skills/` ab V5 wale hain: AI Fashion Campaigner (`agents/AI_FASHION_CAMPAIGNER.md`, `skills/fashion-campaign-director/`) add hua, aur Native Director, Dubbing, Socials, Location, Music, Suno, Daksh, maniik update hue. Details: [V5 update report](reports/V5_UPDATE_REPORT.md), [V5 QA](reports/V5_QA_REPORT.md), [official research](research/OFFICIAL_RESEARCH_2026-11-02.md), [V5 manifest](reports/V5_MANIFEST.json).
>
> Baaki folders (`audit/`, `runtime_state/`, `mapping/`, `skill_packages/`, `verification/`, `previous_v2_summaries/`, `original_dossier/`) v3 snapshot hain. `skill_packages/*.zip` aur `verification/FILE_HASHES.json` V5 se update nahi hue, isliye V5 files ke liye `reports/V5_MANIFEST.json` ke hashes use karo.


V2 ke source folders complete the, lekin main agent MDs short summaries the. V3 mein main dossiers expand kiye hain, scope/wording errors fix kiye hain aur actual dated memory/project records add kiye hain. AI Writer ka exact source abhi bhi missing hai; uski file clearly reconstructed hai.

## maniik brain + God Mode (`gm`)

Is repo ka main kaam ek brain banana hai jo AI mein almost kuch bhi kar sake. Top layer **maniik** hai, Manik ka AI-founder alter ego ([identity](agents/MANIIK_FOUNDER.md)). maniik decide karta hai kya banana hai. Daksh orchestrate karta hai, aur specialists execute karte hain.

| Command | Kaam |
|---|---|
| `gm <goal>` | Repo ke relevant agents/skills + current tools, hacks, architecture ka research -> ek ranked blueprint |
| `gm deep <goal>` | Parallel deep research + independent review |
| `gm build <goal>` | Research ke baad capability repo mein bana ke commit |
| `gm scan <goal>` | Sirf internal: brain mein kya already hai, gaps kya hain |

Skill: [skills/god-mode/SKILL.md](skills/god-mode/SKILL.md). Internal scanner: `python skills/god-mode/scripts/gm_scan.py "<goal>"`. Reports: `research/god-mode/`. Claude Code is repo mein `CLAUDE.md` ke through `gm` automatically pehchanta hai.

### Brain infrastructure (2026-11-01)
| Piece | Path | Kaam |
|---|---|---|
| Live memory | [brain/](brain/README.md) | `DAKSH_BRAIN.json`, versioned, `brain.py` se hi edit |
| Eval gate | [skills/brain-evals/](skills/brain-evals/SKILL.md) | Locks ke regression cases, routing evals, with-skill vs baseline runs |
| CI | `.github/workflows/brain-checks.yml` | Har push/PR par saare tests + selftest + routing + brain validate |
| Cross-tool skills | `.agents/skills/` | `skills/*` ke symlinks (Agent Skills standard path) |
| Eval results | `research/evals/` | Model runs ke dated reports |

## Start here
- [Audit verdict and actual gaps](audit/AUDIT_REPORT.md)
- [Coverage matrix](audit/COVERAGE_MATRIX.md)
- [Agent to skill map](AGENT_SKILL_MAP.md)
- [Detailed skill catalogue](SKILL_CATALOG.md)
- [How to use](HOW_TO_USE.md)
- [Validation report](verification/QA_REPORT.md)

## Package contents
| Folder | What it contains |
|---|---|
| agents/ | 8 source-expanded agent/helper dossiers plus 1 reconstructed Writer dossier |
| skills/ | All 217 exact original custom source files, unchanged |
| skill_packages/ | Eight original single-skill skill.zip archives, unchanged |
| runtime_state/ | Actual dated Daksh brain, Laddu Gopal revision 7, Writer unapplied maintenance |
| shared/ | Current cross-agent contract and recent source-scoped project exceptions |
| overlays/ | Latest conversation-scoped rules and audit clarifications |
| audit/ | Findings, source provenance, content counts, inclusion indices and gaps |
| previous_v2_summaries/ | Exact previous nine short agent MDs |
| original_dossier/ | Earlier v1 dossier files preserved |
| mapping/, support_skills/, external_dependencies/ | Existing routing and supporting dependency snapshots |
| verification/ | v3 checks, preserved v2 reports and integrity verifier |

## Boundaries
All 73 available custom Markdown source modules are consolidated into the corresponding agent MDs. Saved lesson records are included with their original statuses. Scripts, templates and larger structured datasets remain in the indexed source folders. Writer has no original source/installer here.

This is not an exhaustive raw-chat/media archive. Original source statements about APIs, accounts and schedules remain dated and need verification when used for execution. No live agent, timer, external account or approved production asset was modified. The outer ZIP is a documentation/source bundle, not a one-click multi-skill installation.

Use the audited main MD and current scoped overrides for documentation. Loading an unchanged nested skill.zip alone does not install the new v3 clarifications.
