"""Cheap language tagger for posts and comments.

Designed to be deleted: once an LLM tags language at draft time and the logs
carry that tag, this heuristic only matters for old export data.
"""
from __future__ import annotations

import re

_DEVANAGARI = re.compile(r"[\u0900-\u097F]")
_LATIN = re.compile(r"[A-Za-z]")
_TOKEN = re.compile(r"[A-Za-z]+")

# Romanised Hindi words that rarely appear in English text. Short English
# collisions ("to", "me", "is", "the") are left out on purpose.
HINGLISH_MARKERS: frozenset[str] = frozenset(
    """
    hai hain tha thi hoga hogi kya kyu kyun kaise kaisa kaun kab kahan nahi nahin
    bhai yaar mein mai mera meri mere tera teri tum aap hum humne ham apna apni
    aur toh bhi sab kuch bahut bohot accha acha theek thik abhi phir fir
    kar karo karna kiya kiye raha rahi rahe wala wali wale dekho dekh bana banaya
    banayi ek teen jab tak sirf bas yeh ye woh wo unka uska iska inka
    logon kaam baat sach dil ghar gaon desi boli boliyon chahiye sakta sakti
    """.split()
)


def detect_language(text: str) -> str:
    """Tag text as ``hi``, ``hinglish`` or ``en``.

    Args:
        text: Any post, caption or comment.

    Returns:
        ``hi`` when Devanagari dominates the letters, ``hinglish`` when enough
        romanised Hindi markers appear, otherwise ``en``. Empty text is ``en``.
    """
    if not text or not text.strip():
        return "en"
    deva = len(_DEVANAGARI.findall(text))
    latin = len(_LATIN.findall(text))
    if deva and deva >= latin:
        return "hi"
    tokens = [t.lower() for t in _TOKEN.findall(text)]
    if not tokens:
        return "hi" if deva else "en"
    hits = sum(1 for t in tokens if t in HINGLISH_MARKERS)
    if deva or hits >= 3 or (hits >= 2 and hits / len(tokens) >= 0.08):
        return "hinglish"
    return "en"
