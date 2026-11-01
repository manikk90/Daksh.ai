"""Scoring: turn raw platform metrics into one comparable number per post.

The north-star formulas are fixed in code on purpose. If the agent could edit
its own scoring it would learn to game the metric (Goodhart), so only a human
changes ``NORTH_STAR`` and the change shows up in git.

Every post is scored at roughly the same age (first snapshot at least
``MATURE_DAYS`` after publishing), then divided by the median of the same
platform's previous 8 weeks. That ratio, ``normalized``, is what the bandit and
retro learn from: 1.0 = typical post, 1.4 = 40% better than typical.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass
from datetime import timedelta
from typing import Callable, Iterable

from ai_social.models import MetricSnapshot, PostRecord, parse_ts
from ai_social.storage import Paths, append_jsonl, iter_jsonl

MATURE_DAYS = 7
BASELINE_WINDOW_DAYS = 56
MIN_BASELINE_POSTS = 3


def _g(m: dict[str, float], key: str) -> float:
    return float(m.get(key, 0.0))


def _per_k(numerator: float, denominator: float) -> float | None:
    return None if denominator <= 0 else 1000.0 * numerator / denominator


NORTH_STAR: dict[str, Callable[[dict[str, float]], float | None]] = {
    # Saves + sends are LinkedIn's strongest distribution signals in 2026.
    "linkedin": lambda m: _per_k(
        2 * _g(m, "saves") + 2 * _g(m, "sends") + _g(m, "comments") + _g(m, "reposts") + 0.2 * _g(m, "reactions"),
        _g(m, "impressions"),
    ),
    # Sends (shares) drive non-follower reach on Instagram; follows prove the profile converted.
    "instagram": lambda m: _per_k(
        2 * _g(m, "shares") + 1.5 * _g(m, "saves") + _g(m, "comments") + 2 * _g(m, "follows") + 0.2 * _g(m, "likes"),
        _g(m, "reach"),
    ),
    "facebook": lambda m: _per_k(
        2 * _g(m, "shares") + _g(m, "comments") + 0.2 * _g(m, "reactions"),
        _g(m, "reach"),
    ),
    # Replies and quotes carry the heaviest weights in X's open-sourced ranker.
    "x": lambda m: _per_k(
        2 * _g(m, "replies") + 2 * _g(m, "quotes") + _g(m, "reposts") + _g(m, "bookmarks")
        + 0.5 * _g(m, "profile_clicks") + 0.2 * _g(m, "likes"),
        _g(m, "impressions"),
    ),
}


@dataclass(frozen=True)
class ScoredPost:
    """A post with its raw north-star score and its baseline-relative score."""

    post: PostRecord
    raw: float
    normalized: float | None
    baseline_n: int


def load_posts(paths: Paths) -> list[PostRecord]:
    """Load every logged post; later rows with the same post_id win."""
    latest: dict[str, PostRecord] = {}
    for row in iter_jsonl(paths.posts_log):
        rec = PostRecord.from_dict(row)
        latest[rec.post_id] = rec
    return sorted(latest.values(), key=lambda p: p.published_dt)


def load_snapshots(paths: Paths) -> list[MetricSnapshot]:
    """Load every metric snapshot."""
    return [MetricSnapshot.from_dict(r) for r in iter_jsonl(paths.metrics_log)]


def log_post(paths: Paths, post: PostRecord) -> None:
    """Append a post to ``logs/posts.jsonl``."""
    append_jsonl(paths.posts_log, [post.to_dict()])


def log_metrics(paths: Paths, snaps: Iterable[MetricSnapshot]) -> int:
    """Append metric snapshots to ``logs/metrics.jsonl``."""
    return append_jsonl(paths.metrics_log, (s.to_dict() for s in snaps))


def mature_snapshot(post: PostRecord, snaps: list[MetricSnapshot], min_age_days: int = MATURE_DAYS) -> MetricSnapshot | None:
    """Earliest snapshot taken at least ``min_age_days`` after publishing.

    Using the earliest mature snapshot (not the latest) keeps old posts from
    looking better just because they have had more time to collect views.
    """
    cutoff = post.published_dt + timedelta(days=min_age_days)
    mature = [s for s in snaps if s.post_id == post.post_id and parse_ts(s.captured_at) >= cutoff]
    return min(mature, key=lambda s: parse_ts(s.captured_at)) if mature else None


def raw_score(post: PostRecord, snap: MetricSnapshot) -> float | None:
    """North-star score for one post, or None if the denominator is missing."""
    return NORTH_STAR[post.platform](snap.metrics)


def score_posts(posts: list[PostRecord], snaps: list[MetricSnapshot], min_age_days: int = MATURE_DAYS) -> list[ScoredPost]:
    """Score every mature post and normalise against its platform's recent median.

    Baseline: median raw score of same-platform posts published in the
    previous ``BASELINE_WINDOW_DAYS``. With fewer than ``MIN_BASELINE_POSTS`` in
    that window (cold start), fall back to the median of all other scored posts
    on the platform; with fewer than 2 of those, ``normalized`` stays None.
    """
    raw: list[tuple[PostRecord, float]] = []
    for post in posts:
        snap = mature_snapshot(post, snaps, min_age_days)
        if snap is None:
            continue
        val = raw_score(post, snap)
        if val is not None:
            raw.append((post, val))

    scored: list[ScoredPost] = []
    for post, val in raw:
        window_start = post.published_dt - timedelta(days=BASELINE_WINDOW_DAYS)
        window = [
            v for p, v in raw
            if p.platform == post.platform and window_start <= p.published_dt < post.published_dt
        ]
        if len(window) < MIN_BASELINE_POSTS:
            window = [v for p, v in raw if p.platform == post.platform and p.post_id != post.post_id]
        if len(window) < 2:
            scored.append(ScoredPost(post, val, None, len(window)))
            continue
        base = statistics.median(window)
        norm = val / base if base > 0 else None
        scored.append(ScoredPost(post, val, norm, len(window)))
    return scored
