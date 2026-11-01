#!/usr/bin/env python3
"""Retrieve a small composition-pattern and source-frame subset; no media QC."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List pattern identifiers, names and possible uses")
    show = sub.add_parser("show", help="Read selected patterns and bounded evidence")
    show.add_argument("pattern_ids", nargs="+")
    show.add_argument("--evidence-limit", type=int, choices=range(0, 4), default=2)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        pack = json.loads((root / "assets/composition-patterns.json").read_text())
        patterns = {item["id"]: item for item in pack["patterns"]}
        if args.command == "list":
            result = [
                {key: item[key] for key in ("id", "name", "possible_dramatic_use")}
                for item in patterns.values()
            ]
        else:
            missing = sorted(set(args.pattern_ids) - patterns.keys())
            if missing:
                parser.error("Unknown pattern ID(s): " + ", ".join(missing))
            frames = {}
            if args.evidence_limit:
                corpus = json.loads((root / "assets/composition-study.frames.json").read_text())
                frames = {item["frame_id"]: item for item in corpus["frames"]}
            result = []
            for pattern_id in dict.fromkeys(args.pattern_ids):
                item = dict(patterns[pattern_id])
                if args.evidence_limit:
                    item["evidence_frames"] = [
                        frames[frame_id]
                        for frame_id in item["evidence_frame_ids"][:args.evidence_limit]
                    ]
                result.append(item)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Composition lookup unavailable: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
