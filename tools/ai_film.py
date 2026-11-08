#!/usr/bin/env python3
"""Run the pinned AI-film production CLI and Mann editor under Daksh Brain.

Commands preserve the caller's working directory and the upstream exit codes.
This adapter never installs dependencies, updates sources, or records approvals.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "integrations/ai-film.json"
BOOTSTRAP = (
    "import runpy,sys; "
    "sys.path.insert(0,sys.argv.pop(1)); "
    "target=sys.argv.pop(1); "
    "runpy.run_module(target,run_name='__main__',alter_sys=True)"
)


class IntegrationError(ValueError):
    """A missing, changed, or inconsistent integration source."""


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def inside(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if Path(relative).is_absolute() or not path.is_relative_to(root.resolve()):
        raise IntegrationError(f"Integration path escapes its source root: {relative}")
    return path


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if result.returncode:
        raise IntegrationError(result.stderr.strip() or "Git source check failed")
    return result.stdout.strip()


def validate(root: Path = ROOT) -> dict:
    config = read_json(root / MANIFEST)
    source = config["source"]
    module = inside(root, source["path"])
    if not (module / ".git").exists() or not (module / "aifilm/__main__.py").is_file():
        raise IntegrationError(
            "AI-film is not initialized. From the Daksh.ai root run: "
            "git submodule update --init --recursive -- modules/ai-film"
        )
    if config["controller"] != "daksh-brain":
        raise IntegrationError("AI-film must remain under Daksh Brain")
    actual = git(module, "rev-parse", "HEAD")
    if actual != source["commit"]:
        raise IntegrationError("AI-film checkout differs from integrations/ai-film.json; reconcile the pin first")
    entries = git(root, "ls-files", "--stage", "--", source["path"]).splitlines()
    expected = f"160000 {source['commit']} 0\t{source['path']}"
    if entries != [expected]:
        raise IntegrationError("AI-film gitlink and integration manifest disagree")
    url = git(root, "config", "--file", ".gitmodules", "--get", "submodule.modules/ai-film.url")
    if url != source["url"]:
        raise IntegrationError("AI-film URL differs from the declared upstream")
    if git(module, "status", "--porcelain", "--untracked-files=no"):
        raise IntegrationError("AI-film tracked sources have local edits; review and commit them upstream before changing the pin")

    agents = {a["id"] for a in read_json(root / "architecture/agents.json")["agents"]}
    workflows = {w["id"] for w in read_json(root / "architecture/workflows.json")["workflows"]}
    if not set(config["workflow_ids"]) <= workflows:
        raise IntegrationError("Unknown AI-film workflow mapping")
    for role, owner in config["role_mapping"].items():
        if owner not in agents:
            raise IntegrationError(f"Unknown Daksh owner for AI-film role {role}")
    inventory = read_json(root / config["skill_inventory"])
    if inventory["source_commit"] != actual:
        raise IntegrationError("AI-film skill inventory has a stale source revision")
    recorded = set()
    for skill in inventory["skills"]:
        path = inside(module, skill["path"])
        if skill["path"] in recorded or skill["owner_agent_id"] not in agents:
            raise IntegrationError("Duplicate AI-film skill or unknown skill owner")
        recorded.add(skill["path"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != skill["sha256"]:
            raise IntegrationError(f"Changed AI-film skill: {skill['path']}")
    actual_skills = {p.relative_to(module).as_posix()
                     for directory in ("skills", ".claude/skills")
                     for p in (module / directory).glob("*/SKILL.md")}
    if recorded != actual_skills:
        raise IntegrationError("AI-film skill inventory omits or invents source files")
    return {"status": "source_valid", "controller": config["controller"],
            "source_commit": actual, "skills": len(recorded),
            "workflows": config["workflow_ids"], "provider_calls": 0,
            "note": "Source validation only; media quality and provider readiness are not established."}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "status", "film", "mann"))
    if not argv or argv[0] in ("-h", "--help"):
        parser.print_help()
        return 0
    command = parser.parse_args(argv[:1]).command
    remaining = argv[1:]
    if command in ("validate", "status") and remaining:
        parser.error(f"{command} takes no arguments")
    try:
        status = validate()
        if command in ("validate", "status"):
            print(json.dumps(status, ensure_ascii=False, indent=2))
            return 0
        module = inside(ROOT, read_json(ROOT / MANIFEST)["source"]["path"])
        target = "aifilm" if command == "film" else "aifilm.editor"
        if remaining[:1] == ["--"]:
            remaining = remaining[1:]
        return subprocess.run([sys.executable, "-c", BOOTSTRAP, str(module), target, *remaining]).returncode
    except (IntegrationError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"AI-film integration error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
