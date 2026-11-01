"""Deterministic graders for maniik brain evals.

Each check is a dict with a "type" and parameters. `grade(output, checks, root)` returns a
list of {type, ok, detail}. Graders never call a model; they encode Manik's explicit locks
as checkable rules. Passing them proves format/lock compliance, not creative quality.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

TAG_RE = re.compile(r"@[a-z0-9][a-z0-9._-]*[a-z0-9]", re.I)
WORD_RE = re.compile(r"[\wऀ-ॿ]+")
FENCE_RE = re.compile(r"^\s*```")


def strip_fences(text: str) -> str:
    """Drop markdown code-fence lines so prompts inside a copyable block are graded as content."""
    return "\n".join(line for line in text.splitlines() if not FENCE_RE.match(line)).strip("\n")


def _flags(spec: dict) -> int:
    flags = re.M
    for ch in spec.get("flags", ""):
        flags |= {"i": re.I, "s": re.S}.get(ch, 0)
    return flags


def _nonempty_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip()]


def words(text: str) -> list[str]:
    """Spoken-word tokens: bracketed delivery tags removed, case-folded."""
    return [w.casefold() for w in WORD_RE.findall(re.sub(r"\[[^\]]*\]", " ", text))]


def _contains_sequence(hay: list[str], needle: list[str]) -> bool:
    if not needle:
        return True
    n = len(needle)
    return any(hay[i:i + n] == needle for i in range(len(hay) - n + 1))


def check_regex_present(text, spec, root):
    m = re.search(spec["pattern"], text, _flags(spec))
    return bool(m), f"found {m.group(0)[:60]!r}" if m else f"missing /{spec['pattern']}/"


def check_regex_absent(text, spec, root):
    m = re.search(spec["pattern"], text, _flags(spec))
    return (not m), "absent" if not m else f"forbidden {m.group(0)[:60]!r}"


def check_count_regex(text, spec, root):
    n = len(re.findall(spec["pattern"], text, _flags(spec)))
    lo, hi = spec.get("min", 0), spec.get("max", float("inf"))
    return lo <= n <= hi, f"count={n} (want {lo}..{hi})"


def check_last_line(text, spec, root):
    lines = _nonempty_lines(text)
    if not lines:
        return False, "empty output"
    ok = re.search(spec["pattern"], lines[-1].strip(), _flags(spec)) is not None
    return ok, f"last line: {lines[-1].strip()[:80]!r}"


def check_blank_line_before(text, spec, root):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.search(spec["pattern"], line, _flags(spec)):
            ok = i > 0 and not lines[i - 1].strip()
            return ok, "blank line present" if ok else f"line before is {lines[i - 1][:60]!r}" if i else "match on first line"
    return False, f"no line matches /{spec['pattern']}/"


def check_tags(text, spec, root):
    found = {t.lower() for t in TAG_RE.findall(text)}
    required = {t.lower() for t in spec.get("required", [])}
    missing = sorted(required - found)
    problems = []
    if missing:
        problems.append(f"missing {missing}")
    if "allowed" in spec:
        extra = sorted(found - {t.lower() for t in spec["allowed"]} - required)
        if extra:
            problems.append(f"not allowed {extra}")
    for t in spec.get("forbidden", []):
        if t.lower() in found:
            problems.append(f"forbidden {t}")
    return not problems, "; ".join(problems) or f"tags ok {sorted(found)}"


def check_max_chars(text, spec, root):
    n = len(text.strip())
    return n <= spec["max"], f"{n} chars (max {spec['max']})"


def check_preserves_words(text, spec, root):
    ok = _contains_sequence(words(text), words(spec["text"]))
    return ok, "exact words in order" if ok else f"words changed/missing for {spec['text'][:50]!r}"


def check_scan_top(text, spec, root):
    """Routing proxy: does gm_scan rank the expected skill within the top N for this prompt?"""
    scanner = Path(root) / "skills/god-mode/scripts/gm_scan.py"
    out = subprocess.run([sys.executable, str(scanner), text, "--root", str(root), "--json", "--top", "25"],
                         capture_output=True, text=True, check=False)
    import json
    try:
        ranked = json.loads(out.stdout or "[]")
    except json.JSONDecodeError:
        return False, f"scanner error: {out.stderr[:120]}"
    skills = []
    for r in ranked:
        sid = r["id"].split("/")[0] if r["kind"] in ("skill", "reference") else None
        if sid and sid not in skills:
            skills.append(sid)
    within = spec.get("within", 1)
    ok = spec["expect"] in skills[:within]
    return ok, f"top skills {skills[:within + 2]}"


CHECKS = {
    "regex_present": check_regex_present,
    "regex_absent": check_regex_absent,
    "count_regex": check_count_regex,
    "last_line": check_last_line,
    "blank_line_before": check_blank_line_before,
    "tags": check_tags,
    "max_chars": check_max_chars,
    "preserves_words": check_preserves_words,
    "scan_top": check_scan_top,
}


def grade(output: str, checks: list[dict], root: str | Path = ".", fences: bool = True) -> list[dict]:
    text = strip_fences(output) if fences else output
    results = []
    for spec in checks:
        fn = CHECKS.get(spec.get("type"))
        if fn is None:
            results.append({"type": spec.get("type"), "ok": False, "detail": "unknown check type"})
            continue
        try:
            ok, detail = fn(text, spec, root)
        except (KeyError, re.error) as exc:
            ok, detail = False, f"bad check spec: {exc}"
        results.append({"type": spec["type"], "ok": bool(ok), "detail": detail})
    return results
