"""Import post metrics from CSV for platforms without a usable API.

Personal Facebook profiles have no insights API (Professional Mode stats are
dashboard-only), and LinkedIn member analytics need an approved partner app.
So for those two, Manik exports a CSV (Professional Dashboard, LinkedIn post
analytics, Metricool, Buffer) and this module maps whatever column names it
finds onto the canonical metric keys used by ``metrics.NORTH_STAR``.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from ai_social.models import MetricSnapshot, PostRecord
from ai_social.pullers.http import norm_url

ALIASES: dict[str, tuple[str, ...]] = {
    "impressions": ("impressions", "views", "post impressions"),
    "reach": ("reach", "members reached", "accounts reached", "post reach", "unique impressions"),
    "views_3s": ("3-second views", "3 second views", "video views"),
    "reactions": ("reactions", "likes", "post reactions"),
    "comments": ("comments",),
    "reposts": ("reposts",),
    "shares": ("shares",),
    "saves": ("saves", "saved"),
    "sends": ("sends", "sends on linkedin"),
    "profile_views": ("profile viewers from this post", "profile views", "profile visits"),
    "followers_gained": ("followers gained", "follows", "new followers"),
}
URL_COLS = ("post url", "url", "permalink", "post link", "link")
ID_COLS = ("post_id", "post id")


class ImportReport:
    """What happened during an import (matched snapshots and skipped rows)."""

    def __init__(self) -> None:
        self.snapshots: list[MetricSnapshot] = []
        self.unmatched: list[str] = []
        self.bad_rows: list[str] = []


def _number(raw: str) -> float | None:
    cleaned = (raw or "").replace(",", "").replace("%", "").strip()
    if not cleaned or cleaned in ("-", "--"):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def import_metrics_csv(path: Path, platform: str, posts: list[PostRecord], captured_at: str | None = None) -> ImportReport:
    """Map a metrics CSV onto logged posts.

    Rows are matched by a ``post_id`` column if present, otherwise by URL.
    On LinkedIn, ``shares`` columns are stored as ``reposts`` because that is
    what LinkedIn calls a share.

    Args:
        path: CSV file.
        platform: ``linkedin`` or ``facebook`` (any platform works).
        posts: Logged posts to match against.
        captured_at: ISO time the numbers were read; defaults to now (UTC).
    """
    report = ImportReport()
    stamp = captured_at or datetime.now(timezone.utc).isoformat()
    by_id = {p.post_id: p for p in posts if p.platform == platform}
    by_url = {norm_url(p.url): p for p in posts if p.platform == platform and p.url}

    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        header = {(h or "").strip().lower(): h for h in (reader.fieldnames or [])}
        for lineno, row in enumerate(reader, start=2):
            low = {k: row.get(orig, "") for k, orig in header.items()}
            post = next((by_id[low[c].strip()] for c in ID_COLS if low.get(c, "").strip() in by_id), None)
            if post is None:
                url = next((low[c] for c in URL_COLS if low.get(c)), "")
                post = by_url.get(norm_url(url)) if url else None
                if post is None:
                    report.unmatched.append(f"line {lineno}: {url or '(no url/post_id)'}")
                    continue
            metrics: dict[str, float] = {}
            for key, names in ALIASES.items():
                for name in names:
                    value = _number(low.get(name, ""))
                    if value is not None:
                        target = "reposts" if (platform == "linkedin" and key == "shares") else key
                        metrics[target] = value
                        break
            if not metrics:
                report.bad_rows.append(f"line {lineno}: no recognised metric columns")
                continue
            report.snapshots.append(MetricSnapshot(post.post_id, platform, stamp, metrics))
    return report
