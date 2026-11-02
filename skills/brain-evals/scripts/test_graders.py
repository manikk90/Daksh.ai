import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import graders  # noqa: E402
import run_evals  # noqa: E402

ROOT = HERE.parents[2]


def ok(text, *checks):
    return all(r["ok"] for r in graders.grade(text, list(checks), ROOT))


class GraderTests(unittest.TestCase):
    def test_fences_are_stripped(self):
        text = "```\nshot\n\nDIALOGUE: @a: \"hi\"\n```"
        self.assertTrue(ok(text, {"type": "last_line", "pattern": "^DIALOGUE:"}))

    def test_notes_outside_code_block_are_not_graded(self):
        text = "```\nshot @naina-01\n\nDIALOGUE: @naina-01: \"hi\"\n```\n- I left out @crowd on purpose."
        self.assertTrue(ok(text, {"type": "last_line", "pattern": "^DIALOGUE:"}, {"type": "tags", "forbidden": ["@crowd"]}))

    def test_no_fences_grades_whole_text(self):
        self.assertFalse(ok("shot\n- note with @crowd", {"type": "tags", "forbidden": ["@crowd"]}))

    def test_parenthetical_cues_ignored_in_words(self):
        spec = {"type": "preserves_words", "text": "Maa, tum kab aaogi? Main yahin hoon."}
        self.assertTrue(ok('(rote hue) "Maa, tum kab aaogi?" (sisak) "Main yahin hoon."', spec))

    def test_last_line_rejects_trailing_content(self):
        self.assertFalse(ok("DIALOGUE: @a: \"hi\"\nCamera: push", {"type": "last_line", "pattern": "^DIALOGUE:"}))

    def test_blank_line_before(self):
        spec = {"type": "blank_line_before", "pattern": "^DIALOGUE:"}
        self.assertTrue(ok("x\n\nDIALOGUE: y", spec))
        self.assertFalse(ok("x\nDIALOGUE: y", spec))
        self.assertFalse(ok("DIALOGUE: y", spec))

    def test_tags_required_forbidden_allowed(self):
        self.assertTrue(ok("@naina-01 on @steps.ground", {"type": "tags", "required": ["@naina-01"], "allowed": ["@steps.ground"]}))
        self.assertFalse(ok("@naina-01 and @crowd", {"type": "tags", "forbidden": ["@crowd"]}))
        self.assertFalse(ok("@naina-01 and @extra", {"type": "tags", "required": ["@naina-01"], "allowed": []}))

    def test_preserves_words_ignores_tags_and_punctuation(self):
        spec = {"type": "preserves_words", "text": "Maa, tum kab aaogi?"}
        self.assertTrue(ok("[sobbing] Maa... tum kab aaogi!", spec))
        self.assertFalse(ok("Maiya, tum kab aaogi?", spec))
        self.assertFalse(ok("Maa, kab tum aaogi?", spec))

    def test_preserves_devanagari_words(self):
        spec = {"type": "preserves_words", "text": "माँ, मुझे डर लग रहा है।"}
        self.assertTrue(ok("[crying] माँ, मुझे डर लग रहा है।", spec))
        self.assertFalse(ok("माँ, मुझे बहुत डर लग रहा है।", spec))

    def test_count_and_regex(self):
        self.assertTrue(ok("a\nDIALOGUE: x", {"type": "count_regex", "pattern": "^DIALOGUE:", "min": 1, "max": 1}))
        self.assertFalse(ok("DIALOGUE: x\nDIALOGUE: y", {"type": "count_regex", "pattern": "^DIALOGUE:", "max": 1}))
        self.assertFalse(ok("Refs (continuity): @a", {"type": "regex_absent", "pattern": "^Refs \\(continuity\\)"}))

    def test_max_chars(self):
        self.assertTrue(ok("x" * 800, {"type": "max_chars", "max": 800}))
        self.assertFalse(ok("x" * 801, {"type": "max_chars", "max": 800}))

    def test_unknown_and_bad_specs_fail_closed(self):
        self.assertFalse(ok("x", {"type": "nope"}))
        self.assertFalse(ok("x", {"type": "regex_present"}))
        self.assertFalse(ok("x", {"type": "regex_present", "pattern": "("}))


class CaseSuiteTests(unittest.TestCase):
    def test_cases_load_and_have_known_skills(self):
        cases = run_evals.load_cases()
        self.assertGreaterEqual(len(cases), 20)
        for case in cases:
            self.assertTrue((ROOT / "skills" / case["skill"] / "SKILL.md").is_file(), case["id"])
            for check in case["checks"]:
                self.assertIn(check["type"], graders.CHECKS, case["id"])

    def test_selftest_and_routing_pass(self):
        for cmd in ("selftest", "routing"):
            proc = subprocess.run([sys.executable, str(HERE / "run_evals.py"), cmd], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_infra_errors_are_excluded(self):
        self.assertTrue(run_evals.infra_error("You've hit your 5-hour limit · resets 10:50pm (UTC)"))
        self.assertTrue(run_evals.infra_error("   "))
        self.assertIsNone(run_evals.infra_error("A long real prompt " * 40 + " rate limit mentioned in prose"))
        cell = run_evals.score([{"ok": True}, {"ok": None, "error": "limit"}])
        self.assertEqual((cell["pass_rate"], cell["valid_runs"], cell["errored_runs"]), (1.0, 1, 1))

    def test_run_with_fake_agent(self):
        fake = f"{sys.executable} -c \"import sys; sys.stdin.read(); print('[crying softly] माँ, मुझे डर लग रहा है।')\""
        out = ROOT / "research/evals/_test_tmp.json"
        try:
            code = run_evals.main(["run", "--agent-cmd", fake, "--case", "dub-word-lock-tags", "--trials", "2",
                                   "--out", str(out.relative_to(ROOT))])
            self.assertEqual(code, 0)
            report = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(report["with_skill_mean"], 1.0)
            self.assertEqual(report["baseline_mean"], 1.0)
            self.assertEqual(report["lift"], 0.0)
        finally:
            out.unlink(missing_ok=True)
            try:
                out.parent.rmdir()
            except OSError:
                pass


if __name__ == "__main__":
    unittest.main()
