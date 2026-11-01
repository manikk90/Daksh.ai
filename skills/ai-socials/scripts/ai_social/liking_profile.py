"""Build ``brain/liking_profile.json`` from ingested engagement events.

This is the "what does Manik actually engage with" half of the brain. It is
deliberately simple and deterministic (counts, not embeddings) so the weekly
loop can diff it and a human can read it. Designed to be deleted: once the
export volume is large, swap the keyword counting for LLM topic clustering.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable

from ai_social.lang import detect_language
from ai_social.models import IST, EngagementEvent, parse_ts

_WORD = re.compile(r"[a-z][a-z0-9+#]{2,}|[\u0900-\u097F]{2,}")

STOPWORDS: frozenset[str] = frozenset(
    """
    the and for with that this from your you are was were have has had not but our out all
    can will just about into what when where who how why than then them they their there
    here its it's also more most very much some any one two new get got make made like
    http https www com linkedin instagram facebook twitter amp via day days time year years
    post posts share shared sharing today week thanks thank congratulations congrats great
    good best really amazing awesome love nice well done proud happy excited
    hai hain kya nahi bhai yaar mein aur toh bhi sab kuch bahut abhi phir kar karo raha rahi
    wala wali wale yeh woh unka uska iska apna apni hum tum aap kaise
    """.split()
)

ENGAGE_KINDS = ("reaction", "like", "comment", "save", "share")
SELF_KINDS = ("post", "comment")


def _tokens(text: str) -> list[str]:
    return [t for t in _WORD.findall(text.lower()) if t not in STOPWORDS]


def _terms(text: str) -> list[str]:
    toks = _tokens(text)
    bigrams = [f"{a} {b}" for a, b in zip(toks, toks[1:])]
    return toks + bigrams


def build_liking_profile(
    events: Iterable[EngagementEvent],
    pillars: list[dict[str, Any]],
    top_n: int = 40,
) -> dict[str, Any]:
    """Aggregate engagement events into the liking profile.

    Args:
        events: Parsed export events from any platform.
        pillars: ``brain/pillars.json`` entries, each with ``id`` and ``keywords``.
        top_n: How many topics and authors to keep.

    Returns:
        A JSON-serialisable dict. With zero events it still returns the full
        shape, with empty sections and a note saying exports are missing.
    """
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    topics: Counter[str] = Counter()
    authors: Counter[tuple[str, str]] = Counter()
    hours: Counter[int] = Counter()
    weekdays: Counter[str] = Counter()
    lang_mix: dict[str, Counter[str]] = defaultdict(Counter)
    pillar_hits: Counter[str] = Counter()
    total = 0
    no_ts = 0

    keyword_map = {
        p["id"]: [k.lower() for k in p.get("keywords", [])] for p in pillars if "id" in p
    }

    for ev in events:
        total += 1
        counts[ev.platform][ev.kind] += 1
        text = ev.text or ""

        if ev.kind in ENGAGE_KINDS:
            weight = 3 if ev.kind in ("comment", "save", "share") else 1
            for term in _terms(text):
                topics[term] += weight
            if ev.target_author and ev.target_author != "self":
                authors[(ev.platform, ev.target_author.lower())] += weight
            lowered = text.lower()
            for pid, kws in keyword_map.items():
                if any(k in lowered for k in kws):
                    pillar_hits[pid] += weight

        if ev.kind in SELF_KINDS and text.strip():
            lang_mix[ev.platform][detect_language(text)] += 1

        if ev.timestamp:
            local = parse_ts(ev.timestamp).astimezone(IST)
            hours[local.hour] += 1
            weekdays[local.strftime("%a").lower()] += 1
        else:
            no_ts += 1

    notes: list[str] = []
    if total == 0:
        notes.append("No export data ingested yet. Run `ai-social ingest` with your LinkedIn/Meta/X exports.")
    if no_ts:
        notes.append(f"{no_ts} events had no timestamp (X likes never do); excluded from hour/weekday stats.")
    pillar_total = sum(pillar_hits.values())

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_events": total,
        "event_counts": {p: dict(c) for p, c in sorted(counts.items())},
        "top_topics": [{"term": t, "score": n} for t, n in topics.most_common(top_n) if n > 1],
        "top_authors": [
            {"platform": p, "author": a, "score": n} for (p, a), n in authors.most_common(top_n)
        ],
        "active_hours_ist": {str(h): hours[h] for h in range(24)},
        "active_weekdays_ist": dict(weekdays),
        "own_language_mix": {p: dict(c) for p, c in sorted(lang_mix.items())},
        "pillar_affinity": {
            pid: round(pillar_hits[pid] / pillar_total, 3) if pillar_total else 0.0
            for pid in keyword_map
        },
        "notes": notes,
    }
