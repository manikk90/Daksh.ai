import json

from ai_social.validate import check_draft, check_file, check_plan


def draft(**kw):
    base = {
        "post_id": "w44-li-1", "platform": "linkedin", "pillar": "pipeline", "format": "text",
        "hook_type": "constraint_number", "language": "en",
        "text": "Six dialects. One creator. Every week.\n\nHere is how the dubbing step works.",
        "hashtags": ["#AIFilmmaking"], "contains_ai_media": False, "ai_label": False, "experiment_id": "control",
    }
    base.update(kw)
    return base


def test_clean_draft_passes(repo):
    res = check_draft(draft(), repo)
    assert res["pass"], res


def test_schema_failure_blocks(repo):
    res = check_draft(draft(platform="tiktok"), repo)
    assert not res["pass"] and res["blocking"][0].startswith("schema")


def test_hashtag_cap_counts_inline_and_list(repo):
    res = check_draft(draft(text="Hook #one #two #three", hashtags=["#four"]), repo)
    assert not res["pass"] and "cap is 3" in res["blocking"][0]
    assert check_draft(draft(platform="instagram", format="reel", text="Hook #a #b #c #d", hashtags=["#e"]), repo)["pass"]


def test_links_blocked_on_linkedin_allowed_on_facebook(repo):
    body = "Six dialects. One creator.\nRead more https://indiantelevision.com/story"
    assert not check_draft(draft(text=body), repo)["pass"]
    assert check_draft(draft(platform="facebook", language="hinglish", text=body), repo)["pass"]
    assert check_draft(draft(text="Hook line here", first_comment="https://indiantelevision.com/story"), repo)["pass"]


def test_confidential_terms_block(repo):
    res = check_draft(draft(text="Built this inside cut.stage.in last night"), repo)
    assert any("confidential" in b for b in res["blocking"])


def test_national_first_needs_qualifier(repo):
    assert not check_draft(draft(text="India's first AI vertical series."), repo)["pass"]
    assert check_draft(draft(text="Solo-made, and to my knowledge India's first AI vertical series in six dialects."), repo)["pass"]
    assert not check_draft(draft(language="hi", text="भारत की पहली AI सीरीज़"), repo)["pass"]


def test_ai_media_needs_label(repo):
    res = check_draft(draft(platform="instagram", format="reel", contains_ai_media=True, ai_label=False), repo)
    assert any("AI label" in b for b in res["blocking"])


def test_x_length_limit_per_thread_part(repo):
    ok = draft(platform="x", format="thread", text="Hook", thread=["a" * 200, "b" * 250])
    assert check_draft(ok, repo)["pass"]
    bad = draft(platform="x", format="thread", text="Hook", thread=["a" * 200, "b" * 300])
    assert any("part 2" in b for b in check_draft(bad, repo)["blocking"])


def test_humanizer_warnings_do_not_block(repo):
    res = check_draft(draft(text="Let's dive in \u2014 this is a game-changer for everyone in the industry today, agree?"), repo)
    assert res["pass"]
    joined = " ".join(res["warnings"])
    assert "em dash" in joined and "dive in" in joined and "game-changer" in joined and "bait" in joined and "hook line" in joined


def _plan(posts):
    return {"week": "2026-W44", "posts": posts}


def _pp(i, platform="linkedin", slot="2026-10-27T08:00", pillar="pipeline", exp="control"):
    return {"post_id": f"p-{i}", "platform": platform, "pillar": pillar, "format": "text", "hook_type": "contrarian",
            "language": "en", "slot_ist": slot, "experiment_id": exp, "idea": "a concrete idea here"}


def test_plan_rules(repo):
    good = _plan([_pp(1, exp="exp-li-hinglish"), _pp(2, slot="2026-10-28T08:00"), _pp(3, "instagram", "2026-10-27T19:30", "bharat_insight")])
    assert check_plan(good, repo)["pass"]
    clash = _plan([_pp(1, exp="e"), _pp(2), _pp(3, "x", "2026-10-27T20:30")])
    assert any("2 posts on linkedin" in b for b in check_plan(clash, repo)["blocking"])
    no_exp = _plan([_pp(i, slot=f"2026-10-2{i}T08:00") for i in range(1, 4)])
    assert any("explore budget" in b for b in check_plan(no_exp, repo)["blocking"])
    unknown = _plan([_pp(1, pillar="memes", exp="e")])
    assert any("unknown pillar" in b for b in check_plan(unknown, repo)["blocking"])


def test_check_file_eval_consistency_and_bad_json(repo, tmp_path):
    ev = {"post_id": "p", "scores": {"hook_strength": 8, "voice_match": 8, "originality": 8, "platform_fit": 8, "factual_safety": 8, "confidentiality": 9}, "pass": True, "blocking_issues": [], "fix_instructions": []}
    f = tmp_path / "e.json"
    f.write_text(json.dumps(ev), encoding="utf-8")
    assert not check_file("eval", f, repo)["pass"]
    f.write_text("{oops", encoding="utf-8")
    assert "invalid JSON" in check_file("draft", f, repo)["blocking"][0]
