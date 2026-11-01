#!/usr/bin/env python3
"""maniik brain evals: lock-compliance and routing checks for this repo's skills.

Commands
  selftest                 Grade every case's pass/fail fixtures. Proves the graders work. No model.
  routing                  Run routing (scan_top) cases against the current skill descriptions. No model.
  grade CASE_ID FILE       Grade one saved agent output against a case.
  regrade REPORT           Re-grade a saved run report with the current graders (no model calls).
  run                      Run cases through a real agent CLI, with and without the owning skill,
                           for N trials, and report pass rates and the skill's lift.

Examples
  python skills/brain-evals/scripts/run_evals.py selftest
  python skills/brain-evals/scripts/run_evals.py run --skill ai-native-director --trials 3 \
      --agent-cmd "claude -p" --out research/evals/2026-11-01-director.json

`--agent-cmd` receives the full prompt on stdin and must print the answer on stdout
(for example `claude -p` or `codex exec -`). Model runs cost usage, so keep trials small.
"""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from graders import grade  # noqa: E402

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parents[2]
CASES_DIR = HERE.parent / "cases"


def load_cases(cases_dir: Path = CASES_DIR) -> list[dict]:
    cases = []
    for path in sorted(cases_dir.glob("*.json")):
        for case in json.loads(path.read_text(encoding="utf-8")):
            case["_file"] = path.name
            cases.append(case)
    ids = [c["id"] for c in cases]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise SystemExit(f"duplicate case ids: {sorted(dupes)}")
    return cases


def case_ok(output: str, case: dict, root: Path) -> tuple[bool, list[dict]]:
    results = grade(output, case["checks"], root, fences=case.get("strip_fences", True))
    return all(r["ok"] for r in results), results


def cmd_selftest(cases: list[dict], root: Path) -> int:
    failures = 0
    for case in cases:
        if case.get("kind") == "routing":
            continue
        fx = case.get("fixtures", {})
        if not fx.get("pass") or not fx.get("fail"):
            print(f"FAIL {case['id']}: needs at least one pass and one fail fixture")
            failures += 1
            continue
        for sample in fx["pass"]:
            ok, res = case_ok(sample, case, root)
            if not ok:
                failures += 1
                print(f"FAIL {case['id']}: pass-fixture rejected -> {[r['detail'] for r in res if not r['ok']]}")
        for sample in fx["fail"]:
            ok, _ = case_ok(sample, case, root)
            if ok:
                failures += 1
                print(f"FAIL {case['id']}: fail-fixture accepted")
    n = sum(1 for c in cases if c.get("kind") != "routing")
    print(f"selftest: {n} cases, {failures} problems")
    return 1 if failures else 0


def cmd_routing(cases: list[dict], root: Path) -> int:
    rows = [c for c in cases if c.get("kind") == "routing"]
    passed = 0
    for case in rows:
        ok, res = case_ok(case["task"], case, root)
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'} {case['id']}: {res[0]['detail']}")
    print(f"routing: {passed}/{len(rows)} passed")
    return 0 if passed == len(rows) else 1


def build_prompt(case: dict, root: Path, with_skill: bool) -> str:
    task = case["task"]
    if not with_skill:
        return task
    skill_md = (root / "skills" / case["skill"] / "SKILL.md").read_text(encoding="utf-8")
    return ("You are running with the following skill loaded. Follow it exactly.\n"
            f"<skill name=\"{case['skill']}\">\n{skill_md}\n</skill>\n\n"
            "Work from the information given in the task. Do not use tools or read files.\n\n"
            f"Task:\n{task}")


def call_agent(cmd: str, prompt: str, timeout: int) -> str:
    # Run in an empty temp dir so the baseline can't read this repo's skills (no contamination).
    with tempfile.TemporaryDirectory(prefix="brain-eval-") as cwd:
        proc = subprocess.run(shlex.split(cmd), input=prompt, capture_output=True, text=True,
                              timeout=timeout, cwd=cwd)
    return proc.stdout


def cmd_run(cases: list[dict], root: Path, args) -> int:
    chosen = [c for c in cases if c.get("kind") != "routing"
              and (not args.skill or c["skill"] == args.skill)
              and (not args.case or c["id"] in args.case)]
    if not chosen:
        raise SystemExit("no cases selected")
    conditions = ["with_skill"] + ([] if args.no_baseline else ["baseline"])
    report = {"date": datetime.now(timezone.utc).isoformat(timespec="seconds"), "agent_cmd": args.agent_cmd,
              "trials": args.trials, "cases": []}
    jobs = [(ci, cond, t) for ci in range(len(chosen)) for cond in conditions for t in range(args.trials)]

    def work(job):
        ci, cond, _ = job
        case = chosen[ci]
        try:
            out = call_agent(args.agent_cmd, build_prompt(case, root, cond == "with_skill"), args.timeout)
        except subprocess.TimeoutExpired:
            out = ""
        ok, res = case_ok(out, case, root)
        return job, {"ok": ok, "failed": [r["detail"] for r in res if not r["ok"]], "output": out}

    results: dict = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        for job, run in pool.map(work, jobs):
            results.setdefault((job[0], job[1]), []).append(run)
    for ci, case in enumerate(chosen):
        row = {"id": case["id"], "skill": case["skill"]}
        for cond in conditions:
            runs = results[(ci, cond)]
            row[cond] = {"pass_rate": sum(r["ok"] for r in runs) / len(runs), "runs": runs}
        print(f"{case['id']}: " + "  ".join(f"{c}={row[c]['pass_rate']:.0%}" for c in conditions))
        report["cases"].append(row)
    summarize(report, conditions)
    print(json.dumps({k: v for k, v in report.items() if k != "cases"}, indent=2))
    if args.out:
        out = root / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"saved {args.out}")
    return 0


def summarize(report: dict, conditions: list[str]) -> None:
    for cond in conditions:
        report[f"{cond}_mean"] = round(sum(r[cond]["pass_rate"] for r in report["cases"]) / len(report["cases"]), 3)
    if "baseline" in conditions:
        report["lift"] = round(report["with_skill_mean"] - report["baseline_mean"], 3)


def cmd_regrade(cases: list[dict], root: Path, path: Path) -> int:
    report = json.loads(path.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in cases}
    conditions = [c for c in ("with_skill", "baseline") if c in report["cases"][0]]
    for row in report["cases"]:
        case = by_id[row["id"]]
        for cond in conditions:
            for run in row[cond]["runs"]:
                ok, res = case_ok(run["output"], case, root)
                run["ok"], run["failed"] = ok, [r["detail"] for r in res if not r["ok"]]
            runs = row[cond]["runs"]
            row[cond]["pass_rate"] = sum(r["ok"] for r in runs) / len(runs)
        print(f"{row['id']}: " + "  ".join(f"{c}={row[c]['pass_rate']:.0%}" for c in conditions))
    summarize(report, conditions)
    report["regraded"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "cases"}, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    sub.add_parser("routing")
    g = sub.add_parser("grade")
    g.add_argument("case_id")
    g.add_argument("file", type=Path)
    rg = sub.add_parser("regrade")
    rg.add_argument("report", type=Path)
    r = sub.add_parser("run")
    r.add_argument("--agent-cmd", required=True)
    r.add_argument("--skill")
    r.add_argument("--case", action="append")
    r.add_argument("--trials", type=int, default=3)
    r.add_argument("--timeout", type=int, default=300)
    r.add_argument("--workers", type=int, default=4)
    r.add_argument("--no-baseline", action="store_true")
    r.add_argument("--out")
    args = ap.parse_args(argv)
    cases = load_cases()
    root = args.root.resolve()
    if args.cmd == "selftest":
        return cmd_selftest(cases, root)
    if args.cmd == "routing":
        return cmd_routing(cases, root)
    if args.cmd == "regrade":
        return cmd_regrade(cases, root, args.report)
    if args.cmd == "grade":
        case = next((c for c in cases if c["id"] == args.case_id), None)
        if case is None:
            raise SystemExit(f"unknown case {args.case_id}")
        ok, res = case_ok(args.file.read_text(encoding="utf-8"), case, root)
        print(json.dumps({"case": case["id"], "ok": ok, "checks": res}, indent=2, ensure_ascii=False))
        return 0 if ok else 1
    return cmd_run(cases, root, args)


if __name__ == "__main__":
    sys.exit(main())
