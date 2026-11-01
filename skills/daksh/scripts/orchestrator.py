#!/usr/bin/env python3
"""Validate and update Daksh's local task ledger; never launch workers or tools.

The JSON contains declarations and evidence references, never executable commands.
This controller checks ledger consistency, not artifact truth, approval authenticity,
worker isolation, or the availability of any referenced artifact.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Callable, Sequence
from uuid import uuid4

from brain import BrainError, atomic_write, locked, require


Run = dict[str, Any]
Event = dict[str, Any]
STATES = ("pending", "running", "done", "blocked", "failed", "cancelled")
_RUN_KEYS = {
    "schema_version", "run_id", "revision", "objective", "layer", "execution_mode",
    "status", "canonical_writer", "max_parallel", "permissions", "source_versions",
    "locks", "history", "nodes", "review_node_id",
}
_NODE_KEYS = {
    "id", "role", "goal", "depends_on", "source_ids", "permissions", "write_targets",
    "checks", "status", "attempt", "max_attempts", "worker_id", "assignment_id",
    "input_versions", "dependency_assignments", "result",
}
_DYNAMIC_KEYS = {
    "status", "attempt", "worker_id", "assignment_id", "input_versions",
    "dependency_assignments", "result",
}
_RESULT_KEYS = {
    "node_id", "assignment_id", "source_versions", "dependency_assignments",
    "artifacts", "checks",
}
_COMPLETION_KEYS = {
    "required_node_status", "required_check_outcome", "unresolved_blockers",
    "current_source_snapshots", "independent_final_review", "observed_delivery_or_save",
}
_EVENT_KEYS = {
    "assign": {
        "event", "revision", "node_id", "worker_id", "assignment_id", "attempt",
        "input_versions", "dependency_assignments", "contract_digest",
    },
    "finish": {"event", "revision", "result"},
    "block": {"event", "revision", "node_id", "reason"},
    "retry": {"event", "revision", "node_id"},
    "invalidate": {
        "event", "revision", "source_id", "previous_version", "version", "node_ids",
    },
    "cancel": {"event", "revision", "reason", "node_ids"},
}


def _text(value: object, label: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{label} must be nonblank text")
    return value


def _integer(value: object, label: str, low: int, high: int | None = None) -> int:
    require(type(value) is int and value >= low, f"{label} must be an integer >= {low}")
    require(high is None or value <= high, f"{label} must be <= {high}")
    return value


def _object(value: object, keys: set[str], label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be an object")
    require(set(value) == keys, f"{label} has missing or unknown fields: {sorted(set(value) ^ keys, key=str)}")
    return value


def _texts(value: object, label: str) -> list[str]:
    require(isinstance(value, list), f"{label} must be a list")
    for item in value:
        _text(item, label)
    require(len(set(value)) == len(value), f"{label} contains duplicates")
    return value


def _versions(value: object, label: str) -> dict[str, str]:
    require(isinstance(value, dict), f"{label} must be an object of text keys and values")
    for key, version in value.items():
        _text(key, f"{label} key")
        _text(version, f"{label}[{key}]")
    return value


def _result_shape(value: object) -> dict[str, Any]:
    result = _object(value, _RESULT_KEYS, "result")
    _text(result["node_id"], "result.node_id")
    _text(result["assignment_id"], "result.assignment_id")
    _versions(result["source_versions"], "result.source_versions")
    _versions(result["dependency_assignments"], "result.dependency_assignments")
    require(bool(_texts(result["artifacts"], "result.artifacts")), "result needs nonempty artifact references")
    checks = result["checks"]
    require(isinstance(checks, list) and bool(checks), "result.checks must be a nonempty list")
    ids = []
    for check in checks:
        _object(check, {"id", "outcome", "evidence"}, "result check")
        ids.append(_text(check["id"], "check.id"))
        require(check["outcome"] in ("pass", "fail", "not_run"), "check.outcome must be pass, fail, or not_run")
        _text(check["evidence"], "check.evidence")
    require(len(set(ids)) == len(ids), "result.checks contains duplicate IDs")
    return result


def _event_shape(value: object) -> Event:
    require(isinstance(value, dict), "history events must be objects")
    name = value.get("event")
    require(isinstance(name, str) and name in _EVENT_KEYS, "unknown history event")
    event = _object(value, _EVENT_KEYS[name], f"history {name}")
    _integer(event["revision"], "history revision", 2)
    if name in ("assign", "block", "retry"):
        _text(event["node_id"], "history node_id")
    if name == "assign":
        _text(event["worker_id"], "history worker_id")
        _text(event["assignment_id"], "history assignment_id")
        _integer(event["attempt"], "history attempt", 1, 3)
        _versions(event["input_versions"], "history input_versions")
        _versions(event["dependency_assignments"], "history dependency_assignments")
        digest = _text(event["contract_digest"], "history contract_digest")
        require(len(digest) == 64 and all(char in "0123456789abcdef" for char in digest),
                "history contract_digest must be a lowercase SHA-256 hex digest")
    elif name == "finish":
        _result_shape(event["result"])
    elif name in ("block", "cancel"):
        _text(event["reason"], "history reason")
    if name == "invalidate":
        for key in ("source_id", "previous_version", "version"):
            _text(event[key], f"history {key}")
    if name in ("invalidate", "cancel"):
        _texts(event["node_ids"], "history node_ids")
    return event


def _nodes(data: Run) -> dict[str, dict[str, Any]]:
    return {node["id"]: node for node in data["nodes"]}


def _node(data: Run, node_id: str) -> dict[str, Any]:
    require(node_id in _nodes(data), f"unknown node: {node_id}")
    return _nodes(data)[node_id]


def _limit(data: Run) -> int:
    return 1 if data["execution_mode"] == "sequential_skills" else data["max_parallel"]


def _contract_digest(data: Run) -> str:
    """Hash the immutable contract, excluding runtime state and source versions.

    JSON object keys and set-like lists are sorted so formatting and declaration
    order do not change the digest. Exact lock text and declared path text do.
    This binds assignments to a contract; it is not an authenticated signature.
    """
    excluded = {"revision", "status", "history", "nodes", "source_versions"}
    contract = {key: data[key] for key in _RUN_KEYS - excluded}
    if "completion_contract" in data:
        contract["completion_contract"] = data["completion_contract"]
    contract["permissions"] = sorted(data["permissions"])
    contract["locks"] = sorted(data["locks"], key=lambda lock: lock["id"])
    contract["source_ids"] = sorted(data["source_versions"])
    static_nodes = []
    for node in data["nodes"]:
        static = {key: node[key] for key in _NODE_KEYS - _DYNAMIC_KEYS}
        for key in ("depends_on", "source_ids", "permissions", "write_targets", "checks"):
            static[key] = sorted(node[key])
        static_nodes.append(static)
    contract["nodes"] = sorted(static_nodes, key=lambda node: node["id"])
    payload = json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _affected(data: Run, source_id: str) -> list[str]:
    affected = {node["id"] for node in data["nodes"] if source_id in node["source_ids"]}
    while True:
        expanded = affected | {
            node["id"] for node in data["nodes"] if affected.intersection(node["depends_on"])
        }
        if expanded == affected:
            return [node["id"] for node in data["nodes"] if node["id"] in affected]
        affected = expanded


def _clear(node: dict[str, Any], *, reset_attempt: bool = False) -> None:
    node.update(status="pending", worker_id=None, assignment_id=None,
                input_versions={}, dependency_assignments={}, result=None)
    if reset_attempt:
        node["attempt"] = 0


def _matching_result(data: Run, result: dict[str, Any]) -> dict[str, Any]:
    node = _node(data, result["node_id"])
    require(node["status"] == "running", f"node is not running: {node['id']}")
    require(result["assignment_id"] == node["assignment_id"], "result assignment_id does not match current assignment")
    current_inputs = {key: data["source_versions"][key] for key in node["source_ids"]}
    require(result["source_versions"] == node["input_versions"] == current_inputs,
            "result source_versions do not match assigned/current inputs")
    dependencies = {key: _node(data, key)["assignment_id"] for key in node["depends_on"]}
    require(all(_node(data, key)["status"] == "done" for key in node["depends_on"]),
            "result dependencies are not done")
    require(result["dependency_assignments"] == node["dependency_assignments"] == dependencies,
            "result dependency_assignments do not match assigned/current dependencies")
    require({check["id"] for check in result["checks"]} == set(node["checks"]),
            "result must include exactly the required check IDs")
    return node


def _apply_event(data: Run, event: Event) -> None:
    """Apply one checked event in memory, also used to replay the audit trail."""
    _event_shape(event)
    require(event["revision"] == data["revision"] + 1, "history revisions must be consecutive from 2")
    require(data["status"] == "active", "run is cancelled")
    name = event["event"]
    if name == "assign":
        require(event["contract_digest"] == _contract_digest(data),
                "immutable run contract changed; restore it, cancel the run, and create a fresh run")
        node = _node(data, event["node_id"])
        require(node["status"] == "pending", f"node is not pending: {node['id']}")
        require(node["attempt"] < node["max_attempts"], "attempt budget exhausted")
        require(all(_node(data, key)["status"] == "done" for key in node["depends_on"]),
                "dependencies must be done before assignment")
        require(sum(row["status"] == "running" for row in data["nodes"]) < _limit(data),
                "no parallel slots available")
        require(not any(row["status"] == "running" and row["worker_id"] == event["worker_id"]
                        for row in data["nodes"]), "worker_id already has a running assignment")
        require(event["attempt"] == node["attempt"] + 1, "assignment attempt must increment by one")
        require(event["input_versions"] == {key: data["source_versions"][key] for key in node["source_ids"]},
                "assignment input_versions do not match current sources")
        require(event["dependency_assignments"] == {
            key: _node(data, key)["assignment_id"] for key in node["depends_on"]
        }, "assignment dependency snapshots do not match current dependencies")
        require(not any(row["event"] == "assign" and row["assignment_id"] == event["assignment_id"]
                        for row in data["history"]), "assignment_id has already been used")
        if node["id"] == data["review_node_id"] and data["execution_mode"] == "multi_agent":
            require(all(event["worker_id"] != row["worker_id"] for row in data["nodes"]
                        if row["id"] != node["id"] and row["status"] == "done"),
                    "final QC worker must differ from every completed worker")
        node.update(status="running", attempt=event["attempt"], worker_id=event["worker_id"],
                    assignment_id=event["assignment_id"], input_versions=deepcopy(event["input_versions"]),
                    dependency_assignments=deepcopy(event["dependency_assignments"]), result=None)
    elif name == "finish":
        result = event["result"]
        node = _matching_result(data, result)
        node["result"] = deepcopy(result)
        node["status"] = "done" if all(check["outcome"] == "pass" for check in result["checks"]) else "failed"
    elif name == "block":
        node = _node(data, event["node_id"])
        require(node["status"] in ("pending", "running"), "only pending or running nodes can be blocked")
        node["status"] = "blocked"
    elif name == "retry":
        node = _node(data, event["node_id"])
        require(node["status"] in ("failed", "blocked"), "only failed or blocked nodes can be retried")
        require(node["attempt"] < node["max_attempts"], "attempt budget exhausted")
        _clear(node)
    elif name == "invalidate":
        source_id = event["source_id"]
        require(source_id in data["source_versions"], f"unknown source: {source_id}")
        require(event["previous_version"] == data["source_versions"][source_id],
                "invalidation previous_version does not match")
        require(event["version"] != event["previous_version"], "invalidation must change source version")
        affected = _affected(data, source_id)
        require(event["node_ids"] == affected, "invalidation node_ids do not match affected descendants")
        require(not any(_node(data, key)["status"] == "running" for key in affected),
                "cannot invalidate while an affected worker is running; block or cancel first")
        data["source_versions"][source_id] = event["version"]
        for node_id in affected:
            _clear(_node(data, node_id), reset_attempt=True)
    elif name == "cancel":
        outstanding = [row["id"] for row in data["nodes"] if row["status"] not in ("done", "cancelled")]
        require(event["node_ids"] == outstanding, "cancel node_ids do not match outstanding nodes")
        for node_id in outstanding:
            _node(data, node_id)["status"] = "cancelled"
        data["status"] = "cancelled"
    data["revision"] = event["revision"]
    data["history"].append(deepcopy(event))


def validate(value: object) -> Run:
    """Validate schema, DAG, permissions, paths, audit replay, and mode-specific QC.

    Paths are resolved locally relative to the current directory, including existing
    symlinks; absolute write targets are recommended for portable run files. Evidence
    is required as text, but this function does not inspect the referenced artifacts.
    Once assigned, static contracts are immutable in place: cancel the valid run
    and start a fresh run to replace locks, permissions, goals, checks, or the DAG.
    """
    keys = _RUN_KEYS | {"completion_contract"} if isinstance(value, dict) and "completion_contract" in value else _RUN_KEYS
    data = _object(value, keys, "run")
    require(type(data["schema_version"]) is int and data["schema_version"] == 1, "unsupported schema_version")
    _integer(data["revision"], "revision", 1)
    for key in ("run_id", "objective", "review_node_id"):
        _text(data[key], key)
    require(data["layer"] == "harness", "layer must be harness")
    require(data["canonical_writer"] == "daksh", "canonical_writer must be daksh")
    require(data["execution_mode"] in ("multi_agent", "sequential_skills"), "invalid execution_mode")
    if "completion_contract" in data:
        contract = _object(data["completion_contract"], _COMPLETION_KEYS, "completion_contract")
        require(contract["required_node_status"] == "done", "required_node_status must be done")
        require(contract["required_check_outcome"] == "pass", "required_check_outcome must be pass")
        require(type(contract["unresolved_blockers"]) is int and contract["unresolved_blockers"] == 0,
                "unresolved_blockers must be 0")
        for key in ("current_source_snapshots", "observed_delivery_or_save"):
            require(contract[key] is True, f"completion_contract.{key} must be true")
        require(type(contract["independent_final_review"]) is bool, "independent_final_review must be boolean")
        require(data["execution_mode"] != "sequential_skills" or not contract["independent_final_review"],
                "sequential_skills cannot satisfy independent_final_review=true")
    require(data["status"] in ("active", "cancelled"), "invalid run status")
    _integer(data["max_parallel"], "max_parallel", 1, 6)
    permissions = set(_texts(data["permissions"], "permissions"))
    sources = _versions(data["source_versions"], "source_versions")
    require(isinstance(data["locks"], list), "locks must be a list")
    lock_ids = []
    for lock in data["locks"]:
        _object(lock, {"id", "scope", "value"}, "lock")
        for key in ("id", "scope", "value"):
            _text(lock[key], f"lock.{key}")
        lock_ids.append(lock["id"])
    require(len(set(lock_ids)) == len(lock_ids), "duplicate lock id")
    require(isinstance(data["nodes"], list) and bool(data["nodes"]), "nodes must be a nonempty list")
    node_ids: set[str] = set()
    targets: list[tuple[str, str]] = []
    for node in data["nodes"]:
        _object(node, _NODE_KEYS, "node")
        for key in ("id", "role", "goal"):
            _text(node[key], f"node.{key}")
        require(node["id"] not in node_ids, f"duplicate node id: {node['id']}")
        node_ids.add(node["id"])
        for key in ("depends_on", "source_ids", "permissions", "write_targets", "checks"):
            _texts(node[key], f"{node['id']}.{key}")
        require(bool(node["checks"]), f"checks must be nonempty: {node['id']}")
        require(set(node["permissions"]) <= permissions, f"permission escalation: {node['id']}")
        require(set(node["source_ids"]) <= set(sources), f"unknown source reference: {node['id']}")
        require(node["status"] in STATES, f"invalid node status: {node['id']}")
        _integer(node["max_attempts"], f"{node['id']}.max_attempts", 1, 3)
        _integer(node["attempt"], f"{node['id']}.attempt", 0, node["max_attempts"])
        for key in ("worker_id", "assignment_id"):
            if node[key] is not None:
                _text(node[key], f"{node['id']}.{key}")
        require((node["worker_id"] is None) == (node["assignment_id"] is None), "worker_id and assignment_id must both be set or null")
        _versions(node["input_versions"], f"{node['id']}.input_versions")
        _versions(node["dependency_assignments"], f"{node['id']}.dependency_assignments")
        if node["result"] is not None:
            _result_shape(node["result"])
        for target in node["write_targets"]:
            require("\0" not in target, "write_targets cannot contain NUL")
            require("://" not in target, "write_targets must be local filesystem paths, not URLs")
            resolved = os.path.realpath(target)
            for owner, other in targets:
                require(os.path.commonpath((resolved, other)) not in (resolved, other),
                        f"overlapping write targets: {owner} and {node['id']}")
            targets.append((node["id"], resolved))
    by_id = _nodes(data)
    for node in data["nodes"]:
        require(set(node["depends_on"]) <= node_ids, f"unknown dependency: {node['id']}")
    # Kahn's algorithm handles long graphs without recursive traversal limits.
    indegree = {key: len(row["depends_on"]) for key, row in by_id.items()}
    children: dict[str, list[str]] = {key: [] for key in by_id}
    for node in data["nodes"]:
        for parent in node["depends_on"]:
            children[parent].append(node["id"])
    queue = [key for key, degree in indegree.items() if degree == 0]
    visited = 0
    for key in queue:
        visited += 1
        for child in children[key]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    require(visited == len(by_id), "dependency cycle detected")
    review_id = data["review_node_id"]
    require(review_id in by_id and by_id[review_id]["role"] == "qc", "review_node_id must reference a qc node")
    ancestors: set[str] = set()
    pending = list(by_id[review_id]["depends_on"])
    while pending:
        key = pending.pop()
        if key not in ancestors:
            ancestors.add(key)
            pending.extend(by_id[key]["depends_on"])
    require(ancestors == node_ids - {review_id}, "final QC must depend transitively on every other node")
    require(isinstance(data["history"], list), "history must be a list")
    for event in data["history"]:
        _event_shape(event)
    require(len(data["history"]) == data["revision"] - 1, "revision must equal one plus the history length")
    replay = deepcopy(data)
    replay.update(revision=1, status="active", history=[])
    for node in replay["nodes"]:
        _clear(node, reset_attempt=True)
    # Recover initial source versions, then replay every transition and snapshot.
    for event in reversed(data["history"]):
        if event["event"] == "invalidate":
            key = event["source_id"]
            require(key in replay["source_versions"], f"unknown historical source: {key}")
            require(replay["source_versions"][key] == event["version"], "source version history is inconsistent")
            replay["source_versions"][key] = event["previous_version"]
    for event in data["history"]:
        _apply_event(replay, event)
    require(replay["status"] == data["status"], "run status does not match history")
    require(replay["source_versions"] == sources, "source_versions do not match history")
    for actual, rebuilt in zip(data["nodes"], replay["nodes"]):
        require(all(actual[key] == rebuilt[key] for key in _DYNAMIC_KEYS),
                f"node state does not match recorded assignments/results: {actual['id']}")
    return data


def _json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value: str) -> Any:
    raise BrainError(f"non-finite JSON value: {value}")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_json_object, parse_constant=_constant)


def load(path: Path) -> Run:
    """Read strict UTF-8 JSON and validate the complete local ledger."""
    return validate(_read_json(path))


def _ready(data: Run) -> list[str]:
    if data["status"] != "active":
        return []
    by_id = _nodes(data)
    return [row["id"] for row in data["nodes"] if row["status"] == "pending"
            and row["attempt"] < row["max_attempts"]
            and all(by_id[key]["status"] == "done" for key in row["depends_on"])]


def ready(data: Run) -> list[str]:
    """List dependency-ready pending nodes in declaration order; capacity is separate."""
    return _ready(validate(data))


def summary(data: Run) -> dict[str, Any]:
    """Return compact scheduler state, with completion gated on all nodes and QC."""
    validate(data)
    counts = Counter(row["status"] for row in data["nodes"])
    running = [row["id"] for row in data["nodes"] if row["status"] == "running"]
    return {
        "schema_version": 1, "run_id": data["run_id"], "revision": data["revision"],
        "status": data["status"], "execution_mode": data["execution_mode"],
        "max_parallel": data["max_parallel"], "parallel_limit": _limit(data),
        "available_slots": max(0, _limit(data) - len(running)) if data["status"] == "active" else 0,
        "running": running, "ready": _ready(data),
        "counts": {key: counts[key] for key in STATES}, "review_node_id": data["review_node_id"],
        "review_mode": "independent_review" if data["execution_mode"] == "multi_agent" else "self_review",
        "independent_review": data["execution_mode"] == "multi_agent"
                              and _node(data, data["review_node_id"])["status"] == "done",
        "complete": data["status"] == "active" and counts["done"] == len(data["nodes"]),
    }


def _revision(data: Run, expected_revision: int) -> None:
    _integer(expected_revision, "expected_revision", 1)
    require(data["revision"] == expected_revision,
            f"revision conflict: expected {expected_revision}, actual {data['revision']}")


def _mutate(path: Path, expected_revision: int,
            build: Callable[[Run], Event | None]) -> tuple[Run, bool]:
    path = path.resolve()
    with locked(path):
        data = load(path)
        _revision(data, expected_revision)
        event = build(data)
        if event is None:
            return data, False
        _apply_event(data, event)
        validate(data)
        atomic_write(path, data)
        return data, True


def assign(path: Path, node_id: str, worker: str, expected_revision: int) -> tuple[Run, bool]:
    """Record an assignment UUID, contract digest, and source/dependency snapshots.

    This grants no tools or permissions and starts no worker. Attempt budgets,
    dependency completion, independent final QC identity, and capacity are enforced.
    """
    _text(worker, "worker")

    def build(data: Run) -> Event:
        node = _node(data, node_id)
        return {
            "event": "assign", "revision": data["revision"] + 1, "node_id": node_id,
            "worker_id": worker, "assignment_id": str(uuid4()), "attempt": node["attempt"] + 1,
            "contract_digest": _contract_digest(data),
            "input_versions": {key: data["source_versions"][key] for key in node["source_ids"]},
            "dependency_assignments": {key: _node(data, key)["assignment_id"] for key in node["depends_on"]},
        }

    return _mutate(path, expected_revision, build)


def finish(path: Path, result: object, expected_revision: int) -> tuple[Run, bool]:
    """Accept a current assignment's result; only all-pass evidence marks it done.

    An identical current done/failed result is a no-op even with a stale expected
    revision. Retried, invalidated, and cancelled outstanding assignments are rejected.
    """
    result = deepcopy(_result_shape(result))
    _integer(expected_revision, "expected_revision", 1)
    path = path.resolve()
    with locked(path):
        data = load(path)
        node = _node(data, result["node_id"])
        if node["status"] in ("done", "failed") and node["result"] == result:
            return data, False
        _revision(data, expected_revision)
        _apply_event(data, {"event": "finish", "revision": data["revision"] + 1, "result": result})
        validate(data)
        atomic_write(path, data)
        return data, True


def block(path: Path, node_id: str, reason: str, expected_revision: int) -> tuple[Run, bool]:
    """Block a pending/running node, recording a reason and releasing its slot."""
    _text(reason, "reason")
    return _mutate(path, expected_revision, lambda data: {
        "event": "block", "revision": data["revision"] + 1, "node_id": node_id, "reason": reason,
    })


def retry(path: Path, node_id: str, expected_revision: int) -> tuple[Run, bool]:
    """Reset a failed/blocked node to pending without exceeding its attempt budget."""
    return _mutate(path, expected_revision, lambda data: {
        "event": "retry", "revision": data["revision"] + 1, "node_id": node_id,
    })


def invalidate(path: Path, source_id: str, version: str, expected_revision: int) -> tuple[Run, bool]:
    """Update one source, resetting readers/descendants and their attempt budgets.

    Running affected assignments must be explicitly blocked first. A same-version
    update is a no-op after checking the expected revision. Old evidence remains in
    history, while old assignment results can no longer satisfy the reset nodes.
    """
    _text(version, "version")

    def build(data: Run) -> Event | None:
        require(data["status"] == "active", "run is cancelled")
        require(source_id in data["source_versions"], f"unknown source: {source_id}")
        previous = data["source_versions"][source_id]
        if previous == version:
            return None
        return {
            "event": "invalidate", "revision": data["revision"] + 1,
            "source_id": source_id, "previous_version": previous, "version": version,
            "node_ids": _affected(data, source_id),
        }

    return _mutate(path, expected_revision, build)


def cancel(path: Path, reason: str, expected_revision: int) -> tuple[Run, bool]:
    """Cancel the run and all outstanding nodes while retaining completed evidence."""
    _text(reason, "reason")
    return _mutate(path, expected_revision, lambda data: {
        "event": "cancel", "revision": data["revision"] + 1, "reason": reason,
        "node_ids": [row["id"] for row in data["nodes"] if row["status"] not in ("done", "cancelled")],
    })


def main(argv: Sequence[str] | None = None) -> int:
    """Run the local CLI with JSON summaries and exit 2 for rejected operations."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "ready", "summary", "assign", "finish", "block", "retry", "invalidate", "cancel"):
        command = commands.add_parser(name)
        command.add_argument("run", type=Path)
        if name in ("assign", "block", "retry"):
            command.add_argument("node")
        if name == "assign":
            command.add_argument("--worker", required=True)
        elif name == "finish":
            command.add_argument("result", type=Path)
        elif name == "invalidate":
            command.add_argument("--source", required=True)
            command.add_argument("--version", required=True)
        if name in ("block", "cancel"):
            command.add_argument("--reason", required=True)
        if name not in ("validate", "ready", "summary"):
            command.add_argument("--expected-revision", type=int, required=True)
    args = parser.parse_args(argv)
    try:
        changed: bool | None = None
        if args.command in ("validate", "ready", "summary"):
            data = load(args.run)
        elif args.command == "assign":
            data, changed = assign(args.run, args.node, args.worker, args.expected_revision)
        elif args.command == "finish":
            data, changed = finish(args.run, _read_json(args.result), args.expected_revision)
        elif args.command == "block":
            data, changed = block(args.run, args.node, args.reason, args.expected_revision)
        elif args.command == "retry":
            data, changed = retry(args.run, args.node, args.expected_revision)
        elif args.command == "invalidate":
            data, changed = invalidate(args.run, args.source, args.version, args.expected_revision)
        else:
            data, changed = cancel(args.run, args.reason, args.expected_revision)
        output = summary(data)
        if changed is not None:
            output["changed"] = changed
        if args.command == "assign":
            node = _node(data, args.node)
            output["assignment"] = {
                "node_id": node["id"], "worker_id": node["worker_id"], "assignment_id": node["assignment_id"],
                "attempt": node["attempt"], "input_versions": node["input_versions"],
                "dependency_assignments": node["dependency_assignments"],
                "contract_digest": _contract_digest(data),
            }
        print(json.dumps(output, ensure_ascii=False, separators=(",", ":")))
        return 0
    except (BrainError, OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        print(f"Daksh run error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
