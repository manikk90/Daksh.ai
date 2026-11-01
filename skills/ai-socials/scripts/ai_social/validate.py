"""Deterministic gates that run before (and independently of) the LLM Evaluator.

The Evaluator judges taste. This module checks things that must never depend
on taste: schema shape, hashtag caps, link placement, length limits,
confidential terms, unqualified "India's first" claims, AI-media labels, and
the anti-AI-slop rules from Manik's humanizer standard.

Result shape: ``{"pass": bool, "blocking": [...], "warnings": [...]}``.
``pass`` is False whenever anything is blocking.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from ai_social.storage import Paths, read_json

_HASHTAG = re.compile(r"(?<![\w/])#([\w\u0900-\u097F]+)")
_URL = re.compile(r"(https?://|www\.)\S+|\b[\w-]+\.(?:com|in|io|ai|co|org|net|me|ly)/\S*", re.I)
_NATIONAL_FIRST = re.compile(
    r"(india'?s\s+first|bharat\s+k[ia]\s+pehl[ia]|first\s+in\s+india|भारत\s+क[ीा]\s+पहल[ीा]|देश\s+क[ीा]\s+पहल[ीा])",
    re.I,
)
_FIRST_QUALIFIERS = re.compile(
    r"(one of the first|among the first|solo|single[- ]handed|akele|to (?:our|my) knowledge|as far as (?:i|we) know)",
    re.I,
)
SLOP_PHRASES: tuple[str, ...] = (
    "let's dive in", "lets dive in", "dive into", "deep dive", "delve", "game-changer", "game changer",
    "in today's fast-paced", "in today’s fast-paced", "ever-evolving", "unlock the", "unleash",
    "revolutionize", "revolutionise", "elevate your", "seamless", "leverage", "tapestry", "testament to",
    "buckle up", "here's the thing", "it's not just", "not just a", "in conclusion", "furthermore",
    "moreover", "a journey of", "landscape of",
)
BAIT_PHRASES: tuple[str, ...] = (
    "comment yes", "comment 'yes'", "type yes", "agree?", "tag someone", "tag a friend", "like if",
    "share if you agree", "follow for more",
)
SCHEMAS = {
    "draft": "draft_post.schema.json",
    "plan": "content_plan.schema.json",
    "eval": "eval_report.schema.json",
    "brief": "research_brief.schema.json",
    "diff": "playbook_diff.schema.json",
}


def _result() -> dict[str, Any]:
    return {"pass": True, "blocking": [], "warnings": []}


def _block(res: dict[str, Any], msg: str) -> None:
    res["blocking"].append(msg)
    res["pass"] = False


def schema_errors(kind: str, doc: Any, paths: Paths) -> list[str]:
    """Return human-readable schema violations for ``doc`` (empty list = valid).

    Raises:
        KeyError: If ``kind`` is not one of ``SCHEMAS``.
    """
    schema = read_json(paths.schemas / SCHEMAS[kind])
    if schema is None:
        raise FileNotFoundError(f"missing schema {SCHEMAS[kind]} in {paths.schemas}")
    validator = Draft202012Validator(schema)
    out = []
    for err in sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path)):
        where = "/".join(str(p) for p in err.absolute_path) or "(root)"
        out.append(f"{where}: {err.message}")
    return out


def _full_text(draft: dict[str, Any]) -> str:
    parts = [draft.get("text", "")]
    parts += draft.get("thread", []) or []
    parts += draft.get("slides", []) or []
    return "\n".join(p for p in parts if p)


def check_draft(draft: dict[str, Any], paths: Paths) -> dict[str, Any]:
    """Run every hard rule against one DraftPost."""
    res = _result()
    res["ready_to_publish"] = False
    for err in schema_errors("draft", draft, paths):
        _block(res, f"schema: {err}")
    if not res["pass"]:
        return res

    rules = (read_json(paths.platform_rules, {}) or {}).get("hard_constraints", {})
    platform = draft["platform"]
    limits = rules.get(platform, {})
    text = draft["text"]
    everything = _full_text(draft)

    tags = {t.lower() for t in _HASHTAG.findall(everything)} | {h.lstrip("#").lower() for h in draft["hashtags"]}
    max_tags = int(limits.get("max_hashtags", 5))
    if len(tags) > max_tags:
        _block(res, f"{len(tags)} hashtags; {platform} cap is {max_tags}")

    max_chars = int(limits.get("max_chars", 0))
    if max_chars:
        pieces = draft.get("thread") or [text]
        for i, piece in enumerate(pieces, start=1):
            if len(piece) > max_chars:
                _block(res, f"part {i} is {len(piece)} chars; {platform} limit is {max_chars}")

    if not limits.get("external_link_in_body", True) and _URL.search(everything):
        _block(res, f"external link in body; on {platform} put it in first_comment / your own reply")

    terms = read_json(paths.confidential_terms, {"terms": []}) or {"terms": []}
    public_text = everything + "\n" + draft.get("first_comment", "")
    lowered = public_text.lower()
    for term in terms.get("terms", []):
        if term.lower() in lowered:
            _block(res, f"confidential term present: {term!r} (needs STAGE comms clearance)")

    if _NATIONAL_FIRST.search(public_text) and not _FIRST_QUALIFIERS.search(public_text):
        _block(res, "unqualified 'India's first' style claim; add a qualifier or lead with 'solo, 6 dialects'")

    if draft["contains_ai_media"] and not draft["ai_label"]:
        _block(res, "AI-generated media without the platform AI label; turn the label on")

    dashes = everything.count("\u2014")
    if dashes:
        res["warnings"].append(f"{dashes} em dash(es); humanizer rule says rewrite with commas or full stops")
    for phrase in SLOP_PHRASES:
        if phrase in lowered:
            res["warnings"].append(f"AI-slop phrase: {phrase!r}")
    for phrase in BAIT_PHRASES:
        if phrase in lowered:
            res["warnings"].append(f"engagement bait: {phrase!r} (LinkedIn and Meta demote this)")

    first_line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    words = len(first_line.split())
    if words > 12:
        res["warnings"].append(f"hook line is {words} words; aim for 12 or fewer")
    res["ready_to_publish"] = res["pass"] and not draft.get("confirm") and "⟦" not in public_text
    return res


def check_plan(plan: dict[str, Any], paths: Paths) -> dict[str, Any]:
    """Validate a ContentPlan: schema, pillar mix, experiment share, slot clashes."""
    res = _result()
    for err in schema_errors("plan", plan, paths):
        _block(res, f"schema: {err}")
    if not res["pass"]:
        return res

    posts = plan["posts"]
    ids = Counter(p["post_id"] for p in posts)
    for pid, n in ids.items():
        if n > 1:
            _block(res, f"duplicate post_id {pid}")

    slots = Counter((p["platform"], p["slot_ist"][:16]) for p in posts)
    for (platform, slot), n in slots.items():
        if n > 1:
            _block(res, f"{n} posts on {platform} at {slot}")

    pillars = {p["id"]: float(p.get("target_share", 0)) for p in (read_json(paths.pillars, {}) or {}).get("pillars", [])}
    unknown = sorted({p["pillar"] for p in posts} - set(pillars))
    if pillars and unknown:
        _block(res, f"unknown pillar(s): {', '.join(unknown)}")
    if pillars and len(posts) >= 5:
        counts = Counter(p["pillar"] for p in posts)
        for pid, target in pillars.items():
            actual = counts.get(pid, 0) / len(posts)
            if abs(actual - target) > 0.15:
                res["warnings"].append(f"pillar {pid} at {actual:.0%} vs target {target:.0%}")

    experiments = sum(1 for p in posts if p["experiment_id"] != "control")
    needed = max(1, math.ceil(0.3 * len(posts))) if len(posts) >= 3 else 0
    if experiments < needed:
        _block(res, f"only {experiments} experimental post(s); need at least {needed} (30% explore budget)")
    return res


def check_file(kind: str, file: Path, paths: Paths) -> dict[str, Any]:
    """Load ``file`` as JSON and run the matching validator."""
    try:
        doc = json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        res = _result()
        _block(res, f"{file}: invalid JSON ({exc.msg} at line {exc.lineno})")
        return res
    if kind == "draft":
        return check_draft(doc, paths)
    if kind == "plan":
        return check_plan(doc, paths)
    res = _result()
    for err in schema_errors(kind, doc, paths):
        _block(res, f"schema: {err}")
    if kind == "eval" and res["pass"]:
        scores = doc["scores"]
        should_pass = all(v >= 7 for v in scores.values()) and scores["confidentiality"] == 10 and not doc["blocking_issues"]
        if doc["pass"] != should_pass:
            _block(res, f"eval 'pass'={doc['pass']} contradicts thresholds (all >=7, confidentiality 10)")
    return res
