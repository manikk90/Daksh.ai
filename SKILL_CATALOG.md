# Mapped Skills: Detailed File Catalog

Har custom skill ka complete available directory copy kiya gaya hai. Neeche modules ke entry points diye hain; full file index bhi included hai. Source content English mein jaisa saved tha waisa hi preserve hai.

## Contents

- [Daksh](#daksh)
- [maniik](#maniik)
- [AI Native Director](#ai-native-director)
- [AI Location Director](#ai-location-director)
- [AI Music Director](#ai-music-director)
- [Ai Dubbing](#ai-dubbing)
- [AI Socials](#ai-socials)
- [Suno Instrumental Prompt Helper](#suno-instrumental-prompts)

<a id="daksh"></a>
## Daksh

**Entry:** [SKILL.md](skills/daksh/SKILL.md)  |  **Source files:** 22  |  **Single-skill archive:** [skill.zip](skill_packages/daksh/skill.zip)

### Master orchestration and dependency tracking

- [`references/master-orchestration.md`](skills/daksh/references/master-orchestration.md)
- [`assets/agent-registry.json`](skills/daksh/assets/agent-registry.json)
- [`assets/run.template.json`](skills/daksh/assets/run.template.json)
- [`scripts/orchestrator.py`](skills/daksh/scripts/orchestrator.py)

### Memory, scoped corrections and action/style model

- [`references/memory-and-actions.md`](skills/daksh/references/memory-and-actions.md)
- [`references/operating-loop.md`](skills/daksh/references/operating-loop.md)
- [`assets/brain.template.json`](skills/daksh/assets/brain.template.json)
- [`scripts/brain.py`](skills/daksh/scripts/brain.py)

### AI research, synthesis and business analysis

- [`references/research-synthesis.md`](skills/daksh/references/research-synthesis.md)
- [`references/research-and-business.md`](skills/daksh/references/research-and-business.md)
- [`scripts/synthesis.py`](skills/daksh/scripts/synthesis.py)

### Specialist dispatch and independent QC contract

- [`references/specialists.md`](skills/daksh/references/specialists.md)
- [`references/evaluation.md`](skills/daksh/references/evaluation.md)
- [`assets/evaluation.json`](skills/daksh/assets/evaluation.json)

### Daily/weekly learning and historical runtime state

- [`references/weekly-learning.md`](skills/daksh/references/weekly-learning.md)
- [`assets/runtime.json`](skills/daksh/assets/runtime.json)

### Complete source file index

```text
SKILL.md
agents/openai.yaml
assets/agent-registry.json
assets/brain.template.json
assets/evaluation.json
assets/icon.svg
assets/run.template.json
assets/runtime.json
references/evaluation.md
references/master-orchestration.md
references/memory-and-actions.md
references/operating-loop.md
references/research-and-business.md
references/research-synthesis.md
references/specialists.md
references/weekly-learning.md
scripts/brain.py
scripts/orchestrator.py
scripts/synthesis.py
scripts/test_brain.py
scripts/test_brain_extensions.py
scripts/test_orchestrator.py
```


<a id="maniik"></a>
## maniik

**Entry:** [SKILL.md](skills/maniik/SKILL.md)  |  **Source files:** 7  |  **Single-skill archive:** [skill.zip](skill_packages/maniik/skill.zip)

### Slack/Gmail evidence and exact weekly template

- [`references/context-and-template.md`](skills/maniik/references/context-and-template.md)

### Dependencies, capacity and demonstrated workflows

- [`references/extended-workflows.md`](skills/maniik/references/extended-workflows.md)

### Explicit preferences and scoped ownership

- [`references/preferences.md`](skills/maniik/references/preferences.md)

### Learning/schedule binding snapshot

- [`assets/learning-runtime.json`](skills/maniik/assets/learning-runtime.json)

### Complete source file index

```text
SKILL.md
agents/openai.yaml
assets/icon.svg
assets/learning-runtime.json
references/context-and-template.md
references/extended-workflows.md
references/preferences.md
```


<a id="ai-native-director"></a>
## AI Native Director

**Entry:** [SKILL.md](skills/ai-native-director/SKILL.md)  |  **Source files:** 31  |  **Single-skill archive:** [skill.zip](skill_packages/ai-native-director/skill.zip)

### Director controller and task routing

- [`references/controller-runtime.md`](skills/ai-native-director/references/controller-runtime.md)
- [`references/execution-quality.md`](skills/ai-native-director/references/execution-quality.md)

### Camera, coverage, composition and focus

- [`references/camera-and-coverage.md`](skills/ai-native-director/references/camera-and-coverage.md)
- [`references/camera-catalog.md`](skills/ai-native-director/references/camera-catalog.md)
- [`references/shot-composition.md`](skills/ai-native-director/references/shot-composition.md)
- [`assets/composition-patterns.json`](skills/ai-native-director/assets/composition-patterns.json)
- [`assets/composition-study.frames.json`](skills/ai-native-director/assets/composition-study.frames.json)
- [`scripts/composition_lookup.py`](skills/ai-native-director/scripts/composition_lookup.py)

### Cast identity and costumes

- [`references/cast-and-costume.md`](skills/ai-native-director/references/cast-and-costume.md)
- [`assets/cast-costume.template.json`](skills/ai-native-director/assets/cast-costume.template.json)

### Performance, action and micro-expressions

- [`references/performance-and-action.md`](skills/ai-native-director/references/performance-and-action.md)
- [`assets/character-performance.template.json`](skills/ai-native-director/assets/character-performance.template.json)

### Image/video compiler and model adapters

- [`references/image-video-prompts.md`](skills/ai-native-director/references/image-video-prompts.md)
- [`references/model-adapters.md`](skills/ai-native-director/references/model-adapters.md)
- [`references/reference-input-preflight.md`](skills/ai-native-director/references/reference-input-preflight.md)
- [`scripts/audit_prompt_contract.py`](skills/ai-native-director/scripts/audit_prompt_contract.py)

### Reference Mapper role and tag/asset binding

- [`agents/reference-mapper.md`](skills/ai-native-director/agents/reference-mapper.md)
- [`references/reference-mapper-contract.md`](skills/ai-native-director/references/reference-mapper-contract.md)
- [`references/mapping-and-qc-agents.md`](skills/ai-native-director/references/mapping-and-qc-agents.md)
- [`scripts/validate_handoff.py`](skills/ai-native-director/scripts/validate_handoff.py)

### Filmmaking QC role and evidence contract

- [`agents/filmmaking-qc.md`](skills/ai-native-director/agents/filmmaking-qc.md)
- [`references/filmmaking-qc-contract.md`](skills/ai-native-director/references/filmmaking-qc-contract.md)

### Continuity, editing and sound

- [`references/composition-editing-sound.md`](skills/ai-native-director/references/composition-editing-sound.md)
- [`references/laddu-gopal.md`](skills/ai-native-director/references/laddu-gopal.md)
- [`scripts/project_context.py`](skills/ai-native-director/scripts/project_context.py)

### Scoped corrections and continuous learning

- [`references/continuous-learning.md`](skills/ai-native-director/references/continuous-learning.md)
- [`assets/learning-ledger.json`](skills/ai-native-director/assets/learning-ledger.json)
- [`scripts/validate_learning_ledger.py`](skills/ai-native-director/scripts/validate_learning_ledger.py)

### Complete source file index

```text
SKILL.md
agents/filmmaking-qc.md
agents/openai.yaml
agents/reference-mapper.md
assets/cast-costume.template.json
assets/character-performance.template.json
assets/composition-patterns.json
assets/composition-study.frames.json
assets/icon.svg
assets/learning-ledger.json
references/camera-and-coverage.md
references/camera-catalog.md
references/cast-and-costume.md
references/composition-editing-sound.md
references/continuous-learning.md
references/controller-runtime.md
references/execution-quality.md
references/filmmaking-qc-contract.md
references/image-video-prompts.md
references/laddu-gopal.md
references/mapping-and-qc-agents.md
references/model-adapters.md
references/performance-and-action.md
references/reference-input-preflight.md
references/reference-mapper-contract.md
references/shot-composition.md
scripts/audit_prompt_contract.py
scripts/composition_lookup.py
scripts/project_context.py
scripts/validate_handoff.py
scripts/validate_learning_ledger.py
```


<a id="ai-location-director"></a>
## AI Location Director

**Entry:** [SKILL.md](skills/ai-location-director/SKILL.md)  |  **Source files:** 30  |  **Single-skill archive:** [skill.zip](skill_packages/ai-location-director/skill.zip)

### Location controller and staged master workflow

- [`references/agent-controller.md`](skills/ai-location-director/references/agent-controller.md)
- [`references/workflow.md`](skills/ai-location-director/references/workflow.md)
- [`references/context-research.md`](skills/ai-location-director/references/context-research.md)

### Connected geography and spatial contracts

- [`references/spatial-contract.md`](skills/ai-location-director/references/spatial-contract.md)
- [`references/project-location-locks.md`](skills/ai-location-director/references/project-location-locks.md)
- [`assets/location-manifest.template.json`](skills/ai-location-director/assets/location-manifest.template.json)
- [`scripts/spatial_checks.py`](skills/ai-location-director/scripts/spatial_checks.py)

### Four-view props

- [`references/props-four-views.md`](skills/ai-location-director/references/props-four-views.md)

### Reference-input and Director handoff

- [`references/reference-input-preflight.md`](skills/ai-location-director/references/reference-input-preflight.md)
- [`references/prompts-and-handoff.md`](skills/ai-location-director/references/prompts-and-handoff.md)

### Production state and location QC

- [`references/production-runtime.md`](skills/ai-location-director/references/production-runtime.md)
- [`references/qc-and-repair.md`](skills/ai-location-director/references/qc-and-repair.md)
- [`scripts/location_runtime.py`](skills/ai-location-director/scripts/location_runtime.py)
- [`scripts/validate_location.py`](skills/ai-location-director/scripts/validate_location.py)

### Panorama/pose/view tooling

- [`scripts/build_panorama_viewer.py`](skills/ai-location-director/scripts/build_panorama_viewer.py)
- [`scripts/inspect_colmap_pose.py`](skills/ai-location-director/scripts/inspect_colmap_pose.py)
- [`scripts/transfer_intrinsics.py`](skills/ai-location-director/scripts/transfer_intrinsics.py)
- [`scripts/compare_views.py`](skills/ai-location-director/scripts/compare_views.py)

### Learning ledger and validation

- [`references/continuous-learning.md`](skills/ai-location-director/references/continuous-learning.md)
- [`assets/learning-ledger.json`](skills/ai-location-director/assets/learning-ledger.json)
- [`scripts/validate_learning.py`](skills/ai-location-director/scripts/validate_learning.py)

### Complete source file index

```text
SKILL.md
agents/openai.yaml
assets/icon.svg
assets/learning-ledger.json
assets/location-manifest.template.json
references/agent-controller.md
references/context-research.md
references/continuous-learning.md
references/production-runtime.md
references/project-location-locks.md
references/prompts-and-handoff.md
references/props-four-views.md
references/qc-and-repair.md
references/reference-input-preflight.md
references/spatial-contract.md
references/workflow.md
scripts/build_panorama_viewer.py
scripts/compare_views.py
scripts/inspect_colmap_pose.py
scripts/location_runtime.py
scripts/spatial_checks.py
scripts/test_build_panorama_viewer.py
scripts/test_compare_views.py
scripts/test_inspect_colmap_pose.py
scripts/test_location_runtime.py
scripts/test_spatial_checks.py
scripts/test_transfer_intrinsics.py
scripts/transfer_intrinsics.py
scripts/validate_learning.py
scripts/validate_location.py
```


<a id="ai-music-director"></a>
## AI Music Director

**Entry:** [SKILL.md](skills/ai-music-director/SKILL.md)  |  **Source files:** 21  |  **Single-skill archive:** [skill.zip](skill_packages/ai-music-director/skill.zip)

### Music director role and runtime

- [`agents/music-director.md`](skills/ai-music-director/agents/music-director.md)
- [`references/autonomous-runtime.md`](skills/ai-music-director/references/autonomous-runtime.md)
- [`scripts/music_runtime.py`](skills/ai-music-director/scripts/music_runtime.py)

### Scene scoring, instruments and project motifs

- [`references/scene-scoring.md`](skills/ai-music-director/references/scene-scoring.md)
- [`references/instrument-palette.md`](skills/ai-music-director/references/instrument-palette.md)
- [`references/project-music-context.md`](skills/ai-music-director/references/project-music-context.md)

### Lyrics and singing micro-expression

- [`references/lyrics-and-vocal-direction.md`](skills/ai-music-director/references/lyrics-and-vocal-direction.md)
- [`references/vocal-micro-expression.md`](skills/ai-music-director/references/vocal-micro-expression.md)
- [`assets/lyric-patterns.json`](skills/ai-music-director/assets/lyric-patterns.json)

### Platform routing, model registry and controls

- [`references/platform-workflows.md`](skills/ai-music-director/references/platform-workflows.md)
- [`references/smart-parameters.md`](skills/ai-music-director/references/smart-parameters.md)
- [`assets/model-registry.json`](skills/ai-music-director/assets/model-registry.json)
- [`assets/control-profiles.json`](skills/ai-music-director/assets/control-profiles.json)

### Music QC and learning

- [`scripts/music_qc.py`](skills/ai-music-director/scripts/music_qc.py)
- [`references/continuous-learning.md`](skills/ai-music-director/references/continuous-learning.md)
- [`assets/learning-ledger.json`](skills/ai-music-director/assets/learning-ledger.json)
- [`assets/improvement-state.json`](skills/ai-music-director/assets/improvement-state.json)

### Suno instrumental delegation

- Route to [`suno-instrumental-prompts`](skills/suno-instrumental-prompts/SKILL.md).

### Complete source file index

```text
SKILL.md
agents/music-director.md
agents/openai.yaml
assets/control-profiles.json
assets/icon.svg
assets/improvement-state.json
assets/learning-ledger.json
assets/lyric-patterns.json
assets/model-registry.json
references/autonomous-runtime.md
references/continuous-learning.md
references/instrument-palette.md
references/lyrics-and-vocal-direction.md
references/platform-workflows.md
references/project-music-context.md
references/scene-scoring.md
references/smart-parameters.md
references/vocal-micro-expression.md
scripts/music_qc.py
scripts/music_runtime.py
scripts/test_music_runtime.py
```


<a id="ai-dubbing"></a>
## Ai Dubbing

**Entry:** [SKILL.md](skills/ai-dubbing/SKILL.md)  |  **Source files:** 16  |  **Single-skill archive:** [skill.zip](skill_packages/ai-dubbing/skill.zip)

### Fast emotion and performance direction

- [`references/fast-performance.md`](skills/ai-dubbing/references/fast-performance.md)
- [`assets/performance-cues.json`](skills/ai-dubbing/assets/performance-cues.json)

### Research, language and model/interface guidance

- [`references/research-and-playbook.md`](skills/ai-dubbing/references/research-and-playbook.md)
- [`references/interface-specific-controls.md`](skills/ai-dubbing/references/interface-specific-controls.md)

### Writer/Director/native-review/editor handoff

- [`references/workflow-contract.md`](skills/ai-dubbing/references/workflow-contract.md)
- [`assets/dubbing-manifest.example.json`](skills/ai-dubbing/assets/dubbing-manifest.example.json)

### Cue and request validation

- [`scripts/cue_qc.py`](skills/ai-dubbing/scripts/cue_qc.py)
- [`scripts/dialogue_request_qc.py`](skills/ai-dubbing/scripts/dialogue_request_qc.py)

### Learning and observed runtime

- [`references/continuous-learning.md`](skills/ai-dubbing/references/continuous-learning.md)
- [`assets/learning-ledger.json`](skills/ai-dubbing/assets/learning-ledger.json)
- [`assets/learning-runtime.json`](skills/ai-dubbing/assets/learning-runtime.json)

### Complete source file index

```text
SKILL.md
agents/openai.yaml
assets/dubbing-manifest.example.json
assets/icon.svg
assets/learning-ledger.json
assets/learning-runtime.json
assets/performance-cues.json
references/continuous-learning.md
references/fast-performance.md
references/interface-specific-controls.md
references/research-and-playbook.md
references/workflow-contract.md
scripts/cue_qc.py
scripts/dialogue_request_qc.py
scripts/test_cue_qc.py
scripts/test_dialogue_request_qc.py
```


<a id="ai-socials"></a>
## AI Socials

**Entry:** [SKILL.md](skills/ai-socials/SKILL.md)  |  **Source files:** 87  |  **Single-skill archive:** [skill.zip](skill_packages/ai-socials/skill.zip)

### Voice, profiles and editorial boundaries

- [`brain/voice.md`](skills/ai-socials/brain/voice.md)
- [`brain/profiles.json`](skills/ai-socials/brain/profiles.json)
- [`brain/platform_rules.json`](skills/ai-socials/brain/platform_rules.json)
- [`assets/source-manifest.json`](skills/ai-socials/assets/source-manifest.json)

### Caption routing and six platform formats

- [`references/caption-mode.md`](skills/ai-socials/references/caption-mode.md)

### Growth, hooks, pillars and planning

- [`references/growth-strategy.md`](skills/ai-socials/references/growth-strategy.md)
- [`brain/playbook.md`](skills/ai-socials/brain/playbook.md)
- [`brain/hook_library.json`](skills/ai-socials/brain/hook_library.json)
- [`brain/pillars.json`](skills/ai-socials/brain/pillars.json)
- [`brain/hypotheses.json`](skills/ai-socials/brain/hypotheses.json)
- [`brain/slots.json`](skills/ai-socials/brain/slots.json)
- [`brain/playbook_rules.json`](skills/ai-socials/brain/playbook_rules.json)

### Researcher, manager and independent-evaluator roles

- [`references/roles.md`](skills/ai-socials/references/roles.md)
- [`references/workflows.md`](skills/ai-socials/references/workflows.md)

### Draft/plan/evaluation schemas

- [`schemas/draft_post.schema.json`](skills/ai-socials/schemas/draft_post.schema.json)
- [`schemas/content_plan.schema.json`](skills/ai-socials/schemas/content_plan.schema.json)
- [`schemas/eval_report.schema.json`](skills/ai-socials/schemas/eval_report.schema.json)
- [`schemas/research_brief.schema.json`](skills/ai-socials/schemas/research_brief.schema.json)
- [`schemas/playbook_diff.schema.json`](skills/ai-socials/schemas/playbook_diff.schema.json)

### Social CLI, ingestion and analytics

- [`scripts/social.py`](skills/ai-socials/scripts/social.py)
- [`scripts/ai_social/cli.py`](skills/ai-socials/scripts/ai_social/cli.py)
- [`scripts/ai_social/validate.py`](skills/ai-socials/scripts/ai_social/validate.py)
- [`scripts/ai_social/ready.py`](skills/ai-socials/scripts/ai_social/ready.py)
- [`scripts/ai_social/metrics.py`](skills/ai-socials/scripts/ai_social/metrics.py)
- [`scripts/ai_social/metrics_import.py`](skills/ai-socials/scripts/ai_social/metrics_import.py)
- [`scripts/ai_social/retro.py`](skills/ai-socials/scripts/ai_social/retro.py)
- [`scripts/ai_social/liking_profile.py`](skills/ai-socials/scripts/ai_social/liking_profile.py)

### Image scope and learning

- [`references/recent-lessons.md`](skills/ai-socials/references/recent-lessons.md)
- [`references/learning.md`](skills/ai-socials/references/learning.md)
- [`assets/learning-ledger.json`](skills/ai-socials/assets/learning-ledger.json)

### Historical launch drafts, not publications

- [`assets/launch/2026-W44/READY.md`](skills/ai-socials/assets/launch/2026-W44/READY.md)
- [`assets/launch/2026-W44/plan.json`](skills/ai-socials/assets/launch/2026-W44/plan.json)

### Complete source file index

```text
.gitignore
SKILL.md
agents/openai.yaml
assets/icon.svg
assets/launch/2026-W44/READY.md
assets/launch/2026-W44/plan.json
assets/launch/2026-W44/w44-fb-1.json
assets/launch/2026-W44/w44-fb-2.json
assets/launch/2026-W44/w44-ig-1.json
assets/launch/2026-W44/w44-ig-2.json
assets/launch/2026-W44/w44-li-1.json
assets/launch/2026-W44/w44-li-2.json
assets/launch/2026-W44/w44-li-3.json
assets/launch/2026-W44/w44-x-1.json
assets/launch/2026-W44/w44-x-2.json
assets/learning-ledger.json
assets/profile_copy.md
assets/source-manifest.json
brain/confidential_terms.json
brain/hook_library.json
brain/hypotheses.json
brain/pillars.json
brain/platform_rules.json
brain/playbook.md
brain/playbook_rules.json
brain/profiles.json
brain/slots.json
brain/targets.json
brain/voice.md
pytest.ini
references/caption-mode.md
references/growth-strategy.md
references/learning.md
references/recent-lessons.md
references/roles.md
references/workflows.md
schemas/content_plan.schema.json
schemas/draft_post.schema.json
schemas/eval_report.schema.json
schemas/playbook_diff.schema.json
schemas/research_brief.schema.json
scripts/ai_social/__init__.py
scripts/ai_social/__main__.py
scripts/ai_social/bandit.py
scripts/ai_social/cli.py
scripts/ai_social/ingest/__init__.py
scripts/ai_social/ingest/linkedin.py
scripts/ai_social/ingest/meta.py
scripts/ai_social/ingest/x_archive.py
scripts/ai_social/lang.py
scripts/ai_social/liking_profile.py
scripts/ai_social/metrics.py
scripts/ai_social/metrics_import.py
scripts/ai_social/models.py
scripts/ai_social/pullers/__init__.py
scripts/ai_social/pullers/http.py
scripts/ai_social/pullers/instagram.py
scripts/ai_social/pullers/x.py
scripts/ai_social/ready.py
scripts/ai_social/retro.py
scripts/ai_social/storage.py
scripts/ai_social/validate.py
scripts/requirements.txt
scripts/social.py
tests/conftest.py
tests/fixtures/linkedin/Comments.csv
tests/fixtures/linkedin/Reactions.csv
tests/fixtures/linkedin/Shares.csv
tests/fixtures/meta/connections/followers_and_following/followers_1.json
tests/fixtures/meta/your_facebook_activity/comments_and_reactions/comments.json
tests/fixtures/meta/your_facebook_activity/comments_and_reactions/likes_and_reactions_1.json
tests/fixtures/meta/your_instagram_activity/comments/post_comments_1.json
tests/fixtures/meta/your_instagram_activity/likes/liked_comments.json
tests/fixtures/meta/your_instagram_activity/likes/liked_posts.json
tests/fixtures/x/data/like.js
tests/fixtures/x/data/tweets.js
tests/helpers.py
tests/test_cli.py
tests/test_ingest_profile.py
tests/test_launch_pack.py
tests/test_metrics_bandit.py
tests/test_models_lang.py
tests/test_portability_and_readiness.py
tests/test_pullers_import.py
tests/test_retro.py
tests/test_storage.py
tests/test_validate.py
```


<a id="suno-instrumental-prompts"></a>
## Suno Instrumental Prompt Helper

**Entry:** [SKILL.md](skills/suno-instrumental-prompts/SKILL.md)  |  **Source files:** 3  |  **Single-skill archive:** [skill.zip](skill_packages/suno-instrumental-prompts/skill.zip)

### Compact Styles-field cue compiler

- [`SKILL.md`](skills/suno-instrumental-prompts/SKILL.md)

### UI metadata and icon

- [`agents/openai.yaml`](skills/suno-instrumental-prompts/agents/openai.yaml)
- [`assets/icon.svg`](skills/suno-instrumental-prompts/assets/icon.svg)

### Complete source file index

```text
SKILL.md
agents/openai.yaml
assets/icon.svg
```
