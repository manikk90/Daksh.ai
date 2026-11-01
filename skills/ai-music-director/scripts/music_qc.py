#!/usr/bin/env python3
"""Check music text and saved resource contracts; does not evaluate audio quality."""
import argparse
import json
from datetime import date
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def check_resources(root):
    registry = read_json(root / "assets/model-registry.json")
    ledger = read_json(root / "assets/learning-ledger.json")
    date.fromisoformat(registry["checked_at"])
    platforms = registry["platforms"]
    assert len({p["id"] for p in platforms}) == len(platforms), "Duplicate platform IDs"
    for platform in platforms:
        assert platform["sources"], f"Missing official sources: {platform['id']}"
        assert platform["documentation_status"] == "DOC_VERIFIED"
        for source in platform["sources"]:
            assert source["url"].startswith("https://"), "Source must be an HTTPS URL"
            date.fromisoformat(source["checked_at"])
            if source["published_at"]:
                date.fromisoformat(source["published_at"])
    lessons = ledger["lessons"]
    assert len({x["id"] for x in lessons}) == len(lessons), "Duplicate lesson IDs"
    for lesson in lessons:
        for field in ("scope", "source_kind", "source", "rule", "boundary", "validation"):
            assert lesson.get(field), f"Missing {field}: {lesson['id']}"
        assert lesson["status"] in {"active", "pending", "superseded", "rejected"}
        assert isinstance(lesson["version"], int) and lesson["version"] >= 1
        date.fromisoformat(lesson["recorded_at"])
        assert lesson["validation"].get("kind") and lesson["validation"].get("evidence")
    for required in ("agents/music-director.md", "references/project-music-context.md",
                     "references/scene-scoring.md", "references/instrument-palette.md",
                     "references/lyrics-and-vocal-direction.md", "references/platform-workflows.md",
                     "references/continuous-learning.md", "references/autonomous-runtime.md",
                     "references/vocal-micro-expression.md", "references/smart-parameters.md",
                     "assets/control-profiles.json", "assets/lyric-patterns.json",
                     "assets/improvement-state.json", "scripts/music_runtime.py"):
        assert (root / required).is_file(), f"Missing resource: {required}"
    return {"platforms": len(platforms), "lessons": len(lessons)}


def check_styles(path, max_chars, instrumental):
    # Strip file terminator whitespace, not any internal prompt content.
    value = Path(path).read_text(encoding="utf-8").strip()
    assert value and "```" not in value, "Supply raw pasteable Styles content"
    assert len(value) <= max_chars, f"Styles has {len(value)} characters; maximum {max_chars}"
    if instrumental:
        lowered = value.lower()
        required = ("instrumental", "no vocals", "no lyrics", "no spoken word", "no choir")
        missing = [term for term in required if term not in lowered]
        assert not missing, f"Missing instrumental constraints: {', '.join(missing)}"
    return {"characters": len(value), "max_characters": max_chars,
            "scope": "Length and required phrases only; semantic and audio checks remain separate"}


def integer(value, low, high, label):
    assert type(value) is int and low <= value <= high, f"{label} must be integer {low}..{high}"


def check_eleven(path):
    value = path if isinstance(path, dict) else read_json(path)
    profile = read_json(Path(__file__).resolve().parents[1] / "assets/control-profiles.json")["profiles"]["eleven-music"]
    limits = profile["chunk_limits"]
    assert isinstance(value, dict), "Request must be an object"
    prompt_mode = value.get("prompt") is not None
    plan_mode = value.get("composition_plan") is not None
    assert prompt_mode != plan_mode, "Provide exactly one of prompt or composition_plan"
    model = value.get("model_id")
    assert model in profile["models"], "Explicit checked Music model ID required"
    for name in ("store_for_inpainting", "respect_sections_durations", "sign_with_c2pa"):
        if name in value:
            assert type(value[name]) is bool, f"{name} must be boolean"
    if value.get("finetune_id") is not None:
        assert isinstance(value["finetune_id"], str) and len(value["finetune_id"]) <= 100, "finetune_id must be a string of at most 100 characters"
    if prompt_mode:
        prompt = value["prompt"]
        cap = profile["styles_hard_max"]
        assert isinstance(prompt, str) and 0 < len(prompt) <= cap, f"Prompt must have 1..{cap} characters"
        assert value.get("seed") is None, "Checked API does not accept seed with prompt"
        if value.get("music_length_ms") is not None:
            integer(value["music_length_ms"], limits["total_min_ms"], limits["total_max_ms"], "music_length_ms")
        if "force_instrumental" in value:
            assert type(value["force_instrumental"]) is bool, "force_instrumental must be boolean"
        return {"mode": "prompt", "model": model}
    assert value.get("music_length_ms") is None, "Use chunk durations, not music_length_ms with plan"
    assert "force_instrumental" not in value, "force_instrumental is prompt-only in checked API"
    if value.get("seed") is not None:
        integer(value["seed"], 0, 2147483647, "seed")
    assert model in {"music_v2", "music_v2_5"}, "This checker validates v2 chunk plans, not v1 plans"
    plan = value["composition_plan"]
    assert isinstance(plan, dict) and "sections" not in plan, "Do not mix v1 section schema into v2 plans"
    chunks = plan.get("chunks")
    assert isinstance(chunks, list) and 1 <= len(chunks) <= limits["count_max"], "Chunk count outside verified limits"
    total = 0
    for index, chunk in enumerate(chunks):
        assert isinstance(chunk, dict), f"Chunk {index} must be an object"
        assert isinstance(chunk.get("text"), str), f"Chunk {index} needs text"
        integer(chunk.get("duration_ms"), limits["duration_min_ms"], limits["duration_max_ms"], f"Chunk {index} duration_ms")
        total += chunk["duration_ms"]
        for field in ("positive_styles", "negative_styles"):
            items = chunk.get(field, [] if field == "negative_styles" else None)
            assert isinstance(items, list) and len(items) <= limits["styles_count_max"], f"Chunk {index} {field} invalid"
            assert all(isinstance(item, str) for item in items), f"Chunk {index} styles must be strings"
        assert chunk.get("context_adherence", "high") in {"low", "medium", "high"}
    integer(total, limits["total_min_ms"], limits["total_max_ms"], "Total duration_ms")
    return {"mode": "chunk_plan", "model": model, "chunks": len(chunks), "total_duration_ms": total}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-resources", action="store_true")
    parser.add_argument("--styles-file", type=Path)
    parser.add_argument("--max-chars", type=int, default=800)
    parser.add_argument("--instrumental", action="store_true")
    parser.add_argument("--eleven-request", type=Path)
    args = parser.parse_args()
    if not any((args.validate_resources, args.styles_file, args.eleven_request)):
        parser.error("Choose --validate-resources, --styles-file or --eleven-request")
    if args.instrumental and not args.styles_file:
        parser.error("--instrumental requires --styles-file")
    results = {}
    try:
        if args.validate_resources:
            results["resources"] = check_resources(Path(__file__).resolve().parents[1])
        if args.styles_file:
            results["styles"] = check_styles(args.styles_file, args.max_chars, args.instrumental)
        if args.eleven_request:
            results["eleven_request"] = check_eleven(args.eleven_request)
    except (AssertionError, ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps({"status": "PASS", "checks": results,
                      "evidence_type": "text_contract_only", "audio_review": "NOT_PERFORMED"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
