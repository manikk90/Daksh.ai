# Writing eval cases

A case lives in `skills/brain-evals/cases/*.json` (a JSON list). Fields:

| Field | Meaning |
|---|---|
| `id` | Unique, `<skill-prefix>-<rule>` (e.g. `dir-no-refs-line`) |
| `skill` | The owning skill ID under `skills/` |
| `kind` | `regression` (approved lock, must hold) · `capability` (new ability being hill-climbed) · `routing` (a prompt must route to the skill) |
| `lock` | The source file and rule the case encodes. Never write a case without a source. |
| `task` | A self-contained prompt for the agent. Include every tag and exact line the agent needs. |
| `checks` | A list of deterministic checks (types below) |
| `fixtures.pass` / `fixtures.fail` | At least one known-good and one known-bad output. `selftest` proves the checks separate them. |
| `strip_fences` | Default true: markdown ``` lines are ignored before grading |

## Check types
| Type | Params | Use for |
|---|---|---|
| `regex_present` / `regex_absent` | `pattern`, `flags` (`i`, `s`) | Required or forbidden wording, e.g. no `Refs (continuity)` |
| `count_regex` | `pattern`, `min`, `max` | Exactly one `DIALOGUE:` line |
| `last_line` | `pattern` | DIALOGUE as absolute last content |
| `blank_line_before` | `pattern` | Blank line before DIALOGUE |
| `tags` | `required`, `allowed`, `forbidden` | Exact `@tags`, frame-local inventory |
| `max_chars` | `max` | The Suno 800-character cap and other length budgets |
| `preserves_words` | `text` | Word-locked dialogue. Ignores `[tags]`, punctuation and case; order must match |
| `scan_top` | `expect`, `within` | Routing: the skill appears in gm_scan's top N for the task |

## Good case checklist
- The task tempts the known failure (e.g. a tight shot in a crowd scene, to test the `@crowd` rule).
- Its checks test only the lock, so a valid creative choice can't fail it.
- The fail fixture is a realistic mistake, not gibberish.
- When a lock is scoped (one project or shot), the task states that scope.
- **Graduation:** a `capability` case that passes ≥ 90% across two runs becomes `regression`.
- When Manik supersedes a lock, update or retire its case in the same change. Don't leave contradictory cases.
