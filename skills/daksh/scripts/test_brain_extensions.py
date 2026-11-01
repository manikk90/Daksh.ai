#!/usr/bin/env python3
"""Regression cases for scoped recall, correction history and actual task ownership."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest

import brain


class RecallAndTaskTests(unittest.TestCase):
    def setUp(self) -> None:
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "brain.json"
        self.data = json.loads((Path(__file__).resolve().parents[1] / "assets/brain.template.json").read_text())
        self.data["sources"] = [
            {"id": "user", "kind": "user_correction", "locator": "user words", "coverage": "one instruction"},
            {"id": "team", "kind": "third_party_report", "locator": "team discussion", "coverage": "a task assigned to Kamal"},
            {"id": "result", "kind": "validation_output", "locator": "actual artifact check", "coverage": "one check"},
        ]
        brain.atomic_write(self.path, self.data)

    def memory(self, identity: str, status: str = "active", scope: dict | None = None) -> dict:
        return {"id": identity, "claim": "bag @canvas-travel-bag rule", "scope": scope or {"level": "project", "project": "Laddu Gopal"}, "status": status, "evidence": "user_correction", "source_ids": ["user"]}

    def task(self, identity: str = "task", kind: str = "user", priority: str = "P1") -> dict:
        proposal = kind == "assistant"
        other = kind in {"other", "unassigned"}
        source = "team" if other else "user"
        return {"id": identity, "title": "Review the supplied model comparison", "owner": {"kind": kind, "name": "Kamal" if other else "Manik" if kind == "user" else "Daksh"}, "status": "open", "priority": priority, "scope": {"level": "task", "target": identity}, "source_ids": [source], "assignment_evidence": {"kind": "third_party_report" if other else "assistant_proposal" if proposal else "explicit_user_request", "source_ids": [source]}, "next_action": "Prepare the explicitly requested review."}

    def test_legacy_validation_does_not_insert_tasks(self) -> None:
        original = deepcopy(self.data)
        brain.validate(self.data)
        self.assertEqual(original, self.data)
        self.assertEqual(brain.summary(self.data)["counts"]["tasks"], 0)

    def test_current_recall_excludes_superseded_and_proposed(self) -> None:
        self.data["memory"] = [self.memory("old", "superseded"), self.memory("proposal", "proposed"), self.memory("current")]
        self.assertEqual([r["id"] for r in brain.retrieve(self.data, "bag")], ["current"])
        self.assertEqual(len(brain.retrieve(self.data, "bag", include_inactive=True)), 3)

    def test_other_projects_and_unscoped_records_do_not_leak(self) -> None:
        self.data["memory"] = [self.memory("lg"), self.memory("jh", scope={"level": "project", "project": "Jai Hanuman"}), self.memory("global", scope={"level": "global"})]
        self.data["research"] = [{"id": "unscoped", "finding": "bag bag bag", "verification": "proposed", "source_ids": ["user"]}]
        self.assertEqual({r["id"] for r in brain.retrieve(self.data, "bag", project="Laddu Gopal")}, {"lg", "global"})

    def test_exact_shot_override_precedes_project_default(self) -> None:
        self.data["memory"] = [self.memory("default"), self.memory("shot", scope={"level": "shot", "project": "Laddu Gopal", "target": "@s4p3s9"}), self.memory("other", scope={"level": "shot", "project": "Laddu Gopal", "target": "@s4p4s6"})]
        rows = brain.retrieve(self.data, "bag", project="Laddu Gopal", target="@s4p3s9")
        self.assertEqual([r["id"] for r in rows], ["shot", "default"])
        self.assertEqual(rows[0]["scope"]["target"], "@s4p3s9")

    def test_project_search_does_not_globalize_shot(self) -> None:
        self.data["memory"] = [self.memory("shot", scope={"level": "shot", "project": "Laddu Gopal", "target": "@s4p3s9"})]
        self.assertEqual(brain.retrieve(self.data, "bag", project="Laddu Gopal"), [])

    def test_dangling_supersession_rejected(self) -> None:
        row = self.memory("new")
        row["supersedes"] = ["missing"]
        self.data["memory"] = [row]
        with self.assertRaises(brain.BrainError): brain.validate(self.data)

    def test_cross_scope_supersession_rejected(self) -> None:
        old = self.memory("old", "superseded")
        new = self.memory("new", scope={"level": "global"})
        new["supersedes"] = ["old"]
        self.data["memory"] = [old, new]
        with self.assertRaises(brain.BrainError): brain.validate(self.data)

    def test_supersession_cycle_rejected(self) -> None:
        a, b = self.memory("a", "superseded"), self.memory("b", "superseded")
        a["supersedes"], b["supersedes"] = ["b"], ["a"]
        self.data["memory"] = [a, b]
        with self.assertRaises(brain.BrainError): brain.validate(self.data)

    def test_two_successors_cannot_claim_one_old_rule(self) -> None:
        old, a, b = self.memory("old", "superseded"), self.memory("a"), self.memory("b")
        a["supersedes"], b["supersedes"] = ["old"], ["old"]
        self.data["memory"] = [old, a, b]
        with self.assertRaises(brain.BrainError): brain.validate(self.data)

    def test_atomic_replacement_and_idempotent_retry(self) -> None:
        self.data["memory"] = [self.memory("old")]
        brain.atomic_write(self.path, self.data)
        os.setxattr(self.path, "user.library-file-id", b"identity")
        data, changed = brain.supersede(self.path, "old", self.memory("new"), 1)
        self.assertTrue(changed)
        self.assertEqual(data["memory"][0]["superseded_by"], "new")
        self.assertEqual(brain.retrieve(data, "bag")[0]["id"], "new")
        before = self.path.read_bytes()
        _, changed = brain.supersede(self.path, "old", self.memory("new"), 1)
        self.assertFalse(changed)
        self.assertEqual(before, self.path.read_bytes())
        self.assertEqual(os.getxattr(self.path, "user.library-file-id"), b"identity")

    def test_stale_replacement_preserves_bytes(self) -> None:
        self.data["memory"] = [self.memory("old")]
        brain.atomic_write(self.path, self.data)
        before = self.path.read_bytes()
        with self.assertRaises(brain.BrainError): brain.supersede(self.path, "old", self.memory("new"), 8)
        self.assertEqual(before, self.path.read_bytes())

    def test_proposed_rule_cannot_displace_explicit_correction(self) -> None:
        self.data["memory"] = [self.memory("old")]
        brain.atomic_write(self.path, self.data)
        with self.assertRaises(brain.BrainError): brain.supersede(self.path, "old", self.memory("new", "proposed"), 1)
        self.assertEqual(brain.load(self.path)["memory"][0]["status"], "active")

    def test_optional_task_append_and_idempotence(self) -> None:
        data, changed = brain.append(self.path, "tasks", self.task(), 1)
        self.assertTrue(changed)
        self.assertEqual(brain.agenda(data)[0]["id"], "task")
        _, changed = brain.append(self.path, "tasks", self.task(), 1)
        self.assertFalse(changed)

    def test_team_assignment_cannot_become_user_task(self) -> None:
        task = self.task(kind="other")
        task["owner"] = {"kind": "user", "name": "Manik"}
        self.data["tasks"] = [task]
        with self.assertRaises(brain.BrainError): brain.validate(self.data)

    def test_assistant_proposal_cannot_become_user_task(self) -> None:
        task = self.task(kind="assistant")
        task["owner"] = {"kind": "user", "name": "Manik"}
        self.data["tasks"] = [task]
        with self.assertRaises(brain.BrainError): brain.validate(self.data)

    def test_agenda_owner_priority_and_terminal_filters(self) -> None:
        self.data["tasks"] = [self.task("other", "other", "P0"), self.task("assistant", "assistant", "P2"), self.task("urgent", "user", "P0"), self.task("closed")]
        self.data["tasks"][-1].update(status="done", completion_evidence_ids=["result"])
        brain.validate(self.data)
        self.assertEqual([r["id"] for r in brain.agenda(self.data)], ["urgent", "assistant"])
        self.assertEqual([r["id"] for r in brain.agenda(self.data, "user")], ["urgent"])
        self.assertIn("other", [r["id"] for r in brain.agenda(self.data, "all")])

    def test_done_task_requires_evidence(self) -> None:
        task = self.task()
        task["status"] = "done"
        self.data["tasks"] = [task]
        with self.assertRaises(brain.BrainError): brain.validate(self.data)

    def test_blocked_task_requires_reason(self) -> None:
        task = self.task()
        task["status"] = "blocked"
        self.data["tasks"] = [task]
        with self.assertRaises(brain.BrainError): brain.validate(self.data)

    def test_full_history_capability_claim_rejected(self) -> None:
        self.data["coverage"]["all_chats_accessible"] = True
        with self.assertRaises(brain.BrainError): brain.validate(self.data)

    def test_passive_monitor_capability_claim_rejected(self) -> None:
        self.data["coverage"]["passive_device_monitoring"] = True
        with self.assertRaises(brain.BrainError): brain.validate(self.data)

    def test_task_close_and_identical_retry(self) -> None:
        brain.append(self.path, "tasks", self.task(), 1)
        state = {"status": "done", "completion_evidence_ids": ["result"]}
        data, changed = brain.task_update(self.path, "task", state, 2)
        self.assertTrue(changed)
        self.assertEqual(brain.agenda(data), [])
        before = self.path.read_bytes()
        _, changed = brain.task_update(self.path, "task", state, 2)
        self.assertFalse(changed)
        self.assertEqual(before, self.path.read_bytes())

    def test_task_close_without_proof_preserves_bytes(self) -> None:
        brain.append(self.path, "tasks", self.task(), 1)
        before = self.path.read_bytes()
        with self.assertRaises(brain.BrainError): brain.task_update(self.path, "task", {"status": "done"}, 2)
        self.assertEqual(before, self.path.read_bytes())

    def test_task_owner_cannot_change_through_state_update(self) -> None:
        brain.append(self.path, "tasks", self.task(), 1)
        with self.assertRaises(brain.BrainError): brain.task_update(self.path, "task", {"status": "open", "owner": {"kind": "other", "name": "Kamal"}}, 2)

    def test_stale_task_update_preserves_bytes(self) -> None:
        brain.append(self.path, "tasks", self.task(), 1)
        before = self.path.read_bytes()
        with self.assertRaises(brain.BrainError): brain.task_update(self.path, "task", {"status": "in_progress"}, 1)
        self.assertEqual(before, self.path.read_bytes())

    def test_closed_task_does_not_reappear_without_new_request(self) -> None:
        brain.append(self.path, "tasks", self.task(), 1)
        brain.task_update(self.path, "task", {"status": "done", "completion_evidence_ids": ["result"]}, 2)
        with self.assertRaises(brain.BrainError): brain.task_update(self.path, "task", {"status": "open"}, 3)


if __name__ == "__main__":
    unittest.main()
