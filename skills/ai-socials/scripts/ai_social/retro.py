"""The weekly self-update loop's maths.

Sunday flow:
  1. score every mature post (metrics.score_posts)
  2. group by platform x dimension x value, bootstrap a CI on the mean
  3. propose at most ``MAX_CHANGES`` rule changes that clear the evidence gate
  4. a fresh Evaluator agent audits the diff against the logs
  5. Manik approves -> ``apply_diff`` bumps the playbook version (git commit)

Nothing here writes to the brain without ``approve=True``. Rules carry their
evidence post IDs so the Evaluator (and Manik) can check every claim.
"""
from __future__ import annotations

import math
import random
import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Sequence

from ai_social.metrics import ScoredPost
from ai_social.models import LEARNABLE_DIMENSIONS

MIN_N = 4
MIN_LIFT = 0.20
MAX_CHANGES = 3
STALE_DAYS = 42      # 6-week half-life: flag for re-confirmation
EXPIRE_DAYS = 84     # two half-lives unconfirmed: propose retirement
BOOTSTRAP_ROUNDS = 2000
CI_LEVEL = 0.90


@dataclass(frozen=True)
class GroupStat:
    """Evidence for one platform x dimension x value group, against the rest.

    ``ratio`` compares this value's mean normalised score with the mean of the
    other values of the same dimension on the same platform. Comparing against
    "the rest" (not against 1.0) means a dimension where every post shares one
    value (e.g. all carousels) produces no rule: there is nothing to contrast.
    """

    platform: str
    dimension: str
    value: str
    n: int
    n_rest: int
    mean: float
    ratio: float
    ci_low: float
    ci_high: float
    post_ids: tuple[str, ...]

    @property
    def lift_pct(self) -> float:
        return round((self.ratio - 1.0) * 100, 1)

    @property
    def strength(self) -> float:
        return abs(self.ratio - 1.0) * math.sqrt(min(self.n, self.n_rest))


def iso_week(d: date) -> str:
    """ISO week label like ``2026-W43``."""
    year, week, _ = d.isocalendar()
    return f"{year}-W{week:02d}"


def bootstrap_ci(values: Sequence[float], seed: int = 7, rounds: int = BOOTSTRAP_ROUNDS) -> tuple[float, float]:
    """Percentile bootstrap CI for the mean (deterministic for a given seed)."""
    if not values:
        raise ValueError("bootstrap_ci needs at least one value")
    if len(values) == 1:
        return values[0], values[0]
    rng = random.Random(seed)
    means = sorted(statistics.fmean(rng.choices(values, k=len(values))) for _ in range(rounds))
    tail = (1 - CI_LEVEL) / 2
    return means[int(tail * rounds)], means[min(rounds - 1, int((1 - tail) * rounds))]


def bootstrap_ratio_ci(group: Sequence[float], rest: Sequence[float], seed: int = 7, rounds: int = BOOTSTRAP_ROUNDS) -> tuple[float, float]:
    """Percentile bootstrap CI for mean(group) / mean(rest), resampling both sides."""
    if not group or not rest:
        raise ValueError("bootstrap_ratio_ci needs values on both sides")
    rng = random.Random(seed)
    ratios: list[float] = []
    for _ in range(rounds):
        g = statistics.fmean(rng.choices(group, k=len(group)))
        r = statistics.fmean(rng.choices(rest, k=len(rest)))
        ratios.append(g / r if r > 0 else math.inf)
    ratios.sort()
    tail = (1 - CI_LEVEL) / 2
    return ratios[int(tail * rounds)], ratios[min(rounds - 1, int((1 - tail) * rounds))]


def group_stats(scored: Sequence[ScoredPost]) -> list[GroupStat]:
    """Contrast every platform x dimension x value against the other values of that dimension."""
    buckets: dict[tuple[str, str], dict[str, list[ScoredPost]]] = defaultdict(lambda: defaultdict(list))
    for sp in scored:
        if sp.normalized is None:
            continue
        for dim in LEARNABLE_DIMENSIONS:
            buckets[(sp.post.platform, dim)][sp.post.dimension(dim)].append(sp)
    out: list[GroupStat] = []
    for (platform, dim), by_value in sorted(buckets.items()):
        if len(by_value) < 2:
            continue
        for value, items in sorted(by_value.items()):
            group = [i.normalized for i in items if i.normalized is not None]
            rest = [i.normalized for v, its in by_value.items() if v != value for i in its if i.normalized is not None]
            rest_mean = statistics.fmean(rest)
            if rest_mean <= 0:
                continue
            low, high = bootstrap_ratio_ci(group, rest)
            out.append(GroupStat(
                platform, dim, value, len(group), len(rest), statistics.fmean(group),
                statistics.fmean(group) / rest_mean, low, high, tuple(i.post.post_id for i in items),
            ))
    return out


def _rule_id(platform: str, dimension: str, value: str) -> str:
    return f"{platform}:{dimension}:{value}"


def propose_diff(
    scored: Sequence[ScoredPost],
    rules_doc: dict[str, Any],
    today: date | None = None,
) -> dict[str, Any]:
    """Build the week's PlaybookDiff (see schemas/playbook_diff.schema.json).

    Gate for a new or modified rule: n >= MIN_N on both sides of the contrast,
    |lift vs the other values| >= MIN_LIFT, and the 90% CI of the ratio excludes 1.0. Existing rules contradicted by the data,
    or unconfirmed for EXPIRE_DAYS, are proposed for retirement. Confirmations
    refresh ``last_confirmed`` and do not count towards MAX_CHANGES.
    """
    today = today or datetime.now(timezone.utc).date()
    stats = {(_rule_id(s.platform, s.dimension, s.value)): s for s in group_stats(scored)}
    existing = {r["id"]: r for r in rules_doc.get("rules", [])}

    candidates: list[dict[str, Any]] = []
    confirmations: list[dict[str, Any]] = []
    stale: list[str] = []

    for rid, s in stats.items():
        if s.n < MIN_N or s.n_rest < MIN_N:
            continue
        prefer = s.ratio >= 1 + MIN_LIFT and s.ci_low > 1.0
        avoid = s.ratio <= 1 - MIN_LIFT and s.ci_high < 1.0
        current = existing.get(rid)
        evidence = {
            "evidence_post_ids": list(s.post_ids), "n": s.n, "n_rest": s.n_rest, "lift_vs_rest_pct": s.lift_pct,
            "ci90": [round(s.ci_low, 3), round(s.ci_high, 3)], "ci_excludes_parity": prefer or avoid,
        }
        if current and ((current["direction"] == "prefer" and prefer) or (current["direction"] == "avoid" and avoid)):
            confirmations.append({"rule_id": rid, **evidence})
        elif current and (
            (current["direction"] == "prefer" and s.ci_high < 1.0)
            or (current["direction"] == "avoid" and s.ci_low > 1.0)
        ):
            candidates.append({"action": "retire", "rule_id": rid, "platform": s.platform, "dimension": s.dimension,
                               "value": s.value, "direction": current["direction"],
                               "reason": "data contradicts rule", "strength": s.strength, **evidence})
        elif prefer or avoid:
            direction = "prefer" if prefer else "avoid"
            action = "modify" if current else "add"
            candidates.append({"action": action, "rule_id": rid, "platform": s.platform, "dimension": s.dimension,
                               "value": s.value, "direction": direction,
                               "reason": f"{s.lift_pct:+.0f}% vs other {s.dimension} values ({s.n} vs {s.n_rest} posts)", "strength": s.strength,
                               **evidence})

    confirmed_ids = {c["rule_id"] for c in confirmations}
    for rid, rule in existing.items():
        if rid in confirmed_ids:
            continue
        last = date.fromisoformat(rule.get("last_confirmed", today.isoformat()))
        age = (today - last).days
        if age >= EXPIRE_DAYS and not any(c["rule_id"] == rid for c in candidates):
            candidates.append({"action": "retire", "rule_id": rid, "platform": rule["platform"],
                               "dimension": rule["dimension"], "value": rule["value"],
                               "direction": rule["direction"], "reason": f"unconfirmed for {age} days",
                               "strength": 0.0, "evidence_post_ids": [], "n": 0, "n_rest": 0,
                               "lift_vs_rest_pct": None, "ci90": None, "ci_excludes_parity": False})
        elif age >= STALE_DAYS:
            stale.append(rid)

    candidates.sort(key=lambda c: c["strength"], reverse=True)
    chosen = candidates[:MAX_CHANGES]
    for c in chosen:
        c.pop("strength", None)
    deferred = [c["rule_id"] for c in candidates[MAX_CHANGES:]]

    version = int(rules_doc.get("version", 1))
    scored_n = sum(1 for s in scored if s.normalized is not None)
    return {
        "week": iso_week(today),
        "generated_on": today.isoformat(),
        "version_from": version,
        "version_to": version + 1 if chosen or confirmations else version,
        "scored_posts": scored_n,
        "changes": chosen,
        "confirmations": confirmations,
        "stale_rules": sorted(stale),
        "deferred_changes": deferred,
        "guards": {
            "max_changes": MAX_CHANGES,
            "changes_within_cap": len(chosen) <= MAX_CHANGES,
            "only_learnable_dimensions": all(c["dimension"] in LEARNABLE_DIMENSIONS for c in chosen),
            "voice_anchor_untouched": True,
        },
    }


class DiffRejected(ValueError):
    """Raised when a PlaybookDiff fails a guard or was not approved."""


def apply_diff(rules_doc: dict[str, Any], diff: dict[str, Any], approve: bool, today: date | None = None) -> dict[str, Any]:
    """Return a new rules document with ``diff`` applied.

    Raises:
        DiffRejected: Without approval, on a version mismatch, or when a guard fails.
    """
    if not approve:
        raise DiffRejected("refusing to change the playbook without --approve")
    current = int(rules_doc.get("version", 1))
    if int(diff.get("version_from", -1)) != current:
        raise DiffRejected(f"diff was built against v{diff.get('version_from')} but playbook is v{current}; re-run retro")
    changes = diff.get("changes", [])
    if len(changes) > MAX_CHANGES:
        raise DiffRejected(f"{len(changes)} changes exceeds cap of {MAX_CHANGES}")
    for c in changes:
        if c.get("dimension") not in LEARNABLE_DIMENSIONS:
            raise DiffRejected(f"dimension {c.get('dimension')!r} is a hard rule, not learnable")

    today = today or datetime.now(timezone.utc).date()
    rules = {r["id"]: dict(r) for r in rules_doc.get("rules", [])}
    new_version = current + 1 if (changes or diff.get("confirmations")) else current

    for conf in diff.get("confirmations", []):
        if conf["rule_id"] in rules:
            rules[conf["rule_id"]]["last_confirmed"] = today.isoformat()
            rules[conf["rule_id"]]["n"] = conf["n"]
            rules[conf["rule_id"]]["lift_pct"] = conf["lift_vs_rest_pct"]

    for c in changes:
        rid = c["rule_id"]
        if c["action"] == "retire":
            rules.pop(rid, None)
            continue
        rules[rid] = {
            "id": rid, "platform": c["platform"], "dimension": c["dimension"], "value": c["value"],
            "direction": c["direction"], "origin": "learned", "evidence_post_ids": c["evidence_post_ids"],
            "n": c["n"], "lift_pct": c["lift_vs_rest_pct"], "added_in": new_version,
            "last_confirmed": today.isoformat(), "note": c["reason"],
        }

    summary = "; ".join(f"{c['action']} {c['rule_id']}" for c in changes) or "confirmations only"
    changelog = list(rules_doc.get("changelog", []))
    if new_version != current:
        changelog.append({"version": new_version, "date": today.isoformat(), "week": diff.get("week"), "summary": summary})
    return {
        "version": new_version,
        "updated_at": today.isoformat(),
        "rules": sorted(rules.values(), key=lambda r: r["id"]),
        "changelog": changelog,
    }


def render_report(diff: dict[str, Any], stats: Sequence[GroupStat]) -> str:
    """Markdown retro report for Manik (the Evaluator reads the JSON, not this)."""
    lines = [
        f"# AI Social retro {diff['week']}",
        "",
        f"Scored posts: {diff['scored_posts']}. Playbook v{diff['version_from']} -> v{diff['version_to']} if approved.",
        "",
        "## Proposed changes",
    ]
    if not diff["changes"]:
        lines.append("Koi change nahi. Abhi data itna strong nahi hai ki rule badla jaye.")
    for c in diff["changes"]:
        lift = "n/a" if c["lift_vs_rest_pct"] is None else f"{c['lift_vs_rest_pct']:+.0f}%"
        lines.append(f"- **{c['action']}** `{c['rule_id']}` ({c['direction']}): {c['reason']}. n={c['n']}, lift {lift}, CI90 {c['ci90']}")
    if diff["confirmations"]:
        lines += ["", "## Confirmed (still true)"]
        lines += [f"- `{c['rule_id']}`: {c['lift_vs_rest_pct']:+.0f}% over {c['n']} posts" for c in diff["confirmations"]]
    if diff["stale_rules"]:
        lines += ["", "## Stale (needs a fresh test)"] + [f"- `{r}`" for r in diff["stale_rules"]]
    if diff["deferred_changes"]:
        lines += ["", "## Deferred (over the 3-change cap)"] + [f"- `{r}`" for r in diff["deferred_changes"]]
    top = sorted((s for s in stats if s.n >= 2), key=lambda s: s.ratio, reverse=True)[:8]
    if top:
        lines += ["", "## Top groups this cycle", "", "| platform | dimension | value | n | vs rest of dimension |", "|---|---|---|---|---|"]
        lines += [f"| {s.platform} | {s.dimension} | {s.value} | {s.n} | {s.ratio:.2f}x |" for s in top]
    lines += ["", "Approve: `ai-social apply-diff retro/" + diff["week"] + ".diff.json --approve`"]
    return "\n".join(lines) + "\n"
