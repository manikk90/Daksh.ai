"""Parse the LinkedIn "Get a copy of your data" archive.

Files used (names as LinkedIn ships them; matching is case-insensitive):
  Reactions.csv  Date, Type, Link           -> posts Manik reacted to
  Comments.csv   Date, Link, Message        -> Manik's comments
  Shares.csv     Date, ShareLink, ShareCommentary, SharedUrl, MediaUrl, Visibility
                                            -> Manik's own posts

The archive does not include reactions other people left on Manik's posts,
so performance comes from analytics (metrics.py), not from here.
"""
from __future__ import annotations

import csv
import io
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from ai_social.models import EngagementEvent

# linkedin.com/posts/<author>_<slug-words>-activity-<id>-<hash>
_POST_URL = re.compile(r"linkedin\.com/posts/([^_/]+)_(.+?)-(?:activity|ugcPost|share)-\d+", re.I)


def _find_file(folder: Path, name: str) -> Path | None:
    target = name.lower()
    for path in folder.rglob("*.csv"):
        if path.name.lower() == target:
            return path
    return None


def _read_rows(path: Path, required: str) -> list[dict[str, str]]:
    """Read a LinkedIn CSV, skipping any "Notes:" preamble before the header row."""
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    lines = text.splitlines(keepends=True)
    start = 0
    for i, line in enumerate(lines):
        if required.lower() in line.lower() and "," in line:
            start = i
            break
    reader = csv.DictReader(io.StringIO("".join(lines[start:])))
    rows: list[dict[str, str]] = []
    for row in reader:
        rows.append({(k or "").strip().lower(): (v or "").strip() for k, v in row.items()})
    return rows


def _iso(date_str: str) -> str | None:
    """LinkedIn writes UTC as ``YYYY-MM-DD HH:MM:SS`` (sometimes without seconds)."""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%m/%d/%y, %I:%M %p", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            continue
    return None


def author_and_slug(url: str) -> tuple[str, str]:
    """Pull the author handle and slug words out of a LinkedIn post URL.

    Liked posts arrive as bare URLs, and the slug is the only text signal we
    have about what Manik engaged with, so it matters for the liking profile.

    Returns:
        ``(author, slug_text)``; both empty when the URL has no slug.
    """
    match = _POST_URL.search(url or "")
    if not match:
        return "", ""
    return match.group(1).lower(), match.group(2).replace("-", " ")


def parse_linkedin_export(folder: Path) -> Iterator[EngagementEvent]:
    """Yield engagement events from an unzipped LinkedIn archive folder.

    Missing files are skipped, so a partial archive still works.
    """
    reactions = _find_file(folder, "Reactions.csv")
    if reactions:
        for row in _read_rows(reactions, "link"):
            author, slug = author_and_slug(row.get("link", ""))
            yield EngagementEvent(
                platform="linkedin",
                kind="reaction",
                timestamp=_iso(row.get("date", "")),
                text=slug,
                target_url=row.get("link", ""),
                target_author=author,
                source_file=reactions.name,
            )

    comments = _find_file(folder, "Comments.csv")
    if comments:
        for row in _read_rows(comments, "message"):
            author, _ = author_and_slug(row.get("link", ""))
            yield EngagementEvent(
                platform="linkedin",
                kind="comment",
                timestamp=_iso(row.get("date", "")),
                text=row.get("message", ""),
                target_url=row.get("link", ""),
                target_author=author,
                source_file=comments.name,
            )

    shares = _find_file(folder, "Shares.csv")
    if shares:
        for row in _read_rows(shares, "sharelink"):
            yield EngagementEvent(
                platform="linkedin",
                kind="post",
                timestamp=_iso(row.get("date", "")),
                text=row.get("sharecommentary", ""),
                target_url=row.get("sharelink", ""),
                target_author="self",
                source_file=shares.name,
            )
