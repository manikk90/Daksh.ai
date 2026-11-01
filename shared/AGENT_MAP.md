# Ownership and Dependencies

```text
Manik -> Daksh (master)
            |-- AI Writer (story, dialogue lock)
            |     |-- AI Native Director (shots, acting, camera) <-- AI Location Director (spatial references)
            |     |-- Ai Dubbing (language, cue/voice QC) <---- AI Native Director (picture timing)
            |     `-- AI Music Director (score / original song)
            |             `-- Suno Instrumental Prompt Helper (Styles)
            |-- AI Socials (public content, copy; release approval separate)
            `-- maniik (internal work plans, Slack/Gmail read-only)
```

## Handoff gates
- Writer -> Director: approved scene/script ID, shot intent, locked words and visible inventory.
- Location -> Director: master reference, approved geography and exact view/prop tags.
- Director -> Dubbing: picture version, character acting, duration, speech timing and audio constraints.
- Writer -> Dubbing: approved dialogue and pronunciation notes; adaptation review needed.
- Director/Music -> Edit: timing map, motif and dialogue ducking notes; audio exists only if actually generated.
- Production -> Socials: approved public facts, imagery clearance, publication permission separate.
- Slack/Gmail -> maniik: owned tasks, deadlines, blocker evidence, accepted targets.

## Scheduler warnings
Daily/Sunday planned learning frequencies are not a blanket guarantee of active jobs. Check live schedule before saying enabled; do not duplicate coordinator, Writer, or Location tasks.
