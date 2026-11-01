#!/usr/bin/env python3
"""Exercise state provenance, concurrency and lexical retrieval contracts."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest

import brain


class BrainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "brain.json"
        template = Path(__file__).resolve().parents[1] / "assets/brain.template.json"
        self.data = json.loads(template.read_text())
        self.data["sources"] = [{"id": "source-user", "kind": "user_instruction", "locator": "current user message", "coverage": "one message"}]
        brain.atomic_write(self.path, self.data)

    def memory(self, identity: str = "mem-bag") -> dict:
        return {"id": identity, "claim": "Use @canvas-travel-bag only where visible or mentioned.", "scope": {"level": "project", "project": "Laddu Gopal"}, "status": "active", "evidence": "user_instruction", "source_ids": ["source-user"]}

    def test_valid_template(self) -> None:
        self.assertEqual(brain.load(self.path)["revision"], 1)

    def test_stale_write_preserves_bytes(self) -> None:
        before = self.path.read_bytes()
        with self.assertRaises(brain.BrainError):
            brain.append(self.path, "memory", self.memory(), 99)
        self.assertEqual(before, self.path.read_bytes())

    def test_retry_is_idempotent(self) -> None:
        data, changed = brain.append(self.path, "memory", self.memory(), 1)
        self.assertTrue(changed)
        self.assertEqual(data["revision"], 2)
        before = self.path.read_bytes()
        _, changed = brain.append(self.path, "memory", self.memory(), 1)
        self.assertFalse(changed)
        self.assertEqual(before, self.path.read_bytes())

    def test_conflicting_identity_rejected(self) -> None:
        brain.append(self.path, "memory", self.memory(), 1)
        changed = self.memory()
        changed["claim"] = "Put a bag in every shot."
        with self.assertRaises(brain.BrainError):
            brain.append(self.path, "memory", changed, 2)

    def test_unknown_source_rejected(self) -> None:
        row = self.memory()
        row["source_ids"] = ["missing"]
        with self.assertRaises(brain.BrainError):
            brain.append(self.path, "memory", row, 1)

    def test_inferred_preference_not_active(self) -> None:
        row = self.memory()
        row["evidence"] = "inference"
        with self.assertRaises(brain.BrainError):
            brain.append(self.path, "memory", row, 1)

    def test_shot_scope_needs_target(self) -> None:
        row = self.memory()
        row["scope"]["level"] = "shot"
        with self.assertRaises(brain.BrainError):
            brain.append(self.path, "memory", row, 1)

    def test_assistant_cannot_declare_user_approval(self) -> None:
        row = {"id": "act-1", "action": "Image generated", "actor": "assistant", "outcome": "approved", "source_ids": ["source-user"]}
        with self.assertRaises(brain.BrainError):
            brain.append(self.path, "actions", row, 1)

    def test_hypothesis_cannot_be_validated_without_evidence(self) -> None:
        row = {"id": "opp-1", "problem": "Workflow continuity failures", "next_step": "Interview a buyer", "status": "validated", "source_ids": ["source-user"]}
        with self.assertRaises(brain.BrainError):
            brain.append(self.path, "opportunities", row, 1)

    def test_new_rule_needs_actual_test_extent(self) -> None:
        row = {"id": "lesson-1", "rule": "Use fewer reads", "status": "active", "evidence": "inference", "test": {"outcome": "pass"}, "source_ids": ["source-user"]}
        with self.assertRaises(brain.BrainError):
            brain.append(self.path, "lessons", row, 1)

    def test_exact_tag_retrieval_and_empty_query(self) -> None:
        data, _ = brain.append(self.path, "memory", self.memory(), 1)
        self.assertEqual(brain.retrieve(data, "@canvas-travel-bag")[0]["id"], "mem-bag")
        with self.assertRaises(brain.BrainError):
            brain.retrieve(data, "  ")

    def test_identity_xattrs_preserved(self) -> None:
        os.setxattr(self.path, "user.library-file-id", b"test-identity")
        brain.append(self.path, "memory", self.memory(), 1)
        self.assertEqual(os.getxattr(self.path, "user.library-file-id"), b"test-identity")


if __name__ == "__main__":
    unittest.main()
