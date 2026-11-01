"""Parse the X "Download an archive of your data" export.

Files used:
  data/tweets.js   window.YTD.tweets.part0 = [{"tweet": {...}}]
  data/like.js     window.YTD.like.part0   = [{"like": {"tweetId", "fullText", "expandedUrl"}}]

Likes carry no timestamp in the archive, so they feed topic and author
signals only, never the activity-by-hour histogram.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from ai_social.models import EngagementEvent

_PREFIX = re.compile(r"^\s*window\.YTD\.[\w.]+\s*=\s*", re.S)
_STATUS_URL = re.compile(r"(?:twitter|x)\.com/([A-Za-z0-9_]{1,15})/status/", re.I)


def load_ytd(path: Path) -> list[Any]:
    """Strip the ``window.YTD...=`` wrapper and parse the JSON array.

    Raises:
        ValueError: If the file is not a YTD-wrapped JSON array.
    """
    raw = path.read_text(encoding="utf-8")
    body = _PREFIX.sub("", raw, count=1).rstrip().rstrip(";")
    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: not a valid X archive file ({exc.msg})") from exc
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a JSON array")
    return data


def _tweet_time(created_at: str) -> str | None:
    try:
        return datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y").isoformat()
    except (TypeError, ValueError):
        return None


def _find(folder: Path, name: str) -> Path | None:
    for path in folder.rglob(name):
        return path
    return None


def parse_x_archive(folder: Path) -> Iterator[EngagementEvent]:
    """Yield engagement events from an unzipped X archive folder."""
    tweets = _find(folder, "tweets.js") or _find(folder, "tweet.js")
    if tweets:
        for item in load_ytd(tweets):
            tweet = item.get("tweet", item) if isinstance(item, dict) else {}
            text = str(tweet.get("full_text") or tweet.get("text") or "")
            is_reply = bool(tweet.get("in_reply_to_status_id_str"))
            is_retweet = text.startswith("RT @")
            yield EngagementEvent(
                platform="x",
                kind="share" if is_retweet else ("comment" if is_reply else "post"),
                timestamp=_tweet_time(str(tweet.get("created_at", ""))),
                text=text,
                target_url=f"https://x.com/i/status/{tweet.get('id_str', '')}",
                target_author=str(tweet.get("in_reply_to_screen_name") or "self"),
                source_file=tweets.name,
            )

    likes = _find(folder, "like.js")
    if likes:
        for item in load_ytd(likes):
            like = item.get("like", {}) if isinstance(item, dict) else {}
            url = str(like.get("expandedUrl") or "")
            match = _STATUS_URL.search(url)
            yield EngagementEvent(
                platform="x",
                kind="like",
                timestamp=None,
                text=str(like.get("fullText") or ""),
                target_url=url,
                target_author=match.group(1).lower() if match and match.group(1) != "i" else "",
                source_file=likes.name,
            )
