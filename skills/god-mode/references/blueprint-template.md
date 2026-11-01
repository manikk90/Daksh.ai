# God Mode blueprint template

Copy this structure for every `gm` output and saved report. Keep the chat version tight. The saved file may hold the full source list.

```markdown
# GM: <goal in 5-8 words>
**Date:** YYYY-MM-DD | **Mode:** gm / gm deep / gm build | **Status:** proposal / built / tested

## Verdict
<2-3 lines: the one path to take and why it beats the alternatives>

## Brain recon (already in this repo)
| Asset | Path | Reuse how |
|---|---|---|
| <agent/skill/reference> | <path> | <reuse / extend / not relevant> |
**Gaps:** <what nothing covers yet>

## Architecture
```text
<input> -> <component> -> <component> -> <output>
            |                ^
         <memory/tool>   <feedback/eval loop>
```
<2-4 lines: what each new component does and where the existing agents plug in>

## Agents and skills
| Action | ID / path | Job |
|---|---|---|
| reuse | skills/ai-music-director | ... |
| extend | skills/<id>/references/<file>.md | ... |
| create | skills/<new-id>/ | ... |

## Hacks
1. **<hack>:** <how> | gain: <time/cost/quality> | risk: <what breaks>

## Execution plan
1. <today: smallest concrete step>
2. ...

## Smallest experiment
<test, metric, pass threshold, time box>
**Kill signal:** <the result that means stop or pivot>

## Sources
- [V] <title>, <url>, <published/checked date>  (V = verified this run)
- [R] <title>, <url>, <date>  (R = reported/secondary)

## Open questions
- <question>, default assumption: <assumption>
```

Rules: tables only where they compare; no filler sections. If a section is genuinely empty, write "none" instead of padding it.
