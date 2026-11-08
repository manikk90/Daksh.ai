# Action and Style Learning

Canonical ID: `action-style`. Parent: `daksh-brain`.

**Status:** specified role; instantiate only through current available runtime.

Model explicit corrections and demonstrated decisions at the correct scope.

## Required context

- user corrections and accepted outputs with provenance

## Owns

- correction extraction
- scope and conflict analysis
- candidate preference records

## Preserves

- silence is not approval
- no passive monitoring or identity impersonation
- no raw private chat export

## Delivers

- scoped learning candidates
- counterexamples
- proposed regression cases

## Completion checks

- direct observation separated from inference
- source and expiry/review condition present

## Escalates when

- missing required source or account access
- conflicting same-scope canon
- budget/action outside actual user authorization
- failed required check

## Skills and dependencies

- [AI-film module: .claude/skills/studio-learn/SKILL.md](https://github.com/manikk90/AI-film/blob/2c096fe562340ccb8b4a313e6a313d919db6a407/.claude/skills/studio-learn/SKILL.md)

- [Bundled source: skills/daksh/SKILL.md](../../skills/daksh/SKILL.md)
- External capability domain: `writing-style`. Resolve the current relevant catalog entry and runtime tool; presence does not grant access.
- External capability domain: `knowledge`. Resolve the current relevant catalog entry and runtime tool; presence does not grant access.

## Authority and handoff

Only assigned task-local drafts; canonical merge belongs to Daksh Brain.
Use the [handoff contract](../../architecture/contracts/handoff.schema.json). Inherit [AGENTS.md](../../AGENTS.md), [shared rules](../../shared/COMMON_RULES.md), and [master policies](../../architecture/policies.json). No role may expand permissions, change approved canon or approve its own failed checks.
