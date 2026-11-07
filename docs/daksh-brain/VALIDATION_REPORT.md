# Daksh Brain architecture validation

**Prepared: 7 November 2026.** Baseline: `4c7276d9388817c175ad7ad85caa3130d6ca912c`. This report describes observed local checks before push; Ubuntu CI runs from the committed workflow. It does not claim model/media quality or active providers.

## Specification and inventory

| Check | Observed result |
|---|---|
| Master hierarchy | Daksh Brain is the single root; all 27 other roles have it as parent |
| Agent contracts | 28 present with mission, inputs, ownership, preserved locks, outputs, completion and escalation |
| Workflow graphs | 27 acyclic templates; known agents, required inputs/checks, accountable terminal; substantive work feeds final QC |
| JSON contracts | Four valid Draft 2020-12 schemas with four valid synthetic examples |
| Offline preview | Screenplay-to-film preview prints deterministic dependency batches with zero workers/provider calls |
| Missing input behavior | Blank/wrong-type objective blocked; no private input values echoed by preview |
| Skill inventory | 669 readable source records, 11 bundled skills, 390 exact session-listed; 4 policy-disabled and 268 disk-only records distinguished |
| Tool inventory | 628 records: 615 tool-registry capabilities plus 13 native declarations |
| Catalog completeness | Zero scan errors, zero unmatched declared session skills; unique identities and valid owner references |
| Source portability | No machine-specific home path in catalog output; source hashes are labelled metadata hashes |

## Observed deterministic checks

Commands used a local isolated Python 3.14 validation environment. The CI runner is Ubuntu/Python 3.12, matching the repository's existing intended gate.

| Suite/check | Local result |
|---|---|
| `tools/daksh_architecture.py validate` | Pass: 28 agents, 27 workflows, four schemas, 669 catalog sources, 11 bundled skills |
| Root `tests/` | 30 passed, 3 subtests passed |
| Dubbing | 44 passed, 18 subtests passed |
| Music | 32 passed, 12 subtests passed |
| Location | 40 passed, 3 subtests passed |
| Socials | 82 passed |
| God Mode scanner | 6 passed |
| Brain-eval script tests | 16 passed in an environment whose interpreter path contains no spaces |
| Grader selftest | 12 cases, zero problems |
| Routing | 8/8 passed |
| Existing live-brain validation | Passed; live-brain content/revision unchanged |
| Existing skill structure checks | 11/11 passed |
| Existing Daksh memory/orchestrator suite on this Mac | 30 passed, 37 failed; failures require Linux-only `os.listxattr`/`os.setxattr` APIs absent from this Python build |

The memory/orchestrator source scripts were not changed by this edition. Their Mac platform failure is not hidden or counted as a passing gate. Ubuntu CI is the appropriate full regression check. An initial brain-eval test also exposed the existing test command's unquoted interpreter path when the virtual environment lived under a directory with spaces; rerunning that unchanged suite in a real temporary environment without spaces passed all 16 tests. Neither issue was “fixed” by weakening tests or modifying unrelated runtime code.

## Independent review and fixes

A separate reviewer inspected the new registry, planner, docs and catalogs against raw source. The review identified and this edition fixed:

1. QC could previously depend only on intake while production finished in parallel. Validation now requires a final independent-QC node to depend transitively on every required production branch; a negative regression covers the bypass.
2. Empty/wrong-type objectives could appear ready. Input readiness now rejects blank text and incorrect objective types; nine negative inputs are tested.
3. The season-batch template omitted the Music branch described by the workflow docs. The score branch now feeds final review.

The reviewer found no new credential/private-chat leakage or deployed-runtime overclaim in the inspected additions. That is a scoped inspection result, not an assertion about every historical file or every future provider.

## Limits and remote verification

- No paid generations, external messages, account changes, scheduler creation, production deployment or new model training were performed.
- Structural tests do not prove identity, geometry, pronunciation, performance or commercial quality.
- The new CI gate includes architecture/schema validation and root tests; existing skill/regression/eval/brain checks remain intact.
- The push must preserve the existing base tree, including source snapshots and symlinks, and use a non-forced expected-head update. Verify the resulting remote head, changed files and Actions result after push.
