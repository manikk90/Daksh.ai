#!/usr/bin/env python3
"""Resolve saved music profiles and audit contracts. Never generates or reviews audio."""
import argparse
import json
import re
from datetime import date
from pathlib import Path
from music_qc import check_eleven, check_resources

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / "assets" / name).read_text(encoding="utf-8"))


def platform_key(value):
    key = value.strip().lower().replace("_", "-").replace(" ", "-")
    return {"elevenlabs": "eleven-music", "eleven": "eleven-music", "stableaudio": "stable-audio"}.get(key, key)


def missing_ordered_lines(expected, actual_text):
    """Consume exact line occurrences so order and repeated refrains survive."""
    actual = actual_text.splitlines()
    cursor = 0
    for line in expected:
        try:
            cursor = actual.index(line, cursor) + 1
        except ValueError:
            return line
    return None


def resolve(platform, mode, user_cap=None):
    key = platform_key(platform)
    profiles = load("control-profiles.json")
    if key not in profiles["profiles"]:
        raise ValueError(f"Unknown platform {key}; verify and add an official-source profile")
    if mode not in {"song", "instrumental", "prompt", "plan", "controls"}:
        raise ValueError("Unknown output mode")
    profile = profiles["profiles"][key]
    hard = None if mode in {"plan", "controls"} else profile["styles_hard_max"]
    preferred = profile["instrumental_preferred_max"] if mode == "instrumental" else None
    if user_cap is not None and (type(user_cap) is not int or user_cap < 1):
        raise ValueError("User cap must be a positive integer")
    applicable = [x for x in (hard, preferred, user_cap) if x is not None]
    return {"platform": key, "mode": mode, "checked_at": profiles["checked_at"],
            "effective_styles_budget": min(applicable) if applicable else None,
            "provider_hard_max": hard, "editorial_preference": preferred,
            "user_cap": user_cap, "profile": profile,
            "support_status": "DATED_SNAPSHOT_REVERIFY_FOR_CURRENT_CLAIMS"}


def audit(package):
    if not isinstance(package, dict):
        raise ValueError("Package must be an object")
    info = resolve(package["platform"], package["mode"], package.get("user_max_chars"))
    profile = info["profile"]
    mode = info["mode"]
    styles = package.get("styles", "")
    lyrics = package.get("lyrics", "")
    if not isinstance(styles, str) or not isinstance(lyrics, str):
        raise ValueError("Styles and lyrics must be strings")
    locks = package.get("locked_lines", [])
    if not isinstance(locks, list) or not all(isinstance(x, str) and x for x in locks):
        raise ValueError("locked_lines must be a list of nonempty exact lyric strings")
    errors, warnings = [], []
    budget = info["effective_styles_budget"]
    if budget is not None and len(styles) > budget:
        errors.append(f"Styles has {len(styles)} code points; budget {budget}. Rewrite semantically; do not truncate.")
    if budget is None and mode not in {"plan", "controls"}:
        warnings.append("No verified numeric Styles cap; validate actual destination before submission.")
    lyric_cap = profile["lyrics_hard_max"]
    if lyric_cap is not None and len(lyrics) > lyric_cap:
        errors.append(f"Lyrics exceed verified cap {lyric_cap}; preserve locks and revise or split into supported sections.")
    if info["platform"] == "soundraw" and mode != "controls":
        errors.append("Use an actual SOUNDRAW control map, not an invented Styles/Lyrics field.")
    if info["platform"] == "soundraw" and mode == "controls":
        control_map = package.get("control_map", package.get("parameters", {}))
        if not isinstance(control_map, dict) or not control_map:
            errors.append("SOUNDRAW controls mode requires a nonempty actual control map.")
        else:
            warnings.append("Verify this control map against the actual SOUNDRAW interface before applying.")
    vocal_intent = mode == "song" or package.get("allow_vocals") is True or bool(lyrics.strip()) or bool(locks)
    instrumental_intent = mode == "instrumental" or package.get("allow_vocals") is False
    if vocal_intent and instrumental_intent:
        errors.append("Vocal intent conflicts with instrumental/no-vocal intent.")
    if vocal_intent and profile["vocal_generation"] is False:
        errors.append("This profile is not an intelligible-singing route; preserve the vocal brief and choose a supported route.")
    elif vocal_intent and profile["vocal_generation"] is None:
        warnings.append("Sung vocal support unverified; use a verified vocal route or explicit pending handoff.")
    if mode == "instrumental":
        if lyrics.strip() or package.get("allow_vocals") is True:
            errors.append("Instrumental mode conflicts with lyrics/authorized vocals.")
        missing = [x for x in ("instrumental", "no vocals", "no lyrics", "no spoken word", "no choir") if x not in styles.lower()]
        if missing:
            errors.append("Missing instrumental text constraints: " + ", ".join(missing))
    if mode == "song":
        if not lyrics.strip():
            errors.append("Song request has lost its lyrics; preserve them or provide a separate vocal handoff.")
        if package.get("allow_vocals") is False:
            errors.append("Song with lyrics conflicts with allow_vocals=false.")
    missing_lock = missing_ordered_lines(locks, lyrics)
    if missing_lock is not None:
        errors.append("Locked lyric line missing, altered or reordered: " + missing_lock)
    if package.get("model") and package["model"] not in profile["models"]:
        warnings.append("Model not in the saved verified profile; reverify support instead of assuming it.")
    parameters = package.get("parameters", {})
    if not isinstance(parameters, dict):
        raise ValueError("parameters must be an object")
    if info["platform"] == "eleven-music" and mode == "plan" and "music_v1" in (package.get("model"), parameters.get("model_id")):
        errors.append("The saved chunk-plan adapter requires music_v2 or music_v2_5, not music_v1.")
    for name, value in parameters.items():
        spec = profile["parameters"].get(name)
        if spec is None:
            warnings.append(f"PENDING_SUPPORT: {name}; do not submit/apply until verified for exact model/interface.")
            continue
        if "modes" in spec and mode not in spec["modes"]:
            errors.append(f"{name} is not compatible with mode {mode}.")
        if spec.get("type") == "boolean" and type(value) is not bool:
            errors.append(f"{name} must be boolean.")
        if spec.get("type") == "integer":
            if type(value) is not int or not spec["min"] <= value <= spec["max"]:
                errors.append(f"{name} must be integer {spec['min']}..{spec['max']}.")
        if "enum" in spec and value not in spec["enum"]:
            errors.append(f"{name} not in the saved verified enum.")
    if vocal_intent and (parameters.get("force_instrumental") is True or parameters.get("instrumental") is True):
        errors.append("Song mode conflicts with an instrumental control.")
    if instrumental_intent and any(parameters.get(x) is False for x in ("force_instrumental", "instrumental")):
        errors.append("Instrumental mode conflicts with an explicitly disabled instrumental control.")
    request_result = None
    if "request" in package:
        if info["platform"] != "eleven-music":
            errors.append("No request-body validator for this platform; use its actual current schema.")
        else:
            body = package["request"]
            try:
                request_result = check_eleven(body)
                actual_mode = "plan" if body.get("composition_plan") is not None else "prompt"
                if (mode == "plan") != (actual_mode == "plan"):
                    errors.append("Package mode and Music API request mode disagree.")
                unknown = set(body) - {"prompt", "composition_plan", "model_id", "music_length_ms", "seed", "force_instrumental", "store_for_inpainting", "respect_sections_durations", "finetune_id", "sign_with_c2pa"}
                if unknown:
                    warnings.append("PENDING_SUPPORT request fields: " + ", ".join(sorted(unknown)))
                if package.get("model") and package["model"] != body["model_id"]:
                    errors.append("Package model and submitted model_id disagree.")
                for name, value in parameters.items():
                    if name in profile["parameters"] and name not in body:
                        errors.append(f"Requested parameter {name} is missing from submitted request.")
                    elif name in body and value != body[name]:
                        errors.append(f"Package parameter {name} disagrees with submitted request.")
                if vocal_intent and body.get("force_instrumental") is True:
                    errors.append("Submitted request forces instrumental despite vocal intent.")
                if instrumental_intent and body.get("force_instrumental") is False:
                    errors.append("Submitted request explicitly disables instrumental enforcement.")
                submitted_text = body["prompt"] if actual_mode == "prompt" else "\n".join(x["text"] for x in body["composition_plan"]["chunks"])
                missing_lock = missing_ordered_lines(locks, submitted_text)
                if missing_lock is not None:
                    errors.append("Locked lyric absent/altered/reordered in submitted request: " + missing_lock)
                lyric_lines = [line for line in lyrics.splitlines() if line.strip() and not re.fullmatch(r"\s*\[[^\]]*\]\s*", line)]
                missing_lyric = missing_ordered_lines(lyric_lines, submitted_text)
                if missing_lyric is not None:
                    errors.append("Submitted lyrics lost/altered/reordered an occurrence: " + missing_lyric)
                if actual_mode == "prompt":
                    submitted_budget = resolve(info["platform"], "prompt", package.get("user_max_chars"))["effective_styles_budget"]
                    if submitted_budget is not None and len(submitted_text) > submitted_budget:
                        errors.append(f"Actual submitted prompt exceeds effective budget {submitted_budget}.")
                    if instrumental_intent:
                        missing = [x for x in ("instrumental", "no vocals", "no lyrics", "no spoken word", "no choir") if x not in submitted_text.lower()]
                        if missing:
                            errors.append("Submitted instrumental prompt lacks constraints: " + ", ".join(missing))
                if actual_mode == "plan" and instrumental_intent:
                    for index, chunk in enumerate(body["composition_plan"]["chunks"]):
                        exclusions = {x.lower() for x in chunk.get("negative_styles", [])}
                        if not {"vocals", "lyrics", "spoken word", "choir"} <= exclusions:
                            errors.append(f"Instrumental plan chunk {index} lacks required no-voice exclusions.")
                        content = re.sub(r"\[[^\]]*\]|\{[^}]*\}", "", chunk["text"]).strip()
                        if content:
                            errors.append(f"Instrumental plan chunk {index} has non-label text; move performance prose into styles and omit lyrics.")
            except (AssertionError, ValueError, KeyError, TypeError) as error:
                errors.append(str(error))
    return {"status": "FAIL" if errors else "PENDING" if warnings else "PASS", "errors": errors, "warnings": warnings,
            "styles_code_points": len(styles), "styles_utf16_units": len(styles.encode("utf-16-le")) // 2,
            "effective_styles_budget": budget, "request_check": request_result,
            "evidence": "TEXT_CONTRACT_ONLY", "audio_review": "NOT_PERFORMED"}


def validate_schedule(task, timezone):
    """Check the coordinated daily/Sunday binding; never confirms a scheduler."""
    assert timezone == "Asia/Kolkata", "Learning cadence uses Asia/Kolkata"
    assert task["status"] in {"PENDING_SETUP", "PENDING_CONFIRMATION", "ENABLED", "PAUSED", "ERROR"}
    assert task["coordinator"] == "Daksh" and task["task_id"], "Use the existing Daksh coordinator"
    assert task["mode"] == "one_coordinator_with_weekly_branch"
    assert task["cadence"] == "daily", "Recent-chat learning is daily"
    assert task["daily_not_before"] == task["preferred_local_time"] == "23:00"
    lines = task["schedule"].splitlines()
    starts = [x for x in lines if x.startswith("DTSTART")]
    assert len(starts) == 1 and starts[0].startswith("DTSTART;TZID=Asia/Kolkata:") and starts[0].endswith("T230000"), "Daily start must be 23:00 Asia/Kolkata"
    rules = [x for x in lines if x.startswith("RRULE:")]
    assert len(rules) == 1
    recurrence = dict(part.split("=", 1) for part in rules[0][6:].split(";"))
    assert recurrence.get("FREQ") == "DAILY" and recurrence.get("INTERVAL", "1") == "1" and "BYDAY" not in recurrence, "Use one daily coordinator, not a specialist weekly/three-day timer"
    research = task["weekly_research"]
    assert research["day"] == "SU" and research["not_before"] == "23:00"
    assert research["mode"] == "conditional_branch_in_same_daily_automation"
    if task["status"] == "ENABLED":
        assert task.get("is_enabled") is True and task.get("confirmed_at") and task.get("verification_note"), "Enabled status requires observed confirmation"
        date.fromisoformat(task["confirmed_at"].split("T", 1)[0])
    else:
        assert task.get("is_enabled") is not True, "Unconfirmed/paused state cannot claim enabled"
        if task["status"] in {"PENDING_SETUP", "PENDING_CONFIRMATION"}:
            assert not task.get("confirmed_at"), "Pending binding cannot claim confirmation"
    return {"coordinated_task_status": task["status"], "chat_review_cadence": "P1D", "research_day": "SU"}


def validate():
    result = check_resources(ROOT)
    controls = load("control-profiles.json")
    patterns = load("lyric-patterns.json")["patterns"]
    state = load("improvement-state.json")
    date.fromisoformat(controls["checked_at"])
    assert len({x["id"] for x in patterns}) == len(patterns), "Duplicate lyric pattern IDs"
    for pattern in patterns:
        assert pattern["shape"] and pattern["avoid"] and pattern["validation"]
    for profile in controls["profiles"].values():
        assert profile["sources"], "Source required for control profile"
        for field in ("styles_hard_max", "instrumental_preferred_max", "lyrics_hard_max"):
            assert profile[field] is None or (type(profile[field]) is int and profile[field] > 0)
    schedule_result = validate_schedule(state["schedule"], state["timezone"])
    assert state["policy_enabled"] is True
    return {"status": "PASS", **result, "lyric_patterns": len(patterns), **schedule_result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    p = subs.add_parser("profile")
    p.add_argument("--platform", required=True)
    p.add_argument("--mode", default="instrumental")
    p.add_argument("--max-chars", type=int)
    a = subs.add_parser("audit")
    a.add_argument("package", type=Path)
    subs.add_parser("validate")
    args = parser.parse_args()
    try:
        if args.command == "profile":
            result = resolve(args.platform, args.mode, args.max_chars)
        elif args.command == "audit":
            result = audit(json.loads(args.package.read_text(encoding="utf-8")))
        else:
            result = validate()
    except (AssertionError, ValueError, KeyError, TypeError, OSError) as error:
        result = {"status": "FAIL", "error": str(error)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("status") == "FAIL" else 2 if result.get("status") == "PENDING" else 0


if __name__ == "__main__":
    raise SystemExit(main())
