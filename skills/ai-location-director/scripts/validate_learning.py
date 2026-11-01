#!/usr/bin/env python3
"""Validate persisted lessons and review metadata, not rendered quality."""
import argparse
import json
from pathlib import Path


def validate(data):
    errors = []

    def require(ok, message):
        if not ok:
            errors.append(message)

    if not isinstance(data, dict):
        return ["Ledger must be an object"]
    require(data.get("schema_version") == 1, "Unknown schema version")
    require(data.get("skill_name") == "ai-location-director", "Wrong skill ledger")
    require(type(data.get("version")) is int and data["version"] > 0, "Ledger version must be positive")
    lessons = data.get("lessons")
    require(isinstance(lessons, list), "lessons must be a list")
    ids, active_keys = {}, set()
    for lesson in lessons if isinstance(lessons, list) else []:
        if not isinstance(lesson, dict):
            errors.append("Lesson must be an object")
            continue
        lesson_id = lesson.get("id")
        require(isinstance(lesson_id, str) and bool(lesson_id), "Lesson ID missing")
        if not isinstance(lesson_id, str):
            continue
        require(lesson_id not in ids, "Duplicate lesson ID: " + lesson_id)
        ids[lesson_id] = lesson
        require(type(lesson.get("version")) is int and lesson["version"] > 0, lesson_id + ": version missing")
        require(lesson.get("status") in ["pending", "active", "superseded", "rejected"], lesson_id + ": invalid status")
        for field in ["trigger", "failure", "prevention"]:
            require(isinstance(lesson.get(field), str) and bool(lesson[field].strip()), lesson_id + ": " + field + " missing")
        source = lesson.get("source", {})
        if not isinstance(source, dict):
            errors.append(lesson_id + ": source must be an object")
            source = {}
        require(source.get("type") in ["user_feedback", "observed_failure", "primary_research"], lesson_id + ": source type missing")
        require(bool(source.get("evidence")), lesson_id + ": source evidence missing")
        if source.get("type") == "primary_research":
            require(isinstance(source.get("url"), str) and source["url"].startswith("https://"), lesson_id + ": primary-source URL missing")
            require(bool(source.get("accessed_date")), lesson_id + ": source access date missing")
        scope = lesson.get("scope", {})
        if not isinstance(scope, dict):
            errors.append(lesson_id + ": scope must be an object")
            scope = {}
        kind = scope.get("kind")
        require(kind in ["global-workflow", "tool", "project", "location", "shot"], lesson_id + ": scope invalid")
        if kind in ["project", "location", "shot"]:
            require(bool(scope.get("project_id")), lesson_id + ": project scope missing")
        if kind in ["location", "shot"]:
            require(bool(scope.get("location_id")), lesson_id + ": location scope missing")
        if kind == "shot":
            require(bool(scope.get("shot_id")), lesson_id + ": shot scope missing")
        if kind == "tool":
            require(bool(scope.get("tool_id")) and bool(scope.get("interface_version")), lesson_id + ": tool/interface version missing")
        cases = lesson.get("regression_cases", [])
        require(isinstance(cases, list) and len(cases) >= 2, lesson_id + ": include failure and boundary cases")
        case_ids = set()
        for case in cases if isinstance(cases, list) else []:
            if not isinstance(case, dict):
                errors.append(lesson_id + ": invalid regression case")
                continue
            for field in ["id", "input", "expected"]:
                require(isinstance(case.get(field), str) and bool(case[field].strip()), lesson_id + ": case " + field + " missing")
            case_id = case.get("id")
            require(isinstance(case_id, str) and case_id not in case_ids, lesson_id + ": duplicate case ID")
            if isinstance(case_id, str):
                case_ids.add(case_id)
        validation = lesson.get("validation", {})
        if not isinstance(validation, dict):
            errors.append(lesson_id + ": validation must be an object")
            validation = {}
        require(validation.get("result") in ["PASS", "FAIL", "PENDING"], lesson_id + ": validation result missing")
        if lesson.get("status") == "active":
            require(validation.get("result") == "PASS" and bool(validation.get("evidence")), lesson_id + ": active lesson lacks passed evidence")
            require(validation.get("kind") in ["user-directed-scope", "instruction-regression", "structural-test", "render-comparison", "documentation-check"], lesson_id + ": validation kind missing")
            if validation.get("kind") == "user-directed-scope":
                require(source.get("type") == "user_feedback" and kind != "global-workflow", lesson_id + ": user-scope validation cannot certify an inferred global rule")
            key = (json.dumps(scope, sort_keys=True), lesson.get("trigger"))
            require(key not in active_keys, lesson_id + ": duplicate active rule trigger/scope")
            active_keys.add(key)
    for lesson_id, lesson in ids.items():
        if lesson.get("supersedes"):
            old = lesson["supersedes"]
            require(isinstance(old, str) and old in ids and old != lesson_id, lesson_id + ": superseded ID invalid")
            if isinstance(old, str) and old in ids and lesson.get("status") == "active":
                require(ids[old].get("status") == "superseded", lesson_id + ": replaced rule still active")
    schedule = data.get("schedule", {})
    if not isinstance(schedule, dict):
        errors.append("Schedule must be an object")
        schedule = {}
    require(schedule.get("cadence") == "P1D", "Nightly chat review requires daily cadence")
    require(schedule.get("timezone") == "Asia/Kolkata", "Unexpected schedule timezone")
    require(schedule.get("status") in ["pending", "enabled", "paused"], "Schedule status invalid")
    specific_midnight = schedule.get("mode") == "user_specific_daily_override"
    require(specific_midnight or schedule.get("mode") == "one_coordinator_with_weekly_branch",
            "Unknown daily schedule ownership mode")
    require(schedule.get("coordinator") == ("ai-location-director" if specific_midnight else "daksh"),
            "Schedule owner disagrees with the user-specific exception")
    if specific_midnight:
        require(schedule.get("excluded_from_daksh_coordinator") is True,
                "Location midnight exception must be excluded from duplicate coordinator execution")
    time = "00:00" if specific_midnight else "23:00"
    research_day = "MO" if specific_midnight else "SU"
    daily, weekly = schedule.get("daily_chat_review", {}), schedule.get("weekly_research", {})
    require(isinstance(daily, dict) and daily.get("cadence") == "P1D"
            and daily.get("not_before") == time, "Nightly chat time disagrees with the observed schedule")
    require(isinstance(weekly, dict) and weekly.get("day") == research_day
            and weekly.get("not_before") == time
            and weekly.get("mode") == "conditional_branch_in_same_daily_automation",
            "Research must use the same task: Monday midnight (Sunday night ending) for the Location exception")
    schedule_text = schedule.get("schedule", "")
    require(isinstance(schedule_text, str) and bool(schedule_text), "Daily schedule required")
    if isinstance(schedule_text, str):
        rule = next((line for line in schedule_text.splitlines() if line.startswith("RRULE:")), "")
        parts = set(rule.removeprefix("RRULE:").split(";"))
        require("FREQ=DAILY" in parts and not any(part.startswith("BYDAY=") for part in parts)
                and all(part == "INTERVAL=1" for part in parts if part.startswith("INTERVAL=")),
                "Coordinator trigger must run every day")
        start = next((line for line in schedule_text.splitlines() if line.startswith("DTSTART")), "")
        require("TZID=Asia/Kolkata" in start and start.endswith("T000000" if specific_midnight else "T230000"),
                "Schedule must use its confirmed Asia/Kolkata start")
    if schedule.get("status") in ["enabled", "paused"]:
        require(bool(schedule.get("automation_id")) and schedule.get("confirmation_pending") is False
                and type(schedule.get("is_enabled")) is bool and bool(schedule.get("verified_on")),
                "Confirmed schedule requires observed identity, enabled state and verification date")
        require(schedule.get("is_enabled") is (schedule.get("status") == "enabled"),
                "Schedule status disagrees with enabled state")
    elif schedule.get("status") == "pending":
        require(schedule.get("confirmation_pending") is True and schedule.get("is_enabled") is not True,
                "Unconfirmed schedule must remain pending")
    reviews = data.get("research_reviews", [])
    require(isinstance(reviews, list), "research_reviews must be a list")
    for review in reviews if isinstance(reviews, list) else []:
        if not isinstance(review, dict):
            errors.append("Invalid research review")
            continue
        require(bool(review.get("id")) and bool(review.get("reviewed_at")), "Review ID/date missing")
        require(review.get("save_outcome") in ["saved", "pending", "no-change"], "Review save outcome invalid")
        require(isinstance(review.get("sources"), list), "Review sources must be a list")
        for lesson_id in review.get("adopted_lesson_ids", []):
            require(isinstance(lesson_id, str) and lesson_id in ids, "Review references unknown lesson")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()
    try:
        errors = validate(json.loads(args.ledger.read_text()))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        errors = ["Invalid ledger: " + str(exc)]
    print(json.dumps({"structure": "FAIL" if errors else "PASS", "errors": errors, "note": "Metadata checks only; execute the documented behavioral/visual cases separately."}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
