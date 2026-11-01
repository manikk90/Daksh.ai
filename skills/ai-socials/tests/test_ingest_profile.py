import json

import pytest

from ai_social.ingest import parse_linkedin_export, parse_meta_export, parse_x_archive
from ai_social.ingest.linkedin import author_and_slug
from ai_social.ingest.meta import fix_mojibake
from ai_social.liking_profile import build_liking_profile
from ai_social.storage import read_json


def test_linkedin_export(fixtures):
    events = list(parse_linkedin_export(fixtures / "linkedin"))
    kinds = [e.kind for e in events]
    assert kinds.count("reaction") == 3 and kinds.count("comment") == 1 and kinds.count("post") == 1
    first = events[0]
    assert first.target_author == "ankit-ai"
    assert "haryanvi ai dubbing pipeline" in first.text
    assert first.timestamp.startswith("2026-09-02T03:10:00")
    comment = next(e for e in events if e.kind == "comment")
    assert "Bhojpuri" in comment.text and "\n" in comment.text
    post = next(e for e in events if e.kind == "post")
    assert post.text.startswith("The Difference")


def test_linkedin_url_without_slug():
    assert author_and_slug("https://www.linkedin.com/feed/update/urn:li:activity:1") == ("", "")


def test_linkedin_missing_folder_yields_nothing(tmp_path):
    assert list(parse_linkedin_export(tmp_path)) == []


def test_meta_export_both_layouts_and_mojibake(fixtures):
    events = list(parse_meta_export(fixtures / "meta"))
    by_author = {e.target_author: e for e in events}
    assert {"aifilmmaker.in", "kling_ai", "regional.reels", "Ravi Sharma", "Sunita Devi"} <= set(by_author)
    assert by_author["regional.reels"].text == "बहुत बढ़िया काम bhai"
    assert by_author["Sunita Devi"].platform == "facebook" and by_author["Sunita Devi"].kind == "comment"
    assert by_author["Ravi Sharma"].kind == "reaction"
    assert by_author["kling_ai"].target_url == "https://www.instagram.com/p/BBB/"
    assert all("followers" not in e.source_file for e in events)


def test_fix_mojibake_leaves_clean_text():
    assert fix_mojibake("Jai Hanuman") == "Jai Hanuman"
    assert fix_mojibake("हनुमान") == "हनुमान"


def test_meta_invalid_json_names_file(tmp_path):
    bad = tmp_path / "your_instagram_activity" / "likes"
    bad.mkdir(parents=True)
    (bad / "liked_posts.json").write_text("{broken", encoding="utf-8")
    with pytest.raises(ValueError, match="liked_posts.json"):
        list(parse_meta_export(tmp_path))


def test_x_archive(fixtures):
    events = list(parse_x_archive(fixtures / "x"))
    kinds = [e.kind for e in events]
    assert kinds == ["post", "comment", "share", "like"]
    assert events[1].target_author == "kling_ai"
    like = events[-1]
    assert like.timestamp is None and like.target_author == "runwayml"


def test_x_archive_rejects_garbage(tmp_path):
    (tmp_path / "tweets.js").write_text("window.YTD.tweets.part0 = {nope", encoding="utf-8")
    with pytest.raises(ValueError):
        list(parse_x_archive(tmp_path))


def test_liking_profile_end_to_end(fixtures, repo):
    events = list(parse_linkedin_export(fixtures / "linkedin")) + list(parse_meta_export(fixtures / "meta")) + list(parse_x_archive(fixtures / "x"))
    pillars = read_json(repo.pillars)["pillars"]
    prof = build_liking_profile(events, pillars)
    json.dumps(prof)  # serialisable
    assert prof["total_events"] == len(events)
    assert prof["pillar_affinity"]["pipeline"] > 0
    assert any(a["author"] == "kling_ai" for a in prof["top_authors"])
    assert "linkedin" in prof["own_language_mix"]
    assert any("no timestamp" in n for n in prof["notes"])
    assert sum(prof["active_hours_ist"].values()) == sum(1 for e in events if e.timestamp)


def test_liking_profile_empty(repo):
    prof = build_liking_profile([], read_json(repo.pillars)["pillars"])
    assert prof["total_events"] == 0 and prof["top_topics"] == []
    assert "No export data" in prof["notes"][0]
    assert set(prof["pillar_affinity"]) == {"pipeline", "bharat_insight", "builder_log", "origin", "industry"}
