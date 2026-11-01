"""Parse Meta "Download your information" JSON exports (Instagram + Facebook).

Meta has shipped at least two layouts since 2024 (``string_list_data`` /
``string_map_data`` records, and a newer ``label_values`` layout), and file
names drift. So instead of hard-coding one schema, this module:

1. classifies each JSON file by its path (likes, comments, saved, posts),
2. finds the list of records inside it,
3. pulls timestamp / URL / author / text out of each record with tolerant
   lookups that cover both layouts.

Meta also double-encodes non-ASCII text (UTF-8 bytes stored as latin-1 code
points), which turns Hindi into garbage like ``Ã Â¤``. ``fix_mojibake`` repairs
that, which matters a lot for Hinglish and Devanagari comments.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from ai_social.models import EngagementEvent

_FB_TITLE_TARGET = re.compile(r"(?:liked|reacted to|commented on|replied to)\s+(.+?)'s\b", re.I)


def fix_mojibake(text: str) -> str:
    """Undo Meta's latin-1/UTF-8 double encoding; leave clean text untouched."""
    if not text:
        return text
    try:
        repaired = text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text
    return repaired


def _classify(path: Path) -> tuple[str | None, str | None]:
    """Return ``(platform, kind)`` for a file, or ``(None, None)`` to skip it."""
    p = path.as_posix().lower()
    platform: str | None = None
    if "instagram" in p:
        platform = "instagram"
    elif "facebook" in p:
        platform = "facebook"

    name = path.name.lower()
    if "follow" in p or "ads" in name or "message" in p:
        return platform, None
    if "likes_and_reactions" in name or "reactions" in name:
        return platform or "facebook", "reaction"
    if "liked" in name or "/likes/" in p:
        return platform or "instagram", "like"
    if "comment" in name:
        return platform, "comment"
    if "saved" in name:
        return platform, "save"
    if name.startswith("posts_") or "your_posts" in name or name.startswith("reels"):
        return platform, "post"
    return platform, None


def _records(payload: Any) -> list[Any]:
    """Find the list of records in a payload (top-level list or first list value)."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for value in payload.values():
            if isinstance(value, list):
                return value
    return []


def _walk(obj: Any) -> Iterator[tuple[str, Any]]:
    """Depth-first ``(key, value)`` pairs over nested dicts and lists."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield key, value
            yield from _walk(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk(item)


def _dicts(obj: Any) -> Iterator[dict[str, Any]]:
    """Every dict nested anywhere inside ``obj`` (including list items)."""
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from _dicts(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _dicts(item)


def _first_int(record: Any, keys: tuple[str, ...]) -> int | None:
    for key, value in _walk(record):
        if key in keys and isinstance(value, (int, float)) and value > 0:
            return int(value)
    return None


def _first_str(record: Any, keys: tuple[str, ...]) -> str:
    for key, value in _walk(record):
        if key in keys and isinstance(value, str) and value.strip():
            return value
    return ""


def _label_value(record: Any, label: str) -> str:
    """Read ``{"label": <label>, "value": ...}`` pairs from the newer layout."""
    for value in _dicts(record):
        if str(value.get("label", "")).lower() == label.lower():
            found = value.get("value") or value.get("href") or ""
            if isinstance(found, str) and found.strip():
                return found
    return ""


def _map_value(record: Any, field: str) -> str:
    """Read ``string_map_data[field].value`` from the older layout."""
    smd = record.get("string_map_data") if isinstance(record, dict) else None
    if isinstance(smd, dict):
        entry = smd.get(field)
        if isinstance(entry, dict):
            return str(entry.get("value") or entry.get("href") or "")
    return ""


def _iso(ts: int | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _extract(record: Any, platform: str, kind: str, source: str) -> EngagementEvent | None:
    if not isinstance(record, dict):
        return None
    ts = _first_int(record, ("timestamp", "creation_timestamp"))
    url = _first_str(record, ("href", "uri")) or _label_value(record, "URL")
    title = str(record.get("title") or "")

    author = (
        _map_value(record, "Media Owner")
        or _label_value(record, "Username")
        or _first_str(record, ("author",))
    )
    if not author and platform == "instagram" and kind in ("like", "save") and title and " " not in title:
        author = title
    if not author and platform == "facebook":
        match = _FB_TITLE_TARGET.search(fix_mojibake(title))
        author = match.group(1) if match else ""
    if kind == "comment" and author.strip().lower() in ("", "mohit kumar", "manik prajapati"):
        match = _FB_TITLE_TARGET.search(fix_mojibake(title))
        author = match.group(1) if match else author

    text = (
        _map_value(record, "Comment")
        or _first_str(record, ("comment", "post"))
        or _label_value(record, "Caption")
    )
    if not text and kind == "post":
        text = title or _first_str(record, ("title",))

    if ts is None and not url and not text:
        return None
    return EngagementEvent(
        platform=platform,
        kind=kind,
        timestamp=_iso(ts),
        text=fix_mojibake(text),
        target_url=url,
        target_author=fix_mojibake(author).strip(),
        source_file=source,
    )


def parse_meta_export(folder: Path, default_platform: str = "instagram") -> Iterator[EngagementEvent]:
    """Yield engagement events from an unzipped Meta JSON export.

    Args:
        folder: Root of the unzipped export (Instagram, Facebook, or both).
        default_platform: Used when the path does not say which app a file is from.

    Raises:
        ValueError: If a classified file contains invalid JSON (with the file name).
    """
    for path in sorted(folder.rglob("*.json")):
        platform, kind = _classify(path.relative_to(folder))
        if kind is None:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}: invalid JSON in Meta export ({exc.msg})") from exc
        for record in _records(payload):
            event = _extract(record, platform or default_platform, kind, path.name)
            if event is not None:
                yield event
