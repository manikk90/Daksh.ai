# Manik: All Agents + Mapped Skills

**Export v2 | 1 November 2026 | Private working bundle**

Purane agent dossier mein mapped skills ke actual available source files, internal role maps aur supporting resources add kiye gaye hain. Ye sirf names ki list nahi hai.

## Kya included hai

| Item | Count / status |
|---|---|
| Readable operational dossiers | 8 core agents + 1 Suno helper |
| Original custom skill directories | 8, containing 217 original files |
| Mapped maintenance support | Skill Creator, 8 original files |
| Individual custom-skill packages | 8 separate `skill.zip` archives |
| External mapped plugin entrypoints | Data index + Writing Style snapshots |
| Conditional Data routes | 20, cataloged as provider dependencies, not fully bundled |
| Original dossier preservation | All 13 files copied unchanged under `original_dossier/` |
| AI Writer original source | Not available; mapped/reconstructed status clearly marked |

## Yahan se start karo

- [Agent -> Skill Map](AGENT_SKILL_MAP.md): ownership, internal roles aur cross-agent handoffs.
- [Detailed Skill Catalog](SKILL_CATALOG.md): har skill ke modules aur complete source file index.
- [Use guide](HOW_TO_USE.md): reading, reuse aur single-skill package layout.
- [Latest user overrides](overlays/LATEST_USER_OVERRIDES_2026-11-01.md): composition, lighting, previews, shortcuts, dialogue aur identity rules.
- [Dependencies and limits](DEPENDENCIES_AND_LIMITS.md): exact source vs external provider snapshots aur runtime boundaries.
- [Validation report](verification/QA_REPORT.md): actually executed checks, not assumed installation success.

## Folder layout

```text
agents/                 readable agent dossiers, mapped-skills addon included
skills/                 8 exact original custom skill directories
support_skills/         original Skill Creator maintenance source
skill_packages/         one skill.zip per custom skill
mapping/                machine-readable routing and source hashes
external_dependencies/  Data/Writing Style snapshots and dependency catalog
overlays/               latest scoped conversation rules, separate from originals
shared/                 original shared rules and handoff map
missing/                explicit AI Writer source gap
original_dossier/       unchanged original export files
verification/           checks, logs and reusable integrity verifier
```

## Important distinction

The available custom skill source files and support snapshot are exact copies. External provider entrypoints are readable text snapshots with punctuation normalization, not full plugin distributions. Older runtime records remain historical; no live timer or account state is guaranteed.

**Is export se installed agents, automations, publication permissions ya production assets change nahi hue.** Outer ZIP is a multi-skill source/documentation bundle, not a single-skill installer. AI Writer ki missing original source ko fabricated installer se replace nahi kiya gaya.

Current explicit user instructions and approved scoped assets remain authoritative. Load only the relevant agent/skill and latest applicable overlay rather than dumping every file into one context.
