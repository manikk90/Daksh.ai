"""Builders for synthetic posts and metrics used across tests."""
from __future__ import annotations

from datetime import date, datetime, timedelta

from ai_social.models import IST, MetricSnapshot, PostRecord


def li_post(pid: str, when: datetime, **kw) -> PostRecord:
    base = dict(post_id=pid, platform="linkedin", published_at=when.isoformat(), pillar="pipeline",
                format="carousel", hook_type="constraint_number", language="en", experiment_id="exp-li-slot-0800-vs-1030")
    base.update(kw)
    return PostRecord(**base)


def snap(post: PostRecord, days: int, **metrics: float) -> MetricSnapshot:
    return MetricSnapshot(post.post_id, post.platform, (post.published_dt + timedelta(days=days)).isoformat(), metrics)


def slot_experiment(weeks: int = 6, start: date = date(2026, 8, 4)):
    """LinkedIn: Wed 08:00 posts get 3x the saves of Tue 10:30 posts."""
    posts, snaps = [], []
    for k in range(weeks):
        tue = datetime.combine(start + timedelta(days=7 * k), datetime.min.time()).replace(hour=10, minute=30, tzinfo=IST)
        wed = (tue + timedelta(days=1)).replace(hour=8, minute=0)
        p_tue, p_wed = li_post(f"tue-{k}", tue), li_post(f"wed-{k}", wed)
        posts += [p_tue, p_wed]
        snaps += [snap(p_tue, 8, impressions=1000, saves=10), snap(p_wed, 8, impressions=1000, saves=30)]
    return posts, snaps
