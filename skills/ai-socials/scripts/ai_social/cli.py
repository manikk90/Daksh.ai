"""``ai-social`` command line. Every LLM agent calls these instead of doing maths itself.

Commands:
  ingest          parse LinkedIn / Meta / X exports into data/events.jsonl
  profile         rebuild brain/liking_profile.json from events
  log-post        append a published post (JSON file or stdin) to logs/posts.jsonl
  import-metrics  map a LinkedIn/Facebook metrics CSV onto logged posts
  pull            fetch Instagram or X metrics via API
  suggest         Thompson-sampling pick for slot/hook/language/format/pillar
  validate        check a draft / plan / brief / eval / diff file
  retro           build the weekly PlaybookDiff + report (writes nothing to brain/)
  apply-diff      apply an approved PlaybookDiff (requires --approve)
  ready           render drafts/<week>/ into a paste-ready READY.md
  status          one-screen summary
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from ai_social import __version__
from ai_social.bandit import suggest
from ai_social.ingest import parse_linkedin_export, parse_meta_export, parse_x_archive
from ai_social.liking_profile import build_liking_profile
from ai_social.metrics import load_posts, load_snapshots, log_metrics, log_post, score_posts
from ai_social.metrics_import import import_metrics_csv
from ai_social.models import LEARNABLE_DIMENSIONS, PLATFORMS, EngagementEvent, PostRecord, ValidationError
from ai_social.pullers.http import ApiError
from ai_social.ready import render_ready
from ai_social.retro import DiffRejected, apply_diff, group_stats, iso_week, propose_diff, render_report
from ai_social.storage import Paths, iter_jsonl, read_json, write_json, write_jsonl
from ai_social.validate import SCHEMAS, check_file


def _print(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_ingest(args: argparse.Namespace, paths: Paths) -> int:
    events: list[EngagementEvent] = []
    if args.linkedin:
        events += list(parse_linkedin_export(Path(args.linkedin)))
    if args.meta:
        events += list(parse_meta_export(Path(args.meta)))
    if args.x:
        events += list(parse_x_archive(Path(args.x)))
    if not (args.linkedin or args.meta or args.x):
        print("give at least one of --linkedin / --meta / --x", file=sys.stderr)
        return 2
    existing = [] if args.replace else [EngagementEvent.from_dict(r) for r in iter_jsonl(paths.events)]
    seen = {(e.platform, e.kind, e.timestamp, e.target_url, e.text) for e in existing}
    fresh = [e for e in events if (e.platform, e.kind, e.timestamp, e.target_url, e.text) not in seen]
    write_jsonl(paths.events, (e.to_dict() for e in existing + fresh))
    by: dict[str, int] = {}
    for e in fresh:
        by[f"{e.platform}/{e.kind}"] = by.get(f"{e.platform}/{e.kind}", 0) + 1
    _print({"new_events": len(fresh), "total_events": len(existing) + len(fresh), "by_type": by})
    return 0


def cmd_profile(args: argparse.Namespace, paths: Paths) -> int:
    events = [EngagementEvent.from_dict(r) for r in iter_jsonl(paths.events)]
    pillars = (read_json(paths.pillars, {}) or {}).get("pillars", [])
    profile = build_liking_profile(events, pillars, top_n=args.top)
    write_json(paths.liking_profile, profile)
    _print({k: profile[k] for k in ("total_events", "event_counts", "pillar_affinity", "notes")})
    return 0


def cmd_log_post(args: argparse.Namespace, paths: Paths) -> int:
    raw = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    data = json.loads(raw)
    rows = data if isinstance(data, list) else [data]
    if (args.url or args.published_at) and len(rows) != 1:
        print("--url / --published-at only work with a single post", file=sys.stderr)
        return 2
    for row in rows:
        row = dict(row)
        if args.url:
            row["url"] = args.url
        if args.published_at:
            row["published_at"] = args.published_at
        row.setdefault("published_at", row.get("slot_ist", ""))
        log_post(paths, PostRecord.from_dict(row))
    _print({"logged": len(rows)})
    return 0


def cmd_import_metrics(args: argparse.Namespace, paths: Paths) -> int:
    report = import_metrics_csv(Path(args.csv), args.platform, load_posts(paths), args.captured_at)
    log_metrics(paths, report.snapshots)
    _print({"imported": len(report.snapshots), "unmatched": report.unmatched, "bad_rows": report.bad_rows})
    return 0 if report.snapshots or not (report.unmatched or report.bad_rows) else 1


def cmd_pull(args: argparse.Namespace, paths: Paths) -> int:
    posts = load_posts(paths)
    if args.platform == "instagram":
        from ai_social.pullers.instagram import pull_instagram

        snaps = pull_instagram(posts)
    else:
        from ai_social.pullers.x import pull_x

        snaps = pull_x(posts)
    log_metrics(paths, snaps)
    _print({"platform": args.platform, "snapshots": len(snaps)})
    return 0


def cmd_suggest(args: argparse.Namespace, paths: Paths) -> int:
    candidates: Sequence[str] = args.candidates
    if not candidates:
        rules = read_json(paths.brain / "slots.json", {}) or {}
        candidates = rules.get(args.platform, []) if args.dimension == "slot" else []
    if not candidates:
        print("no candidates: pass --candidates or define brain/slots.json", file=sys.stderr)
        return 2
    scored = score_posts(load_posts(paths), load_snapshots(paths))
    _print(suggest(scored, args.platform, args.dimension, list(candidates), seed=args.seed))
    return 0


def cmd_validate(args: argparse.Namespace, paths: Paths) -> int:
    result = check_file(args.kind, Path(args.file), paths)
    _print(result)
    return 0 if result["pass"] else 1


def cmd_retro(args: argparse.Namespace, paths: Paths) -> int:
    today = date.fromisoformat(args.today) if args.today else datetime.now(timezone.utc).date()
    scored = score_posts(load_posts(paths), load_snapshots(paths))
    rules = read_json(paths.playbook_rules, {"version": 1, "rules": []})
    diff = propose_diff(scored, rules, today)
    week = iso_week(today)
    write_json(paths.retro / f"{week}.diff.json", diff)
    (paths.retro / f"{week}.md").write_text(render_report(diff, group_stats(scored)), encoding="utf-8")
    _print({"week": week, "scored_posts": diff["scored_posts"], "changes": len(diff["changes"]),
            "confirmations": len(diff["confirmations"]), "diff": f"retro/{week}.diff.json", "report": f"retro/{week}.md"})
    return 0


def cmd_apply_diff(args: argparse.Namespace, paths: Paths) -> int:
    diff = read_json(Path(args.file))
    if diff is None:
        print(f"no such diff: {args.file}", file=sys.stderr)
        return 2
    rules = read_json(paths.playbook_rules, {"version": 1, "rules": []})
    new_doc = apply_diff(rules, diff, approve=args.approve)
    write_json(paths.playbook_rules, new_doc)
    _print({"version": new_doc["version"], "rules": len(new_doc["rules"])})
    return 0


def cmd_ready(args: argparse.Namespace, paths: Paths) -> int:
    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"no such folder: {folder}", file=sys.stderr)
        return 2
    week = args.week or folder.name
    out = folder / "READY.md"
    out.write_text(render_ready(folder, week), encoding="utf-8")
    _print({"written": str(out)})
    return 0


def cmd_status(args: argparse.Namespace, paths: Paths) -> int:
    posts = load_posts(paths)
    scored = score_posts(posts, load_snapshots(paths))
    rules = read_json(paths.playbook_rules, {"version": 1, "rules": []})
    profile = read_json(paths.liking_profile, {}) or {}
    _print({
        "version": __version__,
        "playbook_version": rules.get("version"),
        "rules": len(rules.get("rules", [])),
        "posts_logged": {p: sum(1 for x in posts if x.platform == p) for p in PLATFORMS},
        "posts_scored": sum(1 for s in scored if s.normalized is not None),
        "liking_profile_events": profile.get("total_events", 0),
    })
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser (exposed for tests)."""
    p = argparse.ArgumentParser(prog="ai-social", description="AI Social deterministic core")
    p.add_argument("--home", help="repo root (default: $AI_SOCIAL_HOME or cwd)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("ingest")
    s.add_argument("--linkedin")
    s.add_argument("--meta")
    s.add_argument("--x")
    s.add_argument("--replace", action="store_true", help="drop existing events first")
    s.set_defaults(fn=cmd_ingest)

    s = sub.add_parser("profile")
    s.add_argument("--top", type=int, default=40)
    s.set_defaults(fn=cmd_profile)

    s = sub.add_parser("log-post")
    s.add_argument("file", help="post or draft JSON (object or list), or - for stdin")
    s.add_argument("--url", help="live post URL (needed for API metric matching)")
    s.add_argument("--published-at", help="actual publish time; defaults to the draft's slot_ist")
    s.set_defaults(fn=cmd_log_post)

    s = sub.add_parser("import-metrics")
    s.add_argument("--platform", required=True, choices=PLATFORMS)
    s.add_argument("--csv", required=True)
    s.add_argument("--captured-at")
    s.set_defaults(fn=cmd_import_metrics)

    s = sub.add_parser("pull")
    s.add_argument("--platform", required=True, choices=("instagram", "x"))
    s.set_defaults(fn=cmd_pull)

    s = sub.add_parser("suggest")
    s.add_argument("--platform", required=True, choices=PLATFORMS)
    s.add_argument("--dimension", required=True, choices=LEARNABLE_DIMENSIONS)
    s.add_argument("--candidates", nargs="*", default=[])
    s.add_argument("--seed", type=int)
    s.set_defaults(fn=cmd_suggest)

    s = sub.add_parser("validate")
    s.add_argument("kind", choices=tuple(SCHEMAS))
    s.add_argument("file")
    s.set_defaults(fn=cmd_validate)

    s = sub.add_parser("retro")
    s.add_argument("--today", help="YYYY-MM-DD (default: today UTC)")
    s.set_defaults(fn=cmd_retro)

    s = sub.add_parser("apply-diff")
    s.add_argument("file")
    s.add_argument("--approve", action="store_true")
    s.set_defaults(fn=cmd_apply_diff)

    s = sub.add_parser("ready")
    s.add_argument("folder", help="e.g. drafts/2026-W44")
    s.add_argument("--week")
    s.set_defaults(fn=cmd_ready)

    s = sub.add_parser("status")
    s.set_defaults(fn=cmd_status)
    return p


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI; returns a process exit code instead of raising for user errors."""
    args = build_parser().parse_args(argv)
    paths = Paths(Path(args.home).resolve()) if args.home else Paths.from_env()
    try:
        return int(args.fn(args, paths))
    except (ValidationError, DiffRejected, ApiError, ValueError, FileNotFoundError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
