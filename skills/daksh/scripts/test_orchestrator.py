#!/usr/bin/env python3
"""Exercise the local ledger with temporary files, never real workers or apps."""

from __future__ import annotations

from copy import deepcopy
import errno
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Callable
import unittest
from uuid import UUID

import orchestrator as controller
from brain import BrainError


def fixture(root: Path) -> dict[str, Any]:
    """Build a small two-branch DAG with an independent final review."""
    def node(identity: str, depends_on: list[str], sources: list[str]) -> dict[str, Any]:
        return {
            "id": identity, "role": "qc" if identity == "qc" else identity,
            "goal": f"Produce evidence for {identity}", "depends_on": depends_on,
            "source_ids": sources, "permissions": ["read"],
            "write_targets": [str(root / f"{identity}.artifact.json")],
            "checks": ["fidelity", "scope"] if identity != "qc" else ["review"],
            "status": "pending", "attempt": 0, "max_attempts": 2,
            "worker_id": None, "assignment_id": None, "input_versions": {},
            "dependency_assignments": {}, "result": None,
        }

    return {
        "schema_version": 1, "run_id": "test-run", "revision": 1,
        "objective": "Produce two checked artifacts and an independent review",
        "layer": "harness", "execution_mode": "multi_agent", "status": "active",
        "canonical_writer": "daksh", "max_parallel": 2, "permissions": ["read"],
        "source_versions": {"brief": "v1", "market": "m1", "unused": "u1"},
        "locks": [{"id": "dialogue", "scope": "task", "value": "Exact approved words"}],
        "history": [], "review_node_id": "qc",
        "nodes": [node("research", [], ["brief"]), node("business", [], ["market"]),
                  node("qc", ["research", "business"], [])],
    }


class OrchestratorTests(unittest.TestCase):
    """Verify state transitions, provenance rejection, atomicity, and the actual CLI."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.path = self.root / "run.json"
        self.write(fixture(self.root))

    def write(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def read(self) -> dict[str, Any]:
        return controller.load(self.path)

    def node(self, identity: str) -> dict[str, Any]:
        return next(node for node in self.read()["nodes"] if node["id"] == identity)

    def result(self, identity: str, outcome: str = "pass") -> dict[str, Any]:
        node = self.node(identity)
        return {
            "node_id": identity, "assignment_id": node["assignment_id"],
            "source_versions": deepcopy(node["input_versions"]),
            "dependency_assignments": deepcopy(node["dependency_assignments"]),
            "artifacts": [f"artifact://test/{identity}/{node['assignment_id']}"],
            "checks": [{"id": check, "outcome": outcome, "evidence": f"Observed {check}: {outcome}"}
                       for check in node["checks"]],
        }

    def assign(self, identity: str, worker: str | None = None) -> dict[str, Any]:
        data, changed = controller.assign(self.path, identity, worker or f"worker-{identity}", self.read()["revision"])
        self.assertTrue(changed)
        return data

    def done(self, identity: str, worker: str | None = None) -> dict[str, Any]:
        self.assign(identity, worker)
        result = self.result(identity)
        data, changed = controller.finish(self.path, result, self.read()["revision"])
        self.assertTrue(changed)
        self.assertEqual(next(row for row in data["nodes"] if row["id"] == identity)["status"], "done")
        return result

    def rejected(self, operation: Callable[[], object], pattern: str = ".*") -> None:
        before = self.path.read_bytes()
        with self.assertRaisesRegex(BrainError, pattern):
            operation()
        self.assertEqual(self.path.read_bytes(), before, "rejection must preserve exact ledger bytes")

    def cli(self, *arguments: str, success: bool = True) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run([sys.executable, str(Path(controller.__file__)), *arguments],
                                   capture_output=True, text=True, timeout=10)
        self.assertEqual(completed.returncode, 0 if success else 2, completed.stderr)
        if success:
            json.loads(completed.stdout)
        return completed

    def test_initial_schema_readiness_and_no_read_side_effects(self) -> None:
        before = self.path.read_bytes()
        data = self.read()
        self.assertEqual(controller.ready(data), ["research", "business"])
        overview = controller.summary(data)
        self.assertEqual(overview["available_slots"], 2)
        self.assertFalse(overview["complete"])
        self.cli("validate", str(self.path))
        self.cli("ready", str(self.path))
        self.assertEqual(self.path.read_bytes(), before)

    def test_schema_graph_permissions_and_review_rejections(self) -> None:
        cases: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
            ("duplicate id", lambda run: run["nodes"][1].update(id="research")),
            ("unknown dependency", lambda run: run["nodes"][0].update(depends_on=["missing"])),
            ("cycle", lambda run: run["nodes"][0].update(depends_on=["qc"])),
            ("permission escalation", lambda run: run["nodes"][0].update(permissions=["send_mail"])),
            ("unknown source", lambda run: run["nodes"][0].update(source_ids=["missing"])),
            ("empty checks", lambda run: run["nodes"][0].update(checks=[])),
            ("duplicate checks", lambda run: run["nodes"][0].update(checks=["x", "x"])),
            ("wrong reviewer", lambda run: run.update(review_node_id="research")),
            ("missing reviewer", lambda run: run.update(review_node_id="missing")),
            ("review misses branch", lambda run: run["nodes"][2].update(depends_on=["research"])),
            ("boolean revision", lambda run: run.update(revision=True)),
            ("boolean schema", lambda run: run.update(schema_version=True)),
            ("too many workers", lambda run: run.update(max_parallel=7)),
            ("zero workers", lambda run: run.update(max_parallel=0)),
            ("unbounded retry", lambda run: run["nodes"][0].update(max_attempts=4)),
            ("unknown fields", lambda run: run.update(tool_calls=[])),
            ("duplicate lock", lambda run: run["locks"].append(deepcopy(run["locks"][0]))),
            ("empty lock", lambda run: run["locks"][0].update(value=" ")),
        ]
        initial = self.read()
        for label, change in cases:
            with self.subTest(label=label):
                changed = deepcopy(initial)
                change(changed)
                with self.assertRaises(BrainError):
                    controller.validate(changed)

    def test_overlapping_paths_include_ancestors_aliases_and_symlinks(self) -> None:
        initial = self.read()
        same = initial["nodes"][0]["write_targets"][0]
        aliases = [same, same + "/child", str(self.root / "subdir" / ".." / Path(same).name)]
        real = self.root / "real"
        real.mkdir()
        link = self.root / "link"
        link.symlink_to(real, target_is_directory=True)
        for target in aliases:
            with self.subTest(target=target):
                run = deepcopy(initial)
                run["nodes"][1]["write_targets"] = [target]
                with self.assertRaisesRegex(BrainError, "overlapping"):
                    controller.validate(run)
        run = deepcopy(initial)
        run["nodes"][0]["write_targets"] = [str(real)]
        run["nodes"][1]["write_targets"] = [str(link / "file")]
        with self.assertRaisesRegex(BrainError, "overlapping"):
            controller.validate(run)
        # A lexical prefix alone is not an ancestor, and read-only targets are valid.
        run["nodes"][1]["write_targets"] = [str(self.root / "really")]
        run["nodes"][2]["write_targets"] = []
        controller.validate(run)

    def test_assignment_snapshots_uuid_capacity_and_pinned_locks(self) -> None:
        locks = deepcopy(self.read()["locks"])
        data = self.assign("research")
        research = self.node("research")
        self.assertEqual(str(UUID(research["assignment_id"])), research["assignment_id"])
        self.assertEqual(research["input_versions"], {"brief": "v1"})
        self.assertEqual(research["dependency_assignments"], {})
        self.assertEqual((research["attempt"], data["revision"]), (1, 2))
        self.assign("business")
        self.assertEqual(controller.summary(self.read())["available_slots"], 0)
        self.rejected(lambda: controller.assign(self.path, "qc", "reviewer", 3))
        self.assertEqual(self.read()["locks"], locks)
        self.assertEqual([row["event"] for row in self.read()["history"]], ["assign", "assign"])

    def test_capacity_and_sequential_fallback_are_enforced(self) -> None:
        for mode, cap in (("multi_agent", 1), ("sequential_skills", 6)):
            with self.subTest(mode=mode):
                run = fixture(self.root)
                run.update(execution_mode=mode, max_parallel=cap)
                self.write(run)
                self.assign("research")
                self.assertEqual(controller.summary(self.read())["parallel_limit"], 1)
                self.rejected(lambda: controller.assign(self.path, "business", "worker-b", 2), "slots")

    def test_one_worker_cannot_hold_two_running_assignments(self) -> None:
        self.assign("research", "actual-worker")
        self.rejected(lambda: controller.assign(self.path, "business", "actual-worker", 2), "already has a running")
        controller.finish(self.path, self.result("research"), 2)
        self.assign("business", "actual-worker")
        self.assertEqual(self.node("business")["worker_id"], "actual-worker")

    def test_sequential_fallback_uses_honest_same_worker_self_review(self) -> None:
        run = self.read()
        run["execution_mode"] = "sequential_skills"
        self.write(run)
        self.done("research", "actual-controller")
        self.done("business", "actual-controller")
        self.done("qc", "actual-controller")
        status = controller.summary(self.read())
        self.assertTrue(status["complete"])
        self.assertEqual(status["review_mode"], "self_review")
        self.assertFalse(status["independent_review"])

    def test_optional_completion_requirements_and_shipped_template(self) -> None:
        template = Path(controller.__file__).resolve().parent.parent / "assets" / "run.template.json"
        controller.load(template)
        contract = {
            "required_node_status": "done", "required_check_outcome": "pass", "unresolved_blockers": 0,
            "current_source_snapshots": True, "independent_final_review": True,
            "observed_delivery_or_save": True,
        }
        run = self.read()
        run["completion_contract"] = contract
        controller.validate(run)
        run["execution_mode"] = "sequential_skills"
        with self.assertRaisesRegex(BrainError, "cannot satisfy"):
            controller.validate(run)
        contract["independent_final_review"] = False
        controller.validate(run)
        for key, value in (("required_check_outcome", "reported"), ("unresolved_blockers", False),
                           ("observed_delivery_or_save", False), ("independent_final_review", "yes")):
            with self.subTest(key=key):
                invalid = deepcopy(run)
                invalid["completion_contract"][key] = value
                with self.assertRaises(BrainError):
                    controller.validate(invalid)

    def test_stale_revision_rejections_preserve_exact_bytes(self) -> None:
        self.assign("research")
        operations = [
            lambda: controller.assign(self.path, "business", "worker-b", 1),
            lambda: controller.finish(self.path, self.result("research"), 1),
            lambda: controller.block(self.path, "research", "waiting", 1),
            lambda: controller.retry(self.path, "research", 1),
            lambda: controller.invalidate(self.path, "brief", "v2", 1),
            lambda: controller.cancel(self.path, "stop", 1),
        ]
        for operation in operations:
            self.rejected(operation, "revision conflict")

    def test_finish_is_evidence_gated_and_idempotent_with_stale_revision(self) -> None:
        self.assign("research")
        result = self.result("research")
        data, changed = controller.finish(self.path, result, 2)
        self.assertTrue(changed)
        self.assertEqual(data["revision"], 3)
        self.assertEqual(self.node("research")["status"], "done")
        before = self.path.read_bytes()
        repeated, changed = controller.finish(self.path, deepcopy(result), 1)
        self.assertFalse(changed)
        self.assertEqual(repeated["revision"], 3)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertFalse(controller.summary(data)["complete"])

    def test_forged_or_incomplete_results_are_rejected_without_writing(self) -> None:
        self.assign("research")
        original = self.result("research")
        cases: list[Callable[[dict[str, Any]], None]] = [
            lambda result: result.update(node_id="unknown"),
            lambda result: result.update(assignment_id="old-worker-token"),
            lambda result: result.update(source_versions={"brief": "stale"}),
            lambda result: result.update(source_versions={"brief": "v1", "unused": "u1"}),
            lambda result: result.update(dependency_assignments={"business": "fake"}),
            lambda result: result.update(artifacts=[]),
            lambda result: result.update(artifacts=[" "]),
            lambda result: result["checks"].pop(),
            lambda result: result["checks"].append(deepcopy(result["checks"][0])),
            lambda result: result["checks"][0].update(id="unrequested_check"),
            lambda result: result["checks"][0].update(outcome="reported_pass"),
            lambda result: result["checks"][0].update(evidence=" "),
            lambda result: result.update(tool_calls=[{"command": "anything"}]),
        ]
        for index, change in enumerate(cases):
            with self.subTest(index=index):
                result = deepcopy(original)
                change(result)
                self.rejected(lambda: controller.finish(self.path, result, 2))

    def test_failed_results_retry_once_and_exhaust_attempt_budget(self) -> None:
        for outcome in ("fail", "not_run"):
            with self.subTest(outcome=outcome):
                self.write(fixture(self.root))
                self.assign("research")
                result = self.result("research", outcome)
                data, _ = controller.finish(self.path, result, 2)
                self.assertEqual(self.node("research")["status"], "failed")
                self.assertFalse(controller.finish(self.path, result, 1)[1])
                data, _ = controller.retry(self.path, "research", data["revision"])
                self.assertEqual(self.node("research")["status"], "pending")
                self.assertIsNone(self.node("research")["assignment_id"])
                self.assign("research")
                self.assertEqual(self.node("research")["attempt"], 2)
                self.rejected(lambda: controller.finish(self.path, result, self.read()["revision"]), "assignment")
                controller.finish(self.path, self.result("research", outcome), self.read()["revision"])
                self.rejected(lambda: controller.retry(self.path, "research", self.read()["revision"]), "budget")

    def test_block_releases_slots_and_retry_rejects_old_worker(self) -> None:
        self.assign("research")
        old_result = self.result("research")
        controller.block(self.path, "research", "Need raw source", 2)
        self.assertEqual(controller.summary(self.read())["available_slots"], 2)
        self.rejected(lambda: controller.finish(self.path, old_result, 3), "not running")
        controller.retry(self.path, "research", 3)
        self.assign("research", "replacement-worker")
        self.rejected(lambda: controller.finish(self.path, old_result, 5), "assignment")
        # A pending block does not consume a worker attempt.
        controller.block(self.path, "business", "Waiting for approval", 5)
        controller.retry(self.path, "business", 6)
        self.assertEqual(self.node("business")["attempt"], 0)
        self.assertTrue(any(row.get("reason") == "Need raw source" for row in self.read()["history"]))

    def test_final_qc_is_transitive_independent_and_gates_completion(self) -> None:
        research_result = self.done("research", "producer")
        self.done("business", "producer")
        self.assertEqual(controller.ready(self.read()), ["qc"])
        self.assertFalse(controller.summary(self.read())["complete"])
        self.rejected(lambda: controller.assign(self.path, "qc", "producer", 5), "QC worker")
        self.assign("qc", "fresh-reviewer")
        qc = self.node("qc")
        self.assertEqual(qc["dependency_assignments"]["research"], research_result["assignment_id"])
        result = self.result("qc")
        forged = deepcopy(result)
        forged["dependency_assignments"]["research"] = "different-producer-assignment"
        self.rejected(lambda: controller.finish(self.path, forged, 6), "dependency_assignments")
        controller.finish(self.path, result, 6)
        self.assertTrue(controller.summary(self.read())["complete"])
        self.assertEqual(controller.ready(self.read()), [])

    def test_invalidation_resets_readers_and_descendants_preserving_history(self) -> None:
        original = self.done("research")
        self.done("business")
        self.done("qc", "independent-reviewer")
        before = deepcopy(self.read())
        data, changed = controller.invalidate(self.path, "brief", "v2", before["revision"])
        self.assertTrue(changed)
        self.assertEqual(data["history"][:-1], before["history"])
        self.assertEqual(data["history"][-1]["node_ids"], ["research", "qc"])
        self.assertEqual(self.node("business"), before["nodes"][1])
        for identity in ("research", "qc"):
            node = self.node(identity)
            self.assertEqual((node["status"], node["attempt"]), ("pending", 0))
            self.assertIsNone(node["result"])
            self.assertIsNone(node["assignment_id"])
            self.assertEqual(node["input_versions"], {})
        self.assertFalse(controller.summary(data)["complete"])
        self.rejected(lambda: controller.finish(self.path, original, data["revision"]), "not running")
        self.assign("research", "new-source-worker")
        self.assertEqual(self.node("research")["input_versions"], {"brief": "v2"})
        self.rejected(lambda: controller.finish(self.path, original, self.read()["revision"]), "assignment")
        self.assertEqual(self.read()["locks"], before["locks"])

    def test_invalidation_rejects_affected_running_workers_but_allows_unrelated(self) -> None:
        self.done("research")
        self.done("business")
        self.assign("qc", "reviewer")
        self.rejected(lambda: controller.invalidate(self.path, "brief", "v2", 6), "affected worker")
        controller.block(self.path, "qc", "Inputs changing", 6)
        controller.invalidate(self.path, "brief", "v2", 7)
        self.assertEqual(self.node("qc")["status"], "pending")
        self.write(fixture(self.root))
        self.assign("business")
        controller.invalidate(self.path, "brief", "v2", 2)
        self.assertEqual(self.node("business")["status"], "running")
        self.assertEqual(self.node("business")["input_versions"], {"market": "m1"})
        before = self.path.read_bytes()
        data, changed = controller.invalidate(self.path, "brief", "v2", 3)
        self.assertFalse(changed)
        self.assertEqual(data["revision"], 3)
        self.assertEqual(self.path.read_bytes(), before)
        self.rejected(lambda: controller.invalidate(self.path, "brief", "v2", 1), "revision conflict")
        self.rejected(lambda: controller.invalidate(self.path, "missing", "v1", 3), "unknown source")

    def test_cancel_outstanding_nodes_retains_completed_evidence(self) -> None:
        completed = self.done("research")
        self.assign("business")
        old_result = self.result("business")
        data, _ = controller.cancel(self.path, "User cancelled task", 4)
        self.assertEqual(data["status"], "cancelled")
        self.assertEqual(self.node("research")["status"], "done")
        self.assertEqual(self.node("research")["result"], completed)
        self.assertEqual(self.node("business")["status"], "cancelled")
        self.assertEqual(self.node("qc")["status"], "cancelled")
        self.assertEqual(controller.ready(data), [])
        self.assertEqual(controller.summary(data)["available_slots"], 0)
        self.assertFalse(controller.summary(data)["complete"])
        self.rejected(lambda: controller.finish(self.path, old_result, 5), "cancelled")
        self.rejected(lambda: controller.assign(self.path, "business", "new", 5), "cancelled")
        self.rejected(lambda: controller.retry(self.path, "business", 5), "cancelled")
        self.rejected(lambda: controller.invalidate(self.path, "brief", "v2", 5), "cancelled")
        # An already completed current assignment still has an idempotent receipt.
        self.assertFalse(controller.finish(self.path, completed, 1)[1])

    def test_current_state_must_match_recorded_assignment_and_result_history(self) -> None:
        self.done("research")
        valid = self.read()
        cases: list[Callable[[dict[str, Any]], None]] = [
            lambda run: run["nodes"][0].update(worker_id="unrecorded-worker"),
            lambda run: run["nodes"][0].update(input_versions={"brief": "v0"}),
            lambda run: run["nodes"][0]["result"]["checks"][0].update(evidence="different"),
            lambda run: run["history"][0].update(input_versions={"brief": "v0"}),
            lambda run: run["history"][1].update(revision=99),
            lambda run: run.update(history=[]),
            lambda run: run.update(revision=1),
            lambda run: run["nodes"][2].update(status="done"),
        ]
        for index, change in enumerate(cases):
            with self.subTest(index=index):
                tampered = deepcopy(valid)
                change(tampered)
                with self.assertRaises(BrainError):
                    controller.validate(tampered)

    def test_changed_lock_rejects_running_results_and_done_receipt_retries(self) -> None:
        self.assign("research")
        result = self.result("research")
        result_path = self.root / "lock-result.json"
        result_path.write_text(json.dumps(result), encoding="utf-8")
        original = self.read()
        tampered = deepcopy(original)
        tampered["locks"][0]["value"] = "Different dialogue contract"
        self.write(tampered)
        self.rejected(lambda: controller.load(self.path), "immutable run contract changed")
        self.rejected(lambda: controller.finish(self.path, result, 2), "immutable run contract changed")
        before = self.path.read_bytes()
        error = self.cli("finish", str(self.path), str(result_path),
                         "--expected-revision", "2", success=False)
        self.assertIn("immutable run contract changed", error.stderr)
        self.assertEqual(self.path.read_bytes(), before)
        self.write(original)
        controller.finish(self.path, result, 2)
        completed = self.read()
        completed["locks"][0]["value"] = "A post-completion contract change"
        self.write(completed)
        self.rejected(lambda: controller.finish(self.path, result, 1), "immutable run contract changed")

    def test_removing_required_check_cannot_weaken_an_assigned_contract(self) -> None:
        self.assign("research")
        result = self.result("research")
        tampered = self.read()
        tampered["nodes"][0]["checks"].remove("scope")
        result["checks"] = [check for check in result["checks"] if check["id"] != "scope"]
        self.write(tampered)
        self.rejected(lambda: controller.load(self.path), "immutable run contract changed")
        self.rejected(lambda: controller.finish(self.path, result, 2), "immutable run contract changed")

    def test_assignments_pin_other_static_contract_definitions(self) -> None:
        self.assign("research")
        result = self.result("research")
        original = self.read()
        changes: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
            ("node permission", lambda run: run["nodes"][0].update(permissions=[])),
            ("run permission", lambda run: run.update(permissions=["read", "send"])),
            ("role", lambda run: run["nodes"][0].update(role="different-specialist")),
            ("goal", lambda run: run["nodes"][0].update(goal="A different authorized goal")),
            ("objective", lambda run: run.update(objective="A replacement run objective")),
            ("identity", lambda run: run.update(run_id="different-run")),
            ("mode", lambda run: run.update(execution_mode="sequential_skills")),
            ("capacity", lambda run: run.update(max_parallel=3)),
            ("retry budget", lambda run: run["nodes"][0].update(max_attempts=3)),
            ("source set", lambda run: run["source_versions"].update(new_source="n1")),
            ("node source set", lambda run: run["nodes"][0].update(source_ids=["brief", "unused"])),
            ("dependency set", lambda run: run["nodes"][0].update(depends_on=["business"])),
            ("write path", lambda run: run["nodes"][0].update(write_targets=[str(self.root / "new-output")])),
            ("other node", lambda run: run["nodes"][1].update(goal="A changed sibling contract")),
            ("completion requirements", lambda run: run.update(completion_contract={
                "required_node_status": "done", "required_check_outcome": "pass", "unresolved_blockers": 0,
                "current_source_snapshots": True, "independent_final_review": True,
                "observed_delivery_or_save": True,
            })),
        ]
        for label, change in changes:
            with self.subTest(label=label):
                tampered = deepcopy(original)
                change(tampered)
                self.write(tampered)
                self.rejected(lambda: controller.load(self.path), "immutable run contract changed")
                self.rejected(lambda: controller.finish(self.path, result, 2), "immutable run contract changed")

    def test_contract_digest_is_required_recorded_and_recomputed(self) -> None:
        response = self.cli("assign", str(self.path), "research", "--worker", "worker-r", "--expected-revision", "1")
        original = self.read()
        recorded = original["history"][0]["contract_digest"]
        self.assertEqual(len(recorded), 64)
        self.assertEqual(json.loads(response.stdout)["assignment"]["contract_digest"], recorded)
        for kind in ("missing", "malformed", "mismatched"):
            with self.subTest(kind=kind):
                tampered = deepcopy(original)
                event = tampered["history"][0]
                if kind == "missing":
                    del event["contract_digest"]
                else:
                    event["contract_digest"] = "not-a-digest" if kind == "malformed" else "0" * 64
                self.write(tampered)
                self.rejected(lambda: controller.load(self.path))
        # Formatting, object key order, and set-like list order are not new contracts.
        original["nodes"][0]["checks"].reverse()
        original["nodes"][2]["depends_on"].reverse()
        self.path.write_text(json.dumps(original, sort_keys=True), encoding="utf-8")
        controller.load(self.path)

    def test_guarded_cancel_then_new_contract_run_rejects_old_assignment(self) -> None:
        self.assign("research")
        old_result = self.result("research")
        old_digest = self.read()["history"][0]["contract_digest"]
        self.rejected(lambda: controller.cancel(self.path, "Contract replacement", 1), "revision conflict")
        controller.cancel(self.path, "Contract replacement", 2)
        old_path = self.path
        cancelled_bytes = old_path.read_bytes()
        replacement = fixture(self.root)
        replacement["run_id"] = "replacement-run"
        replacement["locks"][0]["value"] = "New explicitly approved dialogue contract"
        replacement["nodes"][0]["checks"].append("replacement_lock")
        self.path = self.root / "replacement-run.json"
        self.write(replacement)
        self.assign("research", "replacement-worker")
        current = self.read()
        self.assertNotEqual(current["history"][0]["contract_digest"], old_digest)
        self.assertNotEqual(self.node("research")["assignment_id"], old_result["assignment_id"])
        self.rejected(lambda: controller.finish(self.path, old_result, 2), "assignment_id")
        controller.finish(self.path, self.result("research"), 2)
        self.assertEqual(self.node("research")["status"], "done")
        self.assertEqual(old_path.read_bytes(), cancelled_bytes)
        self.assertEqual(controller.load(old_path)["status"], "cancelled")

    def test_atomic_writes_preserve_xattrs_and_failed_writes_preserve_bytes(self) -> None:
        try:
            os.setxattr(self.path, "user.daksh-test", b"retained-library-identity")
        except OSError as exc:
            if exc.errno in (errno.ENOTSUP, errno.EPERM, errno.EACCES):
                self.skipTest("test filesystem does not support user xattrs")
            raise
        self.assign("research")
        self.assertEqual(os.getxattr(self.path, "user.daksh-test"), b"retained-library-identity")
        self.rejected(lambda: controller.assign(self.path, "business", "worker-b", 1), "revision conflict")
        self.assertEqual(os.getxattr(self.path, "user.daksh-test"), b"retained-library-identity")

    def test_concurrent_cli_writers_have_exactly_one_revision_winner(self) -> None:
        processes = [subprocess.Popen([
            sys.executable, str(Path(controller.__file__)), "assign", str(self.path), identity,
            "--worker", f"worker-{identity}", "--expected-revision", "1",
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for identity in ("research", "business")]
        results = [(process.communicate(timeout=10), process.returncode) for process in processes]
        self.assertEqual(sorted(code for _, code in results), [0, 2], results)
        loser = next(streams for streams, code in results if code == 2)
        self.assertIn("revision conflict", loser[1])
        self.assertEqual(self.read()["revision"], 2)
        self.assertEqual(controller.summary(self.read())["counts"]["running"], 1)
        self.assertEqual(len(self.read()["history"]), 1)

    def test_cli_full_flow_and_strict_json_rejection(self) -> None:
        self.cli("assign", str(self.path), "research", "--worker", "worker-r", "--expected-revision", "1")
        result_path = self.root / "result.json"
        result_path.write_text(json.dumps(self.result("research")), encoding="utf-8")
        self.cli("finish", str(self.path), str(result_path), "--expected-revision", "2")
        repeated = self.cli("finish", str(self.path), str(result_path), "--expected-revision", "1")
        self.assertFalse(json.loads(repeated.stdout)["changed"])
        self.cli("block", str(self.path), "business", "--reason", "Awaiting source", "--expected-revision", "3")
        self.cli("retry", str(self.path), "business", "--expected-revision", "4")
        self.cli("invalidate", str(self.path), "--source", "brief", "--version", "v2", "--expected-revision", "5")
        self.cli("cancel", str(self.path), "--reason", "Test finished", "--expected-revision", "6")
        self.assertEqual(self.read()["status"], "cancelled")
        self.path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
        before = self.path.read_bytes()
        rejected = self.cli("validate", str(self.path), success=False)
        self.assertIn("duplicate JSON key", rejected.stderr)
        self.assertEqual(self.path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
