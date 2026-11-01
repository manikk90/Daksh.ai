"""Filesystem layout and jsonl helpers.

All state lives in plain files under the repo root so git is the version
history and rollback mechanism for the agent's brain.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator


@dataclass(frozen=True)
class Paths:
    """Every file AI Social reads or writes, resolved from one root."""

    root: Path

    @classmethod
    def from_env(cls, start: Path | None = None) -> "Paths":
        """Resolve the repo root.

        ``AI_SOCIAL_HOME`` wins if set. Otherwise walk up from ``start`` (default:
        cwd) to the first folder holding both ``brain/`` and ``schemas/``, so the
        CLI works from any subfolder like ``drafts/2026-W44``. Falls back to cwd.
        """
        env = os.environ.get("AI_SOCIAL_HOME")
        if env:
            return cls(Path(env).resolve())
        here = (start or Path.cwd()).resolve()
        for folder in (here, *here.parents):
            if (folder / "brain").is_dir() and (folder / "schemas").is_dir():
                return cls(folder)
        return cls(here)

    @property
    def brain(self) -> Path:
        return self.root / "brain"

    @property
    def logs(self) -> Path:
        return self.root / "logs"

    @property
    def data(self) -> Path:
        return self.root / "data"

    @property
    def retro(self) -> Path:
        return self.root / "retro"

    @property
    def schemas(self) -> Path:
        return self.root / "schemas"

    @property
    def posts_log(self) -> Path:
        return self.logs / "posts.jsonl"

    @property
    def metrics_log(self) -> Path:
        return self.logs / "metrics.jsonl"

    @property
    def events(self) -> Path:
        return self.data / "events.jsonl"

    @property
    def playbook_rules(self) -> Path:
        return self.brain / "playbook_rules.json"

    @property
    def liking_profile(self) -> Path:
        return self.brain / "liking_profile.json"

    @property
    def pillars(self) -> Path:
        return self.brain / "pillars.json"

    @property
    def platform_rules(self) -> Path:
        return self.brain / "platform_rules.json"

    @property
    def confidential_terms(self) -> Path:
        return self.brain / "confidential_terms.json"


def read_json(path: Path, default: Any = None) -> Any:
    """Read a JSON file, returning ``default`` when it does not exist."""
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, data: Any) -> None:
    """Write JSON atomically (temp file + rename) so a crash never half-writes the brain."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    tmp.replace(path)


def iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    """Yield rows from a jsonl file; a missing file yields nothing.

    Raises:
        ValueError: With the line number, if a row is not valid JSON.
    """
    if not path.exists():
        return
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{lineno}: invalid JSON ({exc.msg})") from exc


def append_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    """Append rows to a jsonl file and return how many were written."""
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    """Replace a jsonl file with ``rows`` and return how many were written."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    count = 0
    with tmp.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    tmp.replace(path)
    return count
