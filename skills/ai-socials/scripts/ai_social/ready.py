"""Render a week's drafts into READY.md: the one file Manik opens to post.

Deterministic on purpose, so the pack always matches the validated JSON
(no LLM re-typing the copy and introducing drift).
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ai_social.models import parse_ts

PLATFORM_NAME = {"linkedin": "LinkedIn", "instagram": "Instagram", "facebook": "Facebook", "x": "X"}


def load_drafts(folder: Path) -> list[dict[str, Any]]:
    """Load every draft JSON in ``folder`` (skips plan.json and *.eval.json), sorted by slot.

    Raises:
        ValueError: If a draft has no ``slot_ist`` or a file is not valid JSON.
    """
    drafts = []
    for path in sorted(folder.glob("*.json")):
        if path.name == "plan.json" or path.name.endswith(".eval.json"):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}: invalid JSON ({exc.msg})") from exc
        if not data.get("slot_ist"):
            raise ValueError(f"{path.name}: missing slot_ist")
        drafts.append(data)
    return sorted(drafts, key=lambda d: parse_ts(d["slot_ist"]))


def _when(slot: str) -> str:
    dt: datetime = parse_ts(slot)
    return dt.strftime("%a %d %b, %H:%M IST")


def render_ready(folder: Path, week: str) -> str:
    """Build the Markdown pack for ``week`` from the drafts in ``folder``."""
    drafts = load_drafts(folder)
    open_items = [(d["post_id"], c) for d in drafts for c in d.get("confirm", [])]
    lines = [
        f"# AI Social: ready-to-post pack, {week}",
        "",
        f"{len(drafts)} posts. {len(open_items)} item(s) need your answer before posting (see the end).",
        "After each post goes live, log it: `ai-social log-post <post>.json` with `url` and `published_at` filled in.",
        "",
        "## Schedule",
        "",
        "| When | Platform | Hook | Format | Test |",
        "|---|---|---|---|---|",
    ]
    for d in drafts:
        hook = d["text"].strip().splitlines()[0].replace("|", "/")
        lines.append(f"| {_when(d['slot_ist'])} | {PLATFORM_NAME[d['platform']]} | {hook} | {d['format']} | {d['experiment_id']} |")

    for d in drafts:
        lines += ["", "---", "", f"## {_when(d['slot_ist'])} · {PLATFORM_NAME[d['platform']]} · `{d['post_id']}`", ""]
        lines.append(f"Pillar `{d['pillar']}` · hook `{d['hook_type']}` · language `{d['language']}` · AI label {'ON' if d['ai_label'] else 'off'}")
        lines += ["", "**Post text**", "", "```", d["text"].strip(), "```"]
        if d.get("thread"):
            lines += ["", "**Thread (one tweet per block)**"]
            for i, tweet in enumerate(d["thread"], start=1):
                lines += ["", f"{i}/", "```", tweet.strip(), "```"]
        if d.get("slides"):
            lines += ["", "**Slides**", ""]
            lines += [f"{i}. {s}" for i, s in enumerate(d["slides"], start=1)]
        if d.get("hashtags"):
            lines += ["", "**Hashtags:** " + " ".join(d["hashtags"])]
        if d.get("first_comment"):
            lines += ["", "**First comment / own reply:**", "", "```", d["first_comment"], "```"]
        if d.get("media_brief"):
            lines += ["", f"**Media brief:** {d['media_brief']}"]

    lines += ["", "---", "", "## Needs your answer before posting", ""]
    if open_items:
        lines += [f"- `{pid}`: {item}" for pid, item in open_items]
    else:
        lines.append("Nothing. Sab ready hai.")
    return "\n".join(lines) + "\n"
