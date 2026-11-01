"""Pull X post metrics via API v2 (pay-per-use, 2026 pricing).

  X_BEARER_TOKEN  required (app-only bearer is enough for public_metrics)
  X_USERNAME      default memanik2079

Cost: one user lookup plus one read per post returned. ``max_results=50``
weekly is roughly 51 reads, cheap at pay-per-use rates.
Matching uses the status ID in each logged post's ``url``.
"""
from __future__ import annotations

import os
import re
import urllib.parse
from datetime import datetime, timezone

from ai_social.models import MetricSnapshot, PostRecord
from ai_social.pullers.http import ApiError, HttpGet, http_get

API = "https://api.x.com/2"
_STATUS_ID = re.compile(r"/status(?:es)?/(\d+)")
RENAME = {
    "impression_count": "impressions",
    "reply_count": "replies",
    "retweet_count": "reposts",
    "quote_count": "quotes",
    "like_count": "likes",
    "bookmark_count": "bookmarks",
}


def status_id(url: str) -> str:
    """Extract the numeric status ID from an x.com / twitter.com URL ('' if none)."""
    match = _STATUS_ID.search(url or "")
    return match.group(1) if match else ""


def pull_x(posts: list[PostRecord], get: HttpGet = http_get, env: dict[str, str] | None = None, max_results: int = 50) -> list[MetricSnapshot]:
    """Fetch public metrics for logged X posts from the account's recent timeline.

    Raises:
        ApiError: If the token is missing or the user cannot be resolved.
    """
    env = dict(os.environ if env is None else env)
    token = env.get("X_BEARER_TOKEN", "")
    if not token:
        raise ApiError("X_BEARER_TOKEN is not set")
    username = env.get("X_USERNAME", "memanik2079").lstrip("@")
    wanted = {status_id(p.url): p for p in posts if p.platform == "x" and status_id(p.url)}
    if not wanted:
        return []
    headers = {"Authorization": f"Bearer {token}"}
    user = get(f"{API}/users/by/username/{urllib.parse.quote(username)}", headers)
    uid = (user.get("data") or {}).get("id")
    if not uid:
        raise ApiError(f"could not resolve X user @{username}: {user.get('errors')}")
    query = urllib.parse.urlencode({
        "max_results": str(max(5, min(max_results, 100))),
        "tweet.fields": "created_at,public_metrics",
        "exclude": "retweets",
    })
    timeline = get(f"{API}/users/{uid}/tweets?{query}", headers)
    now = datetime.now(timezone.utc).isoformat()
    snaps: list[MetricSnapshot] = []
    for tweet in timeline.get("data", []):
        post = wanted.get(str(tweet.get("id")))
        if post is None:
            continue
        pm = tweet.get("public_metrics") or {}
        metrics = {RENAME[k]: float(v) for k, v in pm.items() if k in RENAME and isinstance(v, (int, float))}
        snaps.append(MetricSnapshot(post.post_id, "x", now, metrics))
    return snaps
