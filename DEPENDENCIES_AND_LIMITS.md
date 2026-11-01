# Dependencies, provenance and limits

## What is fully exported
Eight custom installed-skill directories are exact file copies from the available source mount: Daksh, maniik, AI Native Director, AI Location Director, AI Music Director, Ai Dubbing, AI Socials and Suno Instrumental Prompts. Each keeps its entrypoint, UI metadata, supporting references, scripts, schemas, templates, icons, ledgers and bundled tests where the source contains them. These are heterogeneous skills: not every skill has every folder.

The mapped maintenance dependency Skill Creator is included as an exact support-source snapshot. It is not presented as a newly installed custom agent.

## External provider dependencies
Daksh's registry explicitly maps Data and authored writing-style support. The addon contains their current readable entrypoint snapshots and a routing catalog. Provider-managed shared guides, app runtimes, remote APIs, credentials and account connections are not bundled. These two snapshots are not standalone validated plugin distributions.

Data's historical alias `data-analytics:index` resolves here to `skills://plugins/data/index/skill.md`. Writing-style alias `write-like-me:write-like-me` resolves to `skills://plugins/writing-style/write-like-me/skill.md`.

## Tools are not skills
Slack, Gmail, Files/Library, Drive, Calendar, browsing, image generation, audio generation and Automations are runtime tools/capabilities. A skill may direct their use but cannot export authentication, permissions, remote service code or live scheduler state. Reconnect/resolve actual tools in the target host; never put API secrets inside the skill files.

DOCX, PDF, Slides, Spreadsheets, Adobe and other installed general-purpose workflows are available host capabilities, not automatically permanent mappings to every custom agent. This export does not bulk-copy unrelated skills or mislabel them as user-approved agent mappings.

## Records and state
- Runtime IDs, scheduler bindings and past test counts in original sources are historical records. Live scheduler state was not checked or modified for this export.
- Ledgers preserve recorded lessons/research and their original status. Copying a ledger is not a new test, approval, audio render or visual review.
- Templates and fixtures are examples; they are not real production outputs. Social launch files remain drafts unless their own actual publication evidence says otherwise.
- Linked canonical project records, DAKSH_BRAIN live memory, original photos/videos/audio, external assets and full chat archives are not silently reconstructed. This is a skills-and-agent-files export, not a whole-account or production-media backup.
- Font files, environment files, cache files, symlinks and credential-named files are excluded by policy. Exact copied-source coverage and any exclusions are listed in `mapping/source_files.json`.

## Precedence
Current user instructions and approved scoped assets > export-side latest user overrides where applicable > current installed source rules > older readable dossier summaries > historical proposals. A later local correction is not automatically a global rule.

## Validation scope
See `verification/QA_REPORT.md`. Source identity, structure, JSON/YAML parsing, Python syntax and ZIP integrity are deterministic packaging checks. They do not establish that all media outputs, live tools, timers, account controls or plugin installs work. No production generation or external write is included.

## v3 recovery and remaining limits
Actual DAKSH_BRAIN.json, Laddu_Gopal_Production_Context.json revision 7 and AI_Writer_Pending_Maintenance_2026-10-29.json are now in runtime_state/. They are dated records. The Writer pending patch remains unapplied and the complete original source is unavailable. The exact expanded 100-preview set and full raw conversation/media archive remain unrecovered. Main MD consolidation is not live installation, current API verification or proof of future schedule execution.
