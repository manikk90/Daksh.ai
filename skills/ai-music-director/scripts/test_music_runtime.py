#!/usr/bin/env python3
"""Regression and boundary tests for output locks and provider/mode compatibility."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import music_runtime as runtime


class MusicRuntimeTests(unittest.TestCase):
    def instrumental(self):
        return {"platform": "suno", "mode": "instrumental", "allow_vocals": False,
                "styles": "Veena and bansuri grief cue. Instrumental only, no vocals, no lyrics, no spoken word, no choir.",
                "parameters": {"instrumental": True}}

    def plan(self):
        return {"platform": "eleven-music", "mode": "plan", "allow_vocals": False,
                "request": {"model_id": "music_v2_5", "composition_plan": {"chunks": [
                    {"text": "[Anticipation]", "duration_ms": 27000,
                     "positive_styles": ["bansuri", "veena", "unresolved", "instrumental"],
                     "negative_styles": ["vocals", "lyrics", "spoken word", "choir"]},
                    {"text": "[Release]", "duration_ms": 12000,
                     "positive_styles": ["warm strings", "veena", "instrumental"],
                     "negative_styles": ["vocals", "lyrics", "spoken word", "choir"]},
                    {"text": "[Calm tail]", "duration_ms": 6000,
                     "positive_styles": ["bansuri", "quiet", "instrumental"],
                     "negative_styles": ["vocals", "lyrics", "spoken word", "choir"]}]}}}

    def test_editorial_budget_is_not_a_provider_cap(self):
        p = runtime.resolve("suno", "instrumental")
        self.assertEqual(p["effective_styles_budget"], 800)
        self.assertIsNone(p["provider_hard_max"])
        self.assertIsNone(runtime.resolve("suno", "song")["effective_styles_budget"])

    def test_user_budget_wins_and_output_is_not_truncated(self):
        package = self.instrumental()
        package["user_max_chars"] = 20
        original = package["styles"]
        self.assertEqual(runtime.audit(package)["status"], "FAIL")
        self.assertEqual(package["styles"], original)

    def test_valid_instrumental_and_required_exclusions(self):
        package = self.instrumental()
        self.assertEqual(runtime.audit(package)["status"], "PASS")
        package["styles"] = "Veena instrumental"
        self.assertEqual(runtime.audit(package)["status"], "FAIL")

    def test_instrumental_cannot_keep_sung_lyrics(self):
        package = self.instrumental()
        package["lyrics"] = "मेरे गोपाल"
        self.assertEqual(runtime.audit(package)["status"], "FAIL")

    def test_exact_hook_lock_is_preserved(self):
        hook = "लड्डू गोपाल मेरा, लड्डू गोपाल"
        package = {"platform": "suno", "mode": "song", "lyrics": hook,
                   "locked_lines": [hook], "styles": "Tender young-girl devotional folk song"}
        self.assertEqual(runtime.audit(package)["status"], "PENDING")
        package["lyrics"] = "लड्डू गोपाल मेरे"
        self.assertEqual(runtime.audit(package)["status"], "FAIL")

    def test_unsupported_singing_route_is_not_silently_downgraded(self):
        package = {"platform": "stable-audio", "mode": "song", "styles": "Devotional", "lyrics": "मेरे गोपाल"}
        self.assertEqual(runtime.audit(package)["status"], "FAIL")
        self.assertEqual(package["lyrics"], "मेरे गोपाल")

    def test_unknown_parameter_blocks_external_submission(self):
        package = self.instrumental()
        package["parameters"]["micro_expression"] = 95
        result = runtime.audit(package)
        self.assertEqual(result["status"], "PENDING")
        self.assertIn("PENDING_SUPPORT", " ".join(result["warnings"]))

    def test_vocal_control_contradiction(self):
        package = {"platform": "eleven-music", "mode": "song", "styles": "Folk", "lyrics": "गोपाल",
                   "parameters": {"force_instrumental": True}}
        self.assertEqual(runtime.audit(package)["status"], "FAIL")

    def test_prompt_cap_does_not_apply_to_plan_serialization(self):
        package = self.plan()
        package["request"]["composition_plan"]["chunks"][0]["positive_styles"] = ["detailed sparse texture " * 250]
        result = runtime.audit(package)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["request_check"]["total_duration_ms"], 45000)

    def test_plan_rejects_prompt_only_control_and_vocal_text(self):
        package = self.plan()
        package["request"]["force_instrumental"] = True
        self.assertEqual(runtime.audit(package)["status"], "FAIL")
        del package["request"]["force_instrumental"]
        package["request"]["composition_plan"]["chunks"][0]["text"] += "\nमेरे गोपाल"
        self.assertEqual(runtime.audit(package)["status"], "FAIL")

    def test_plan_requires_each_chunks_no_voice_constraints(self):
        package = self.plan()
        package["request"]["composition_plan"]["chunks"][1]["negative_styles"] = []
        self.assertEqual(runtime.audit(package)["status"], "FAIL")

    def test_unicode_counts_and_parameter_types(self):
        package = {"platform": "eleven-music", "mode": "prompt", "styles": "🌼 गोपाल",
                   "parameters": {"music_length_ms": True}}
        result = runtime.audit(package)
        self.assertGreater(result["styles_utf16_units"], result["styles_code_points"])
        self.assertEqual(result["status"], "FAIL")

    def test_updated_profile_cap_is_used_without_code_change(self):
        original_load = runtime.load
        profile = copy.deepcopy(original_load("control-profiles.json"))
        profile["profiles"]["eleven-music"]["styles_hard_max"] = 12
        with patch.object(runtime, "load", side_effect=lambda name: profile if name == "control-profiles.json" else original_load(name)):
            package = {"platform": "eleven-music", "mode": "prompt", "styles": "x" * 13}
            self.assertEqual(runtime.audit(package)["status"], "FAIL")

    def test_pending_cli_has_nonzero_exit_and_audio_not_claimed(self):
        package = self.instrumental()
        package["parameters"]["style_influence"] = 60
        with tempfile.TemporaryDirectory(prefix="music-runtime-") as td:
            path = Path(td) / "package.json"
            path.write_text(json.dumps(package), encoding="utf-8")
            result = subprocess.run([sys.executable, str(runtime.ROOT / "scripts/music_runtime.py"), "audit", str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["audio_review"], "NOT_PERFORMED")

    def test_request_cannot_override_song_with_instrumental(self):
        package = {"platform": "eleven-music", "mode": "song", "lyrics": "Approved hook",
                   "locked_lines": ["Approved hook"],
                   "request": {"model_id": "music_v2", "prompt": "Gentle piano", "force_instrumental": True}}
        self.assertEqual(runtime.audit(package)["status"], "FAIL")

    def test_request_cannot_disable_instrumental_or_lose_constraints(self):
        package = self.instrumental()
        package["platform"] = "eleven-music"
        package["parameters"] = {"force_instrumental": True}
        package["request"] = {"model_id": "music_v2", "prompt": "young girl singing", "force_instrumental": False}
        self.assertEqual(runtime.audit(package)["status"], "FAIL")
        package["request"] = {"model_id": "music_v2", "prompt": package["styles"], "force_instrumental": True}
        self.assertEqual(runtime.audit(package)["status"], "PASS")

    def test_lock_must_appear_in_submitted_plan(self):
        package = self.plan()
        package["allow_vocals"] = True
        package["lyrics"] = "Approved hook"
        package["locked_lines"] = ["Approved hook"]
        self.assertEqual(runtime.audit(package)["status"], "FAIL")

    def test_interface_modes_do_not_bypass_vocal_capability(self):
        for platform, mode in (("soundraw", "controls"), ("stable-audio", "prompt"), ("stable-audio", "plan")):
            with self.subTest(platform=platform, mode=mode):
                package = {"platform": platform, "mode": mode, "lyrics": "Approved hook", "allow_vocals": True, "user_max_chars": 800}
                self.assertEqual(runtime.audit(package)["status"], "FAIL")

    def test_actual_soundraw_controls_are_required(self):
        package = {"platform": "soundraw", "mode": "controls"}
        self.assertEqual(runtime.audit(package)["status"], "FAIL")
        package["control_map"] = {"length_seconds": 30}
        self.assertEqual(runtime.audit(package)["status"], "PENDING")

    def test_nested_parameters_receive_type_checks(self):
        for name in ("store_for_inpainting", "respect_sections_durations", "sign_with_c2pa", "finetune_id"):
            with self.subTest(name=name):
                package = {"platform": "eleven-music", "mode": "prompt", "request": {"model_id": "music_v2", "prompt": "piano", name: 17}}
                self.assertEqual(runtime.audit(package)["status"], "FAIL")

    def test_malformed_lock_list_cannot_be_checked_character_by_character(self):
        with self.assertRaises(ValueError):
            runtime.audit({"platform": "eleven-music", "mode": "song", "lyrics": "B r o k e n   h o o k", "locked_lines": "Broken hook"})

    def test_actual_submitted_prompt_respects_user_budget(self):
        package = {"platform": "eleven-music", "mode": "prompt", "user_max_chars": 5,
                   "request": {"model_id": "music_v2", "prompt": "x" * 100}}
        self.assertEqual(runtime.audit(package)["status"], "FAIL")

    def test_valid_vocal_plan_retains_actual_lyrics(self):
        package = self.plan()
        package["allow_vocals"] = True
        package["lyrics"] = "मेरे गोपाल"
        package["locked_lines"] = ["मेरे गोपाल"]
        package["request"]["composition_plan"]["chunks"][0]["text"] = "[Verse]\nमेरे गोपाल"
        package["request"]["composition_plan"]["chunks"][0]["negative_styles"] = []
        self.assertEqual(runtime.audit(package)["status"], "PASS")

    def test_explicit_parameters_cannot_disappear_from_request(self):
        package = {"platform": "eleven-music", "mode": "prompt",
                   "parameters": {"music_length_ms": 60000, "store_for_inpainting": True},
                   "request": {"model_id": "music_v2", "prompt": "gentle piano"}}
        self.assertEqual(runtime.audit(package)["status"], "FAIL")
        package["request"].update(package["parameters"])
        self.assertEqual(runtime.audit(package)["status"], "PASS")

    def test_submitted_lyric_order_and_repeated_refrain_are_preserved(self):
        package = self.plan()
        package["allow_vocals"] = True
        package["lyrics"] = "first verse\nchorus\nsecond verse\nchorus"
        package["locked_lines"] = ["chorus"]
        chunk = package["request"]["composition_plan"]["chunks"][0]
        chunk["negative_styles"] = []
        chunk["text"] = "second verse\nchorus\nfirst verse"
        self.assertEqual(runtime.audit(package)["status"], "FAIL")
        chunk["text"] = "[Verse]\n" + package["lyrics"]
        self.assertEqual(runtime.audit(package)["status"], "PASS")

    def test_hook_is_an_exact_line_not_a_prefix(self):
        package = {"platform": "suno", "mode": "song", "lyrics": "Approved hook changed", "locked_lines": ["Approved hook"], "user_max_chars": 500}
        self.assertEqual(runtime.audit(package)["status"], "FAIL")

    def test_v1_model_cannot_use_saved_v2_plan_adapter(self):
        self.assertEqual(runtime.audit({"platform": "eleven-music", "mode": "plan", "model": "music_v1"})["status"], "FAIL")

    def test_confirmed_daily_coordinator_and_sunday_branch(self):
        state = runtime.load("improvement-state.json")
        self.assertEqual(runtime.validate_schedule(state["schedule"], state["timezone"])["chat_review_cadence"], "P1D")

    def test_pending_binding_does_not_need_invented_confirmation(self):
        task = copy.deepcopy(runtime.load("improvement-state.json")["schedule"])
        task.update(status="PENDING_CONFIRMATION", is_enabled=None, confirmed_at=None)
        self.assertEqual(runtime.validate_schedule(task, "Asia/Kolkata")["coordinated_task_status"], "PENDING_CONFIRMATION")
        task["is_enabled"] = True
        with self.assertRaises(AssertionError):
            runtime.validate_schedule(task, "Asia/Kolkata")

    def test_enabled_binding_needs_observed_confirmation(self):
        task = copy.deepcopy(runtime.load("improvement-state.json")["schedule"])
        task["confirmed_at"] = None
        with self.assertRaises(AssertionError):
            runtime.validate_schedule(task, "Asia/Kolkata")

    def test_old_weekly_and_three_day_cadences_rejected(self):
        baseline = runtime.load("improvement-state.json")["schedule"]
        for replacement in ("RRULE:FREQ=WEEKLY;BYDAY=SU", "RRULE:FREQ=DAILY;INTERVAL=3"):
            task = copy.deepcopy(baseline)
            task["schedule"] = task["schedule"].replace("RRULE:FREQ=DAILY", replacement)
            with self.subTest(recurrence=replacement), self.assertRaises(AssertionError):
                runtime.validate_schedule(task, "Asia/Kolkata")

    def test_research_branch_and_local_time_are_checked(self):
        baseline = runtime.load("improvement-state.json")["schedule"]
        for field, value in (("day", "FR"), ("not_before", "08:00"), ("mode", "separate_weekly_automation")):
            task = copy.deepcopy(baseline)
            task["weekly_research"][field] = value
            with self.subTest(research_field=field), self.assertRaises(AssertionError):
                runtime.validate_schedule(task, "Asia/Kolkata")
        task = copy.deepcopy(baseline)
        task["schedule"] = task["schedule"].replace("T230000", "T080000")
        with self.assertRaises(AssertionError):
            runtime.validate_schedule(task, "Asia/Kolkata")


if __name__ == "__main__":
    unittest.main()
