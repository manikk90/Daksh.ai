# GM: maniik brain ka next architecture
**Date:** 2026-11-01 | **Mode:** gm | **Status:** proposal
**Goal:** Is repo ko aisa AI-founder brain banana jo khud seekhe, khud capabilities banaye, aur har tool (Claude Code, ChatGPT, Codex) mein chale.
**Done means:** ek ranked architecture, aur pehla step jo aaj build ho sake.

## Verdict
Abhi bottleneck naye agents ki kami nahi hai. Problem ye hai ki **brain ka koi ek source of truth nahi hai, aur uski learning kisi gate se hokar nahi guzarti.** Memory (`DAKSH_BRAIN.json`) aur nightly learning ChatGPT Library aur automations mein hain. Skills repo mein hain. Aur koi skill sach mein kaam karti hai ya nahi, ye ek bhi behavior test se prove nahi hota. Isliye 3 cheezein karni hain:
1. Repo ko single source of truth banao.
2. Har learning ya skill edit tabhi apply ho jab wo behavior evals pass kare.
3. Ek nightly cloud scheduled task jo `gm`-style improvement ka PR khole, aur aap merge karo.
Iske baad naye agents compounding tarike se badhenge.

## Brain recon (repo mein pehle se kya hai)
| Asset | Path | Reuse kaise |
|---|---|---|
| Daksh memory engine | `skills/daksh/scripts/brain.py` | Revision-guarded append, supersede aur retrieve pehle se hain. Isse repo-hosted brain file par chalao. |
| Brain snapshot | `runtime_state/DAKSH_BRAIN.json` | Snapshot folder hai, ise mat chhedo. Iska ek copy live file ka seed banega. |
| Learning loop spec | `skills/daksh/references/weekly-learning.md` | 9-step nightly/Sunday loop pehle se likha hai. Bas runtime ChatGPT hai. |
| Orchestrator + tests | `skills/daksh/scripts/orchestrator.py` (63 tests) | Ye DAG aur handoff logic hai. Reuse karo. |
| Script regression suites | 5 skills, 261 tests | Ye scripts ko test karte hain, agent behavior ko nahi. |
| God Mode + scanner | `skills/god-mode/` | Research aur capability-gap detection ke liye. |
| User locks (golden truth) | Director, Socials, Dubbing ke SKILL.md overlays | Ye ready-made eval cases hain, jaise "DIALOGUE last", `@mukund-03`, "Pinterest Title alag". |

**Gaps:**
- (a) Live memory repo mein nahi hai.
- (b) Behavior/trigger evals zero hain.
- (c) Learning ka koi eval gate nahi, rules sirf likh diye jaate hain.
- (d) Skills ka layout cross-tool standard path par nahi hai.
- (e) Nightly loop ChatGPT automation par tika hai, repo ke saath sync nahi hota.

## Architecture
```text
Manik ──(gm / tasks / corrections)──> maniik (founder) ──> Daksh (orchestrator) ──> specialists
                                         │                        │
                                         ▼                        ▼
                               research/god-mode/         brain/DAKSH_BRAIN.json  (repo = source of truth)
                                         │                        │
                                         └──────> evals/ (golden cases from user locks, trigger cases)
                                                         │  pass?  ── no ──> reject edit (ledger: rejected)
                                                         ▼ yes
                                     nightly cloud scheduled task ──> branch + PR ──> Manik merge
                                                         │
                                     export: skill_packages/*.zip (ChatGPT) · .agents/skills (Codex/others)
```
- **Repo = brain:** memory, skills, evals aur research sab git mein. Har change versioned rahega aur revert ho sakega.
- **Eval gate:** GRASP-style rule. Skill ya lesson ka koi bhi edit tabhi merge ho jab regression evals ~100% pass rahein aur target capability eval behtar ho.
- **Nightly scheduled task:** Claude Code cloud scheduled task repo clone karega, learning loop chalayega, `claude/`-prefixed branch par PR kholega. Main par seedha push nahi karega.
- **Portable exports:** wahi skills Claude Code (`.claude/skills`), Codex/others (`.agents/skills`) aur ChatGPT (`skill.zip`) mein chalengi.

## Agents and skills
| Action | ID / path | Kaam |
|---|---|---|
| create | `skills/brain-evals/` | Golden cases (`cases/*.json`): input, must-contain/must-not rules, owning skill. Plus `run_evals.py`, jisme deterministic graders (regex/tag/order checks) ho aur model-grader ka hook. Trigger cases bhi: kaunse prompt par kaunsi skill fire honi chahiye. |
| create | `brain/` (live) | `DAKSH_BRAIN.json` live copy, `brain.py validate` CI mein. |
| extend | `skills/daksh/references/weekly-learning.md` | Runtime option add: repo + Claude Code scheduled task, PR-gated. ChatGPT path history ke liye rahe. |
| extend | `skills/god-mode/SKILL.md` | `gm build` ke liye shart: nayi skill ke saath kam se kam 3 eval cases bhi aayenge. |
| create | `.agents/skills/` → `skills/*` (symlinks) | Cross-tool standard discovery path. |
| reuse | `skills/daksh/scripts/orchestrator.py`, `brain.py` | Koi rewrite nahi. |

## Hacks
1. **User corrections = free eval dataset:** har V5/V5.1 lock (DIALOGUE last, no `Refs (continuity)` line, `@crowd` sirf visible ho tab, IG+FB ka shared caption) ek deterministic test ban jata hai. | gain: day-1 par ~30+ cases, zero cost | risk: sirf format pakdega, creative quality nahi.
2. **With-skill vs without-skill A/B:** jo skill baseline model ko beat na kare, use kaato ya chhota karo. | gain: context halka, routing sharp | risk: 5+ trials chahiye, ek run ka koi matlab nahi.
3. **Description = trigger:** skill sirf apne name aur description se fire hoti hai. Trigger evals se description tune karo. | gain: galat routing kam | risk: zyada broad description doosri skills ka kaam chheen leti hai.
4. **PR-gated autonomy:** nightly task khud seekhe, lekin merge aap karo. | gain: autonomy aur safety dono | risk: PRs ka review backlog ban sakta hai. Isliye har PR mein ek hi theme rakho.
5. **Capability → regression graduation:** jo capability eval consistently pass ho, wo regression suite mein chala jaye. | gain: brain peeche nahi jaata | risk: suite ka size badhega.
6. **Library lifecycle (Ratchet/GRASP idea):** skill library ko chhota aur versioned rakho. Duplicate ya conflicting rules ko retire karo, unhe jama mat karte jao. | gain: drift kam | risk: purana sahi rule retire ho sakta hai. Isliye retire bhi eval-gated ho.

## Execution plan
1. **Aaj (`gm build`):** `skills/brain-evals/` banao. V5.1 ke Director aur Socials locks se ~15 deterministic cases aur `run_evals.py` + tests. Ek existing prompt sample par chala ke baseline nikalo.
2. `brain/DAKSH_BRAIN.json` live copy aur ek validate step. `.agents/skills` symlinks.
3. `weekly-learning.md` mein repo-runtime path, aur `god-mode` mein eval-case wali shart.
4. Claude Code scheduled task (nightly 23:00 IST): learning loop, phir evals, phir PR. **Ye aapki approval ke baad hi banega**, kyunki ye ek account-level automation hai.
5. 2 hafte baad: with/without A/B se weak skills cut ya shrink karo.

## Smallest experiment
Native Director ke 10 locked rules ko eval cases mein convert karo. 5 prompt-fix tasks ko skill ke saath aur bina skill, 5–5 trials chalao.
**Pass:** with-skill pass rate ≥ 90% aur baseline se ≥ 20 points upar.
**Kill signal:** with-skill bhi < 70% ho, ya baseline ke barabar ho. Tab problem skill ke text mein hai. Naye agents banane se pehle Director SKILL.md (34 KB) ko chhota karo.

## Sources
- [V] Claude Code docs, "Automate work with scheduled tasks" (formerly routines): schedule, API aur GitHub triggers; research preview; Pro/Max/Ultra/Team/Enterprise. https://code.claude.com/docs/en/routines (checked 2026-11-01)
- [R] Agent Skills open standard (Dec 2025), SKILL.md cross-tool adoption, `.agents/skills` convention: https://noqta.tn/en/news/skill-md-open-standard-30-ai-coding-tools-adoption-2026 , https://atlan.com/know/ai-agent/ai-agent-skills/what-are-agent-skills/ (adoption counts sources mein alag-alag hain. agentskills.io is session ke network se blocked tha, isliye primary spec padha nahi gaya.)
- [R] Anthropic Engineering, "Demystifying evals for AI agents" (~Jan 2026): capability vs regression evals, graders, pass@k. https://anthropic.com/engineering/demystifying-evals-for-ai-agents (search snippets se; poora article fetch nahi kiya)
- [R] Skill evals ka method (with/without skill, 5+ trials, KEEP/CUT): https://blog.mgechev.com/2026/02/26/skill-eval/ , https://pypi.org/project/skill-harness/ , https://buidlguidl.com/blog/evaluating-agent-skills
- [R] GRASP, regression-gated skill-library edits (May 2026): https://www.alphaxiv.org/abs/2605.29668 · MemSkill: https://www.emergentmind.com/topics/memskill · Ratchet ka library-drift lifecycle (May 2026, search snippet se)

## Open questions
- Primary runtime ChatGPT rahega ya Claude Code? **Default assumption:** dono. Repo source of truth rahega, ChatGPT ko `skill.zip` export milega.
- Nightly scheduled task banana hai? **Default:** abhi nahi. Pehle evals bano, phir aapke "haan" ke baad.
