# Coverage, provenance and implementation boundary

## Pinned baseline

The baseline is `manikk90/Daksh.ai` main commit `4c7276d9388817c175ad7ad85caa3130d6ca912c`, observed through the authenticated GitHub connection. The full remote tree contained 487 entries. Existing active skill, shared, mapping, brain and agent source was read against that pinned revision; archived source folders remain unchanged by this edition.

## What this edition contains

- One authoritative Daksh Brain hierarchy, 28 detailed role contracts and 27 dependency-graph templates.
- Existing 11 repository skills remain source procedures: Dubbing, Location, Music, Native Director, Socials, Brain Evals, Daksh, Fashion, God Mode, maniik Work Ops and Suno Instrumental Prompts.
- A complete readable-on-disk skill metadata inventory, a separately recorded current-session skill manifest, and a tool capability inventory. Counts and scan errors are generated in [the catalog](../../catalog/SKILLS.md); disk-only and policy-disabled entries are explicit.
- Workflow, context, memory, tool, budget, approval, failure-recovery, QC, migration and operations specifications.
- Four structural handoff schemas, synthetic examples, an offline validator/plan preview, and regression tests.
- The hierarchy entry points in README, CLAUDE and founder/God Mode descriptions are reconciled with the user's 7 November direction.

## Source versus runtime status

| Material | What inclusion proves | What it does not prove |
|---|---|---|
| Existing agent dossier | The dated source is present in this private repo | A worker has been launched or its every claim is current |
| Repository `SKILL.md` | The procedure is bundled | External tools, providers and credentials are connected |
| External skill metadata | A skill source was readable/discoverable at the snapshot | The package is vendored, licensed for redistribution, session-enabled or authorized |
| Advertised tool metadata | A capability was advertised to this session | Account access, supported action success, valid credential or ongoing availability |
| Workflow/schema/role card | Design and structural expectations | A durable engine, scheduler, provider invocation or trained clone |
| Deterministic test | The tested rule/structure behaves as checked | Image identity, regional authenticity, voice quality, acting or commercial performance |

## Deliberate exclusions

Credentials, OAuth tokens, cookies, account-link handles, raw chat archives, hidden host/system/developer instructions, unrelated personal records and production media are not exported. Existing private repository records remain where they already were; new examples use synthetic IDs/content. The account connection does not authorize sending private content to public research tools.

Third-party installed skill bodies are not bulk-copied into this repo. Their names, descriptions, provenance and dependency states are catalogued so a future runtime can discover and load the properly installed/licensed original. Existing bundled third-party material retains its existing notices and license obligations. A catalog entry grants no redistribution rights.

## Known gaps

- AI Writer has a reconstructed dossier in [agents/AI_WRITER.md](../../agents/AI_WRITER.md); its original installable skill remains absent. Daksh must not claim it is an installed original worker.
- Full conversation history, original reference media, private remote skill libraries and every external account are not available merely because this repo exists.
- External skill inventory is a dated machine snapshot. It must be refreshed by explicit local source roots; fresh runtime discovery determines what can actually execute.
- Some legacy cross-references/snapshots describe older versions or earlier hierarchies. Current entry-point precedence is explicit; archives remain historical.
- Workflow nodes for multi-show and season batches are templates. They require per-show/per-episode expansion, capacity enforcement and real tool adapters before execution.
- The new planner does not enforce provider-side permissions or authenticate approval evidence. It validates a specification and previews ordering; runtime enforcement belongs to the future broker.
- Model/provider choices, field limits, prices and schedules must be verified in the actual account and installed documentation. No production deployment is included in this change.

## Compatibility and authority

The human remains final authority. Daksh Brain becomes the sole top AI controller; maniik founder/style guidance is advisory. Existing specialist-internal controllers and source locks stay intact. Existing strict ledger keys/states are unchanged, and new design contracts are not passed directly to `orchestrator.py`.

Source baseline is private repository content; supplementary local skills are inventoried metadata only. The catalog's portable source locators omit machine-specific home paths. Stored hashes identify metadata/source snapshot contents as labelled; they do not imply deployment or full package integrity.

## Refresh procedure

1. Pin the current repo and source revisions.
2. Supply explicit local skill source roots to [catalog/build_catalog.py](../../catalog/build_catalog.py); inspect its help before use.
3. Compare added/removed skills, providers, ownership and availability dimensions.
4. Resolve licensing and runtime dependencies before copying or activating a source.
5. Run the architecture gate, catalog gate and affected existing regressions.
6. Review the intended diff and push only the authorized changes; verify the remote result.
