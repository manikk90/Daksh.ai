# Agent -> Skill Map

> Current master edition: [Daksh Brain architecture](docs/daksh-brain/README.md) and [complete installed skill inventory](catalog/SKILLS.md). Daksh Brain is the top AI controller; this existing source catalogue remains a compatibility/reference record.

AI-film is now integrated as a pinned production/editing module under Daksh Brain. See [the integration and current role mapping](docs/daksh-brain/AI_FILM_INTEGRATION.md) and [61 upstream skill entrypoints](catalog/AI_FILM_SKILLS.md). Its Writer implementation is distinct from the unavailable original Writer source described below.


Is file mein actual mapped skills, internal roles aur external dependencies alag rakhe gaye hain. Kisi role ka naam hona uske live run ya active automation ka proof nahi hai.

| Agent / role | Skill ya implementation | Export status |
|---|---|---|
| Daksh | [`daksh`](skills/daksh/SKILL.md) | Original source, 22 files |
| maniik | [`maniik`](skills/maniik/SKILL.md) | Original source, 7 files |
| AI Native Director | [`ai-native-director`](skills/ai-native-director/SKILL.md) | Original source, 31 files |
| AI Location Director | [`ai-location-director`](skills/ai-location-director/SKILL.md) | Original source, 30 files |
| AI Music Director | [`ai-music-director`](skills/ai-music-director/SKILL.md) | Original source, 21 files |
| Ai Dubbing | [`ai-dubbing`](skills/ai-dubbing/SKILL.md) | Original source, 16 files |
| AI Socials | [`ai-socials`](skills/ai-socials/SKILL.md) | Original source, 87 files |
| Suno Instrumental Prompt Helper | [`suno-instrumental-prompts`](skills/suno-instrumental-prompts/SKILL.md) | Original source, 3 files |
| AI Writer | [`ai-writer` documentation](agents/AI_WRITER.md) | Mapped, installed source unavailable; reconstructed dossier retained |
| Daksh maintenance | [`skill-creator`](support_skills/skill-creator/SKILL.md) | Original support-source snapshot |
| Data analysis | [`data-analytics:index` -> current Data index](external_dependencies/data/index/skill.md) | Plugin entrypoint snapshot; provider dependencies remain external |
| Authored writing style | [`write-like-me:write-like-me` -> Writing Style](external_dependencies/writing-style/write-like-me/skill.md) | Plugin entrypoint snapshot; live connector access not included |

## Internal roles, separate installed skills nahi

| Parent | Internal role / branch | Source |
|---|---|---|
| Daksh | AI Research, Business Analyst, Action/Style Model, Independent QC role | `skills/daksh/assets/agent-registry.json` |
| AI Native Director | Reference Mapper, Filmmaking QC, camera/composition, cast/costume, acting and prompt compiler | `skills/ai-native-director/agents/` and `references/` |
| AI Location Director | Location controller, prop views, spatial QC and panorama tools | `skills/ai-location-director/references/` and `scripts/` |
| AI Music Director | Lyrics/vocals, scoring, platform controls, QC | `skills/ai-music-director/references/` |
| Ai Dubbing | Performance direction, regional adaptation, cue and request QC | `skills/ai-dubbing/references/` and `scripts/` |
| AI Socials | Researcher, Social Media Manager, Independent Evaluator | `skills/ai-socials/references/roles.md` |

## Ownership aur handoffs

```text
Manik -> Daksh
          |-- maniik -> Slack/Gmail evidence -> work plan/review
          |-- AI Writer [source unavailable] -> approved story/dialogue
          |-- AI Native Director -> Reference Mapper + Filmmaking QC
          |         ^
          |         |-- AI Location Director -> geography/props/views
          |-- Ai Dubbing <- exact words + timing + picture version
          |-- AI Music Director -> Suno Instrumental Prompt Helper
          |-- AI Socials -> platform-native drafts
          |-- Data workflows [provider plugin]
          |-- Writing Style [provider plugin]
          `-- Skill Creator [maintenance workflow]
```

Full machine-readable routing, evidence paths aur internal module files: [mapping/agent_skill_map.json](mapping/agent_skill_map.json).

## Boundary

Slack, Gmail, Google Calendar, Library/Files, browsing, image/audio/video generation aur scheduling tools ko fake skills bana kar include nahi kiya gaya. Unki capability aur permission live host par resolve karni hogi. Historical IDs/records ko current enabled state mat samajhna.

AI Writer ke purane records mein recovery aur baad mein paused/unapplied observations dono milte hain. Is export ka accurate claim sirf itna hai: mapping exists, current installed source did not resolve. Koi restore, resume ya scheduler change nahi kiya gaya.
