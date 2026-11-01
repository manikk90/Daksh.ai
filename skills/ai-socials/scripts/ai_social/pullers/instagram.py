"""Pull Instagram post insights via the Instagram Graph API.

Needs a Professional (Creator) account and a long-lived token:
  IG_ACCESS_TOKEN   required
  IG_USER_ID        default "me"
  IG_GRAPH_BASE     default https://graph.instagram.com (Instagram Login);
                    use https://graph.facebook.com for Facebook Login tokens
  IG_GRAPH_VERSION  default v24.0 (bump when Meta deprecates it)

Logged posts are matched to media by permalink, so log each Instagram post
with its permalink in ``url``.
"""
from __future__ import annotations

import os
import urllib.parse
from datetime import datetime, timezone

from ai_social.models import MetricSnapshot, PostRecord
from ai_social.pullers.http import ApiError, HttpGet, http_get, norm_url

BASE_METRICS = ("reach", "views", "saved", "shares", "comments", "likes", "follows")
FALLBACK_METRICS = ("reach", "saved", "shares", "comments", "likes")
RENAME = {"saved": "saves"}


class Config:
    """Instagram API settings read from the environment."""

    def __init__(self, env: dict[str, str] | None = None) -> None:
        env = dict(os.environ if env is None else env)
        self.token = env.get("IG_ACCESS_TOKEN", "")
        self.user_id = env.get("IG_USER_ID", "me")
        self.base = env.get("IG_GRAPH_BASE", "https://graph.instagram.com").rstrip("/")
        self.version = env.get("IG_GRAPH_VERSION", "v24.0")
        if not self.token:
            raise ApiError("IG_ACCESS_TOKEN is not set")

    def url(self, path: str, **params: str) -> str:
        query = urllib.parse.urlencode({**params, "access_token": self.token})
        return f"{self.base}/{self.version}/{path}?{query}"


def _insights(cfg: Config, media_id: str, metrics: tuple[str, ...], get: HttpGet) -> dict[str, float]:
    data = get(cfg.url(f"{media_id}/insights", metric=",".join(metrics)), {})
    out: dict[str, float] = {}
    for item in data.get("data", []):
        name = item.get("name", "")
        values = item.get("values") or [{}]
        value = values[0].get("value", item.get("total_value", {}).get("value", 0))
        if isinstance(value, (int, float)):
            out[RENAME.get(name, name)] = float(value)
    return out


def pull_instagram(posts: list[PostRecord], get: HttpGet = http_get, env: dict[str, str] | None = None, limit: int = 50) -> list[MetricSnapshot]:
    """Fetch insights for every logged Instagram post found among recent media.

    Returns:
        One snapshot per matched post, stamped with the current UTC time.

    Raises:
        ApiError: If the token is missing or the media list call fails.
    """
    cfg = Config(env)
    wanted = {norm_url(p.url): p for p in posts if p.platform == "instagram" and p.url}
    if not wanted:
        return []
    media = get(cfg.url(f"{cfg.user_id}/media", fields="id,permalink,media_product_type,timestamp", limit=str(limit)), {})
    now = datetime.now(timezone.utc).isoformat()
    snaps: list[MetricSnapshot] = []
    for item in media.get("data", []):
        post = wanted.get(norm_url(item.get("permalink", "")))
        if post is None:
            continue
        try:
            metrics = _insights(cfg, item["id"], BASE_METRICS, get)
        except ApiError:
            metrics = _insights(cfg, item["id"], FALLBACK_METRICS, get)
        if item.get("media_product_type") == "REELS":
            try:
                watch = _insights(cfg, item["id"], ("ig_reels_avg_watch_time",), get)
                metrics["avg_watch_time_ms"] = watch.get("ig_reels_avg_watch_time", 0.0)
            except ApiError:
                pass  # watch time is a bonus signal; scoring does not depend on it
        snaps.append(MetricSnapshot(post.post_id, "instagram", now, metrics))
    return snaps
