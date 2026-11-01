#!/usr/bin/env python3
"""Validate, retrieve and safely append to Daksh's external JSON memory."""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import math
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Iterator


CORE_SECTIONS = ("sources", "memory", "actions", "research", "opportunities", "lessons", "reviews", "automations")
SECTIONS = CORE_SECTIONS + ("tasks",)
EVIDENCE = {"user_instruction", "user_correction", "saved_record", "observed", "reported", "inference", "tested_rule"}
SCOPES = {"global", "project", "scene", "shot", "asset", "task"}


class BrainError(ValueError):
    """A state-contract or concurrency error."""


def require(condition: bool, message: str) -> None:
    """Raise a useful contract error when a condition fails."""
    if not condition:
        raise BrainError(message)


def nonempty(value: object) -> bool:
    """Check a nonblank text value."""
    return isinstance(value, str) and bool(value.strip())


def validate_scope(scope: object, identity: str) -> None:
    """Require explicit scope without converting a local correction to a default."""
    require(isinstance(scope, dict) and scope.get("level") in SCOPES, f"invalid scope: {identity}")
    if scope["level"] in {"project", "scene", "shot", "asset"}:
        require(nonempty(scope.get("project")), f"project required by scope: {identity}")
    if scope["level"] in {"scene", "shot", "asset", "task"}:
        require(nonempty(scope.get("target")), f"target required by scope: {identity}")


def validate_supersession(memory: list[dict[str, Any]]) -> None:
    """Check same-scope supersession links and reject cycles or dangling IDs."""
    rows = {row["id"]: row for row in memory}
    incoming = {identity: 0 for identity in rows}
    graph: dict[str, list[str]] = {}
    for identity, row in rows.items():
        refs = row.get("supersedes", [])
        require(isinstance(refs, list) and all(isinstance(ref, str) for ref in refs), f"invalid supersedes: {identity}")
        require(len(set(refs)) == len(refs), f"duplicate supersedes: {identity}")
        graph[identity] = refs
        for ref in refs:
            require(ref in rows and ref != identity, f"unknown/self supersedes: {identity}")
            previous = rows[ref]
            require(previous["scope"] == row["scope"], f"cross-scope supersession: {identity}")
            require(previous["status"] == "superseded", f"superseded target remains current: {ref}")
            require(previous.get("superseded_by") in (None, identity), f"conflicting supersession: {ref}")
            incoming[ref] += 1
            require(incoming[ref] <= 1, f"multiple superseding rules: {ref}")
        successor = row.get("superseded_by")
        if successor is not None:
            require(nonempty(successor) and successor in rows and identity in rows[successor].get("supersedes", []), f"invalid superseded_by: {identity}")
            require(row["status"] == "superseded", f"superseded_by on current memory: {identity}")
    queue = [identity for identity, degree in incoming.items() if degree == 0]
    for identity in queue:
        for ref in graph[identity]:
            incoming[ref] -= 1
            if incoming[ref] == 0:
                queue.append(ref)
    require(len(queue) == len(rows), "memory supersession cycle")


def validate(data: object) -> dict[str, Any]:
    """Check declared structure/provenance, not source truth or approval authenticity."""
    require(isinstance(data, dict), "brain must be an object")
    require(data.get("schema_version") == 1, "unsupported schema_version")
    require(type(data.get("revision")) is int and data["revision"] >= 1, "revision must be a positive integer")
    require(nonempty(data.get("owner")), "owner is required")
    require(nonempty(data.get("timezone")), "timezone is required")
    require(isinstance(data.get("metrics"), dict), "metrics must be an object")
    try:
        stamp = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        require(stamp.tzinfo is not None, "updated_at requires timezone")
    except (KeyError, AttributeError, TypeError, ValueError) as exc:
        raise BrainError("updated_at must be a timezone-aware ISO datetime") from exc
    all_ids: set[str] = set()
    for section in SECTIONS:
        require(isinstance(data.get(section, [] if section == "tasks" else None), list), f"{section} must be a list")
        for row in data.get(section, []):
            require(isinstance(row, dict), f"{section} records must be objects")
            identity = row.get("id")
            require(nonempty(identity), f"{section} record needs id")
            require(identity not in all_ids, f"duplicate id: {identity}")
            all_ids.add(identity)
    sources = {row["id"]: row for row in data["sources"]}
    for source in sources.values():
        require(nonempty(source.get("kind")) and nonempty(source.get("locator")), f"source needs kind and locator: {source['id']}")
        require(nonempty(source.get("coverage")), f"source coverage is required: {source['id']}")
    for section in SECTIONS[1:]:
        for row in data.get(section, []):
            refs = row.get("source_ids")
            require(isinstance(refs, list) and bool(refs), f"source_ids required: {row['id']}")
            require(all(isinstance(ref, str) and ref in sources for ref in refs), f"unknown source reference: {row['id']}")
    for row in data["memory"]:
        require(nonempty(row.get("claim")), f"empty memory claim: {row['id']}")
        require(row.get("status") in {"active", "proposed", "superseded"}, f"invalid memory status: {row['id']}")
        require(row.get("evidence") in EVIDENCE, f"invalid evidence: {row['id']}")
        validate_scope(row.get("scope"), row["id"])
        if row["status"] == "active":
            require(row["evidence"] not in {"inference", "reported"}, f"unsupported active preference: {row['id']}")
    validate_supersession(data["memory"])
    for row in data["actions"]:
        require(nonempty(row.get("action")), f"empty action: {row['id']}")
        require(row.get("actor") in {"user", "assistant", "tool"}, f"invalid actor: {row['id']}")
        require(row.get("outcome") in {"requested", "observed", "reported", "completed", "approved"}, f"invalid outcome: {row['id']}")
        if row["outcome"] == "approved":
            require(row["actor"] == "user" and any(sources[ref]["kind"] in {"user_instruction", "user_correction"} for ref in row["source_ids"]), f"approval needs an explicit user source: {row['id']}")
    for row in data["research"]:
        require(nonempty(row.get("finding")), f"empty research: {row['id']}")
        require(row.get("verification") in {"documented", "tested_text", "tested_media", "historical", "proposed"}, f"invalid research verification: {row['id']}")
    for row in data["opportunities"]:
        require(nonempty(row.get("problem")) and nonempty(row.get("next_step")), f"opportunity needs problem and next step: {row['id']}")
        require(row.get("status") in {"hypothesis", "research", "experiment_ready", "testing", "validated", "paused", "rejected"}, f"invalid opportunity status: {row['id']}")
        if row["status"] == "validated":
            refs = row.get("validation_evidence_ids")
            require(isinstance(refs, list) and bool(refs) and all(ref in sources for ref in refs), f"validation evidence required: {row['id']}")
    for row in data["lessons"]:
        require(nonempty(row.get("rule")), f"empty lesson: {row['id']}")
        require(row.get("status") in {"candidate", "active", "retired"}, f"invalid lesson status: {row['id']}")
        if row["status"] == "active" and row.get("evidence") not in {"user_instruction", "user_correction"}:
            test = row.get("test", {})
            require(isinstance(test, dict) and test.get("outcome") == "pass" and nonempty(test.get("extent")), f"active inferred lesson needs test extent: {row['id']}")
    for row in data.get("tasks", []):
        require(nonempty(row.get("title")), f"task title required: {row['id']}")
        owner = row.get("owner", {})
        require(isinstance(owner, dict) and owner.get("kind") in {"user", "assistant", "other", "unassigned"} and nonempty(owner.get("name")), f"invalid task owner: {row['id']}")
        require(row.get("status") in {"open", "in_progress", "blocked", "done", "cancelled"}, f"invalid task status: {row['id']}")
        require(row.get("priority") in {"P0", "P1", "P2"}, f"invalid priority: {row['id']}")
        validate_scope(row.get("scope"), row["id"])
        assignment = row.get("assignment_evidence", {})
        require(isinstance(assignment, dict) and assignment.get("kind") in {"explicit_user_request", "explicit_assignment", "assistant_proposal", "third_party_report"}, f"invalid task assignment: {row['id']}")
        refs = assignment.get("source_ids")
        require(isinstance(refs, list) and bool(refs) and all(ref in row["source_ids"] for ref in refs), f"assignment sources required: {row['id']}")
        if owner["kind"] == "user":
            require(assignment["kind"] in {"explicit_user_request", "explicit_assignment"} and any(sources[ref]["kind"] in {"user_instruction", "user_correction"} for ref in refs), f"user task needs explicit assignment: {row['id']}")
        if row["status"] in {"open", "in_progress", "blocked"}:
            require(nonempty(row.get("next_action")), f"live task needs next_action: {row['id']}")
        if row["status"] == "blocked":
            require(nonempty(row.get("blocked_reason")), f"blocked task needs reason: {row['id']}")
        if row["status"] == "done":
            refs = row.get("completion_evidence_ids")
            require(isinstance(refs, list) and bool(refs) and all(isinstance(ref, str) and ref in sources for ref in refs), f"done task needs completion evidence: {row['id']}")
    if "coverage" in data:
        require(isinstance(data["coverage"], dict), "coverage must be an object")
        for flag in ("all_chats_accessible", "passive_device_monitoring"):
            if flag in data["coverage"]:
                require(data["coverage"][flag] is False, f"unsupported capability claim: {flag}")
    return data


def load(path: Path) -> dict[str, Any]:
    """Read and validate one materialized brain."""
    return validate(json.loads(path.read_text(encoding="utf-8")))


def summary(data: dict[str, Any]) -> dict[str, Any]:
    """Return a small overview without full private records."""
    return {"schema_version": data["schema_version"], "revision": data["revision"], "updated_at": data["updated_at"], "counts": {key: len(data.get(key, [])) for key in SECTIONS}, "metrics": data["metrics"], "coverage": data.get("coverage")}


def tokens(value: str) -> list[str]:
    """Tokenize Unicode words and exact-ish tag components for lexical ranking."""
    return re.findall(r"(?u)\b\w[\w@.-]*\b", value.casefold())


def current(section: str, row: dict[str, Any]) -> bool:
    """Choose current candidates; historical search is explicitly opt-in."""
    if section in {"memory", "lessons"}:
        return row.get("status") == "active"
    if section == "opportunities":
        return row.get("status") not in {"paused", "rejected"}
    if section == "tasks":
        return row.get("status") in {"open", "in_progress", "blocked"} and row["owner"]["kind"] in {"user", "assistant"}
    return True


def scope_rank(row: dict[str, Any], project: str | None, target: str | None) -> int:
    """Return specificity, or -1 for an inapplicable/unscoped candidate."""
    if project is None and target is None:
        return 0
    scope = row.get("scope")
    if not isinstance(scope, dict):
        return -1
    if scope.get("level") == "global":
        return 0
    if scope.get("project") is not None and scope["project"] != project:
        return -1
    if scope.get("level") == "project":
        return 1 if project is not None else -1
    return 2 if target is not None and scope.get("target") == target else -1


def retrieve(data: dict[str, Any], query: str, top_k: int = 6, *, project: str | None = None, target: str | None = None, include_inactive: bool = False) -> list[dict[str, Any]]:
    """Rank lexical candidates with BM25; do not claim semantic retrieval."""
    require(nonempty(query), "query must not be blank")
    require(1 <= top_k <= 50, "top_k must be between 1 and 50")
    rows = [(section, row, json.dumps(row, ensure_ascii=False)) for section in SECTIONS[1:] for row in data.get(section, []) if (include_inactive or current(section, row)) and scope_rank(row, project, target) >= 0]
    documents = [Counter(tokens(text)) for _, _, text in rows]
    query_terms = set(tokens(query))
    if not rows or not query_terms:
        return []
    lengths = [sum(doc.values()) for doc in documents]
    average = sum(lengths) / len(lengths) or 1
    frequency = Counter(term for doc in documents for term in doc)
    ranked = []
    for (section, row, text), doc, length in zip(rows, documents, lengths):
        score = 0.0
        for term in query_terms:
            count = doc[term]
            if count:
                inverse = math.log(1 + (len(rows) - frequency[term] + 0.5) / (frequency[term] + 0.5))
                score += inverse * count * 2.2 / (count + 1.2 * (0.25 + 0.75 * length / average))
        if query.casefold() in text.casefold():
            score += 2
        if score:
            excerpt = next((row[key] for key in ("claim", "finding", "action", "problem", "rule", "title") if nonempty(row.get(key))), text)
            ranked.append({"section": section, "id": row["id"], "status": row.get("status", row.get("outcome", row.get("verification"))), "evidence": row.get("evidence"), "scope": row.get("scope"), "owner": row.get("owner"), "source_ids": row["source_ids"], "score": round(score, 6), "specificity": scope_rank(row, project, target), "excerpt": excerpt[:600]})
    return sorted(ranked, key=lambda row: (-row["specificity"], -row["score"], row["id"]))[:top_k]


def agenda(data: dict[str, Any], owner: str | None = None) -> list[dict[str, Any]]:
    """Return live commitments, keeping other people's assignments out by default."""
    validate(data)
    require(owner in {None, "user", "assistant", "all"}, "invalid agenda owner")
    kinds = {"user", "assistant"} if owner is None else ({"user", "assistant", "other", "unassigned"} if owner == "all" else {owner})
    return sorted((row for row in data.get("tasks", []) if row["status"] in {"open", "in_progress", "blocked"} and row["owner"]["kind"] in kinds), key=lambda row: (row["priority"], row["id"]))


@contextmanager
def locked(path: Path) -> Iterator[None]:
    """Serialize local writers; remote Library conflicts need their own guard."""
    with path.with_name(path.name + ".lock").open("a", encoding="utf-8") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def atomic_write(path: Path, data: dict[str, Any]) -> None:
    """Replace bytes atomically while preserving existing Library identity xattrs."""
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    attrs = {name: os.getxattr(path, name) for name in os.listxattr(path)} if path.exists() else {}
    handle, temporary = tempfile.mkstemp(dir=path.parent, prefix=".daksh-")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        for name, value in attrs.items():
            os.setxattr(temporary, name, value)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def append(path: Path, section: str, record: object, expected_revision: int) -> tuple[dict[str, Any], bool]:
    """Append a validated record with optimistic locking and idempotent retries."""
    require(section in SECTIONS, "unknown section")
    require(isinstance(record, dict) and nonempty(record.get("id")), "record must have an id")
    with locked(path):
        data = load(path)
        for existing in data.get(section, []):
            if existing["id"] == record["id"]:
                require(existing == record, "existing id has different content; use an explicit supersession")
                return data, False
        require(data["revision"] == expected_revision, f"revision conflict: expected {expected_revision}, actual {data['revision']}")
        data.setdefault(section, []).append(record)
        data["revision"] += 1
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        validate(data)
        atomic_write(path, data)
        return data, True


def supersede(path: Path, old_id: str, record: object, expected_revision: int) -> tuple[dict[str, Any], bool]:
    """Atomically replace an explicitly corrected same-scope memory, preserving history."""
    require(isinstance(record, dict) and nonempty(record.get("id")), "replacement record needs id")
    replacement = deepcopy(record)
    require(replacement.get("supersedes", [old_id]) == [old_id], "replacement must supersede exactly old_id")
    replacement["supersedes"] = [old_id]
    with locked(path):
        data = load(path)
        rows = {row["id"]: row for row in data["memory"]}
        require(old_id in rows and old_id != replacement["id"], "unknown/self replacement")
        previous = rows[old_id]
        if replacement["id"] in rows:
            require(rows[replacement["id"]] == replacement and previous.get("superseded_by") == replacement["id"], "conflicting replacement identity")
            return data, False
        require(data["revision"] == expected_revision, "revision conflict")
        require(previous["status"] in {"active", "proposed"}, "memory is already superseded")
        require(replacement.get("status") == "active" and replacement.get("evidence") in {"user_instruction", "user_correction"}, "replacement requires an explicit current correction")
        require(previous["scope"] == replacement.get("scope"), "cross-scope replacement")
        previous.update(status="superseded", superseded_by=replacement["id"])
        data["memory"].append(replacement)
        data["revision"] += 1
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        validate(data)
        atomic_write(path, data)
        return data, True


def task_update(path: Path, identity: str, state: object, expected_revision: int) -> tuple[dict[str, Any], bool]:
    """Advance task state with evidence, without changing its owner or assignment."""
    allowed = {"status", "next_action", "blocked_reason", "completion_evidence_ids"}
    require(isinstance(state, dict) and "status" in state and set(state) <= allowed, "task state has unknown/missing fields")
    with locked(path):
        data = load(path)
        row = next((row for row in data.get("tasks", []) if row["id"] == identity), None)
        require(row is not None, "unknown task")
        updated = deepcopy(row)
        updated.update(deepcopy(state))
        if updated["status"] != "blocked":
            updated.pop("blocked_reason", None)
        if updated["status"] != "done":
            updated.pop("completion_evidence_ids", None)
        if updated == row:
            return data, False
        require(data["revision"] == expected_revision, "revision conflict")
        require(row["status"] not in {"done", "cancelled"}, "terminal task cannot be reopened; record a new explicit request")
        row.clear()
        row.update(updated)
        data["revision"] += 1
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        validate(data)
        atomic_write(path, data)
        return data, True


def main() -> int:
    """Run the local-only CLI; it never calls apps or executes stored instructions."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "summary", "agenda"):
        commands.add_parser(name).add_argument("path", type=Path)
    commands.choices["agenda"].add_argument("--owner", choices=("user", "assistant", "all"))
    search = commands.add_parser("retrieve")
    search.add_argument("path", type=Path)
    search.add_argument("query")
    search.add_argument("--top-k", type=int, default=6)
    search.add_argument("--project")
    search.add_argument("--target")
    search.add_argument("--include-inactive", action="store_true")
    add = commands.add_parser("append")
    add.add_argument("path", type=Path)
    add.add_argument("section", choices=SECTIONS)
    add.add_argument("record", type=Path)
    add.add_argument("--expected-revision", type=int, required=True)
    replace = commands.add_parser("supersede")
    replace.add_argument("path", type=Path)
    replace.add_argument("old_id")
    replace.add_argument("record", type=Path)
    replace.add_argument("--expected-revision", type=int, required=True)
    task = commands.add_parser("task-update")
    task.add_argument("path", type=Path)
    task.add_argument("identity")
    task.add_argument("record", type=Path)
    task.add_argument("--expected-revision", type=int, required=True)
    args = parser.parse_args()
    try:
        if args.command in {"append", "supersede", "task-update"}:
            record = json.loads(args.record.read_text(encoding="utf-8"))
            if args.command == "append":
                data, changed = append(args.path, args.section, record, args.expected_revision)
            elif args.command == "supersede":
                data, changed = supersede(args.path, args.old_id, record, args.expected_revision)
            else:
                data, changed = task_update(args.path, args.identity, record, args.expected_revision)
            result = {"status": "ok", "changed": changed, "revision": data["revision"], "remote_save": "not_performed"}
        else:
            data = load(args.path)
            if args.command == "retrieve":
                result = retrieve(data, args.query, args.top_k, project=args.project, target=args.target, include_inactive=args.include_inactive)
            else:
                result = agenda(data, args.owner) if args.command == "agenda" else summary(data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (BrainError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Daksh state error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
