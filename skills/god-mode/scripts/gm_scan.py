#!/usr/bin/env python3
"""God Mode internal recon: rank this repo's agents, skills and reference modules for a goal.

Usage:
  python skills/god-mode/scripts/gm_scan.py "goal text" [--root REPO] [--top 12] [--json]
  python skills/god-mode/scripts/gm_scan.py --inventory [--root REPO]

Pure standard library, read-only. Scoring is lexical (BM25-style) with field weights,
so it finds candidates fast; the God Mode run must still read the top hits before
relying on them.

Also ranks the skills of any pinned module Daksh Brain has integrated (see
integrations/*.json, e.g. integrations/ai-film.json for the modules/ai-film
submodule), reading each module's hashed skill_inventory catalog. Those hits are
kind "module_skill" with a "module" field. If the submodule is checked out
(`git submodule update --init -- modules/ai-film`) its real SKILL.md is read for a
full description; otherwise only the catalog's id/name/owner are used, and the hit
is marked "(not checked out)".
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

# Field weights: skill name/description and agent titles matter most.
WEIGHTS = {"name": 4.0, "description": 3.0, "title": 3.0, "headings": 1.5, "body": 1.0}
BODY_CHARS = 6000  # enough to catch the purpose/workflow sections without drowning in ledgers

STOPWORDS = set(
    """a an and are as at be by for from has have in is it its of on or that the this to was were will with
    use using used do does not no only when what which who how why can may must should than then there these those
    into about over under per via any all each every our your my me we you they them he she his her
    ka ki ke ko se me mein hai hain ho aur ya bhi ek jo kya kaise kab kr kar karo krna karna krdo""".split()
)

# Small bilingual/intent bridge so Hinglish goals hit English skill text.
SYNONYMS = {
    "gaana": ["song", "music", "lyrics"], "song": ["music", "lyrics"], "music": ["score", "song"],
    "awaaz": ["voice", "dubbing"], "voice": ["dubbing", "tts"], "dub": ["dubbing"],
    "video": ["shot", "camera", "director"], "film": ["shot", "director", "screenplay"],
    "kahani": ["story", "screenplay", "writer"], "story": ["screenplay", "writer"], "script": ["screenplay", "writer"],
    "jagah": ["location"], "location": ["props", "spatial"], "set": ["location"],
    "post": ["social", "caption"], "instagram": ["social", "caption"], "caption": ["social"],
    "fashion": ["campaign", "editorial"], "kapde": ["fashion", "garment"],
    "plan": ["weekly", "planning"], "slack": ["maniik", "weekly"], "kaam": ["work", "plan"],
    "business": ["buyer", "offer", "experiment"], "startup": ["business", "founder"], "founder": ["business"],
    "research": ["sources", "evidence"], "agent": ["orchestration", "specialist"], "brain": ["memory", "daksh"],
    "memory": ["brain"], "automation": ["schedule", "runtime"], "suno": ["instrumental", "music"],
}


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9][a-z0-9+\-]*", text.lower())
    out = []
    for w in words:
        w = w.strip("-")
        if len(w) < 2 or w in STOPWORDS:
            continue
        out.append(w)
        if len(w) > 4 and w.endswith("s") and not w.endswith("ss"):
            out.append(w[:-1])  # crude plural fold
    return out


def expand_query(text: str) -> list[str]:
    base = tokenize(text)
    extra = [s for t in base for s in SYNONYMS.get(t, [])]
    return base + extra


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if m:
            meta[m.group(1)] = m.group(2).strip().strip("'\"")
    return meta, text[end + 4:]


def headings(text: str) -> str:
    return " ".join(re.findall(r"^#{1,4}\s+(.+)$", text, flags=re.M))


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def collect(root: Path) -> list[dict]:
    docs: list[dict] = []
    skills_dir = root / "skills"
    if skills_dir.is_dir():
        for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
            meta, body = parse_frontmatter(read(skill_md))
            name = meta.get("name", skill_md.parent.name)
            docs.append({
                "kind": "skill", "id": name, "path": str(skill_md.relative_to(root)),
                "summary": meta.get("description", "")[:240],
                "fields": {"name": name.replace("-", " "), "description": meta.get("description", ""),
                           "headings": headings(body), "body": body[:BODY_CHARS]},
            })
            for ref in sorted(skill_md.parent.glob("references/*.md")):
                text = read(ref)
                title = (re.search(r"^#\s+(.+)$", text, flags=re.M) or [None, ref.stem])[1]
                docs.append({
                    "kind": "reference", "id": f"{name}/{ref.stem}", "path": str(ref.relative_to(root)),
                    "summary": title,
                    "fields": {"title": f"{title} {ref.stem.replace('-', ' ')}", "headings": headings(text),
                               "body": text[:BODY_CHARS], "name": name.replace("-", " ")},
                })
    agents_dir = root / "agents"
    if agents_dir.is_dir():
        for md in sorted(agents_dir.glob("*.md")):
            text = read(md)
            title = (re.search(r"^#\s+(.+)$", text, flags=re.M) or [None, md.stem])[1]
            docs.append({
                "kind": "agent", "id": md.stem, "path": str(md.relative_to(root)), "summary": title,
                "fields": {"title": f"{title} {md.stem.replace('_', ' ').lower()}",
                           "headings": headings(text[:40000]), "body": text[:BODY_CHARS]},
            })
    registry = skills_dir / "daksh" / "assets" / "agent-registry.json"
    if registry.is_file():
        try:
            data = json.loads(read(registry))
        except json.JSONDecodeError:
            data = {}
        for role in data.get("roles", []):
            docs.append({
                "kind": "role", "id": role.get("id", "?"), "path": str(registry.relative_to(root)),
                "summary": f"{role.get('label', '')} -> skill {role.get('skill_name')}",
                "fields": {"title": role.get("label", ""), "description": " ".join(role.get("tasks", [])),
                           "body": role.get("handoff", "")},
            })
    docs.extend(collect_modules(root))
    return docs


def collect_modules(root: Path) -> list[dict]:
    """Load pinned-module skills from integrations/*.json + their skill_inventory catalog.

    Each integrations/<id>.json (written when Daksh Brain integrates a sister repo as a
    pinned git submodule, e.g. integrations/ai-film.json) points at a hashed
    skill_inventory catalog (e.g. catalog/ai-film-skills.json: a list of
    {id, name, path, owner_agent_id, kind, sha256}). This reuses that single source of
    truth instead of maintaining a second index: no network calls, no duplicated catalog.
    """
    docs: list[dict] = []
    integrations_dir = root / "integrations"
    if not integrations_dir.is_dir():
        return docs
    for integ_path in sorted(integrations_dir.glob("*.json")):
        module_id = integ_path.stem
        try:
            integ = json.loads(read(integ_path))
        except json.JSONDecodeError:
            continue
        inventory_rel = integ.get("skill_inventory")
        module_root = root / integ.get("source", {}).get("path", "") if integ.get("source", {}).get("path") else None
        if not inventory_rel or not (root / inventory_rel).is_file():
            continue
        try:
            catalog = json.loads(read(root / inventory_rel))
        except json.JSONDecodeError:
            continue
        for entry in catalog.get("skills", catalog if isinstance(catalog, list) else []):
            doc_id = entry.get("id") or f"{module_id}:{entry.get('name', '?')}"
            name = entry.get("name", doc_id)
            description, excerpt, checked_out = "", "", False
            if module_root is not None and entry.get("path"):
                skill_file = module_root / entry["path"]
                if skill_file.is_file():
                    meta, body = parse_frontmatter(read(skill_file))
                    description, excerpt, checked_out = meta.get("description", ""), body.strip(), True
            if not description:
                description = f"{name} ({entry.get('kind', 'skill')}), owner: {entry.get('owner_agent_id', '?')}"
            docs.append({
                "kind": "module_skill", "id": doc_id,
                "path": f"{integ.get('source', {}).get('path', module_id)}/{entry.get('path', '')}",
                "module": module_id, "checked_out": checked_out,
                "summary": description[:240],
                "fields": {"name": name.replace("-", " "), "description": description,
                           "body": excerpt[:BODY_CHARS]},
            })
    return docs


def rank(docs: list[dict], query: str, top: int = 12) -> list[dict]:
    q = expand_query(query)
    if not q or not docs:
        return []
    qset = Counter(q)
    # document frequency over all fields combined
    bags = []
    for d in docs:
        bag = {f: Counter(tokenize(t)) for f, t in d["fields"].items()}
        bags.append(bag)
    n = len(docs)
    df = Counter()
    for bag in bags:
        seen = set()
        for c in bag.values():
            seen.update(c)
        df.update(seen)
    results = []
    for d, bag in zip(docs, bags):
        score, hits = 0.0, set()
        for term, qtf in qset.items():
            if term not in df:
                continue
            idf = math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
            for field, counts in bag.items():
                tf = counts.get(term, 0)
                if tf:
                    length = sum(counts.values()) or 1
                    norm = tf * 2.2 / (tf + 1.2 * (0.25 + 0.75 * min(length / 400, 4)))
                    score += WEIGHTS.get(field, 1.0) * idf * norm * (1 + 0.2 * (qtf - 1))
                    hits.add(term)
        if score > 0:
            row = {"kind": d["kind"], "id": d["id"], "path": d["path"], "score": round(score, 2),
                   "matched": sorted(hits), "summary": d["summary"]}
            if "module" in d:
                row["module"], row["checked_out"] = d["module"], d["checked_out"]
            results.append(row)
    results.sort(key=lambda r: (-r["score"], r["kind"], r["id"]))
    return results[:top]


def inventory(docs: list[dict]) -> dict:
    out: dict[str, list[str]] = {}
    for d in docs:
        if d["kind"] in ("skill", "agent", "role", "module_skill"):
            out.setdefault(d["kind"], []).append(d["id"])
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("goal", nargs="?", default="")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[3]))
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--inventory", action="store_true")
    args = ap.parse_args(argv)
    docs = collect(Path(args.root))
    if args.inventory:
        print(json.dumps(inventory(docs), indent=2))
        return 0
    if not args.goal.strip():
        ap.error("goal text required (or --inventory)")
    results = rank(docs, args.goal, args.top)
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 0
    if not results:
        print("No internal match. Treat this as a capability gap and research externally.")
        return 0
    for i, r in enumerate(results, 1):
        if "module" in r:
            state = "" if r["checked_out"] else " — not checked out, catalog-only description"
            tag = f" [MODULE: {r['module']}{state}]"
        else:
            tag = ""
        print(f"{i:>2}. [{r['kind']}] {r['id']}  score={r['score']}  ({r['path']}){tag}")
        print(f"    matched: {', '.join(r['matched'][:8])}")
        print(f"    {r['summary'][:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
