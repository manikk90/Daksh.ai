#!/usr/bin/env python3
"""Run the imported core in writable state outside the installed skill."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import sys

SKILL_ROOT = Path(__file__).resolve().parents[1]

def initialize(home: Path) -> None:
    if home == SKILL_ROOT or SKILL_ROOT in home.parents:
        raise ValueError("choose a workspace outside the installed skill")
    for folder in ("brain", "schemas"):
        for source in (SKILL_ROOT / folder).rglob("*"):
            if source.is_file():
                target = home / folder / source.relative_to(SKILL_ROOT / folder)
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    shutil.copy2(source, target)
    for folder in ("logs", "data", "drafts", "retro"):
        (home / folder).mkdir(parents=True, exist_ok=True)
    examples = home / "examples" / "2026-W44"
    if not examples.exists():
        shutil.copytree(SKILL_ROOT / "assets" / "launch" / "2026-W44", examples)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Socials workspace adapter")
    parser.add_argument("--home", required=True, type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    home = args.home.expanduser().resolve()
    try:
        initialize(home)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.command == ["init"]:
        print(json.dumps({"initialized": str(home), "existing_state_preserved": True}))
        return 0
    if not args.command:
        parser.error("give init or a core command such as status")
    if (home / "deps").is_dir():
        sys.path.insert(0, str(home / "deps"))
    try:
        from ai_social.cli import main as core_main
    except ModuleNotFoundError as exc:
        if exc.name not in {"jsonschema", "attrs", "referencing", "rpds", "jsonschema_specifications"}:
            raise
        print("Install scripts/requirements.txt into <workdir>/deps and retry.", file=sys.stderr)
        return 2
    return core_main(["--home", str(home), *args.command])

if __name__ == "__main__":
    raise SystemExit(main())
