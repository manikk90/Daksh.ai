from datetime import datetime

import pytest

from ai_social.metrics_import import import_metrics_csv
from ai_social.models import IST, PostRecord
from ai_social.pullers.http import ApiError, norm_url, redact
from ai_social.pullers.instagram import pull_instagram
from ai_social.pullers.x import pull_x, status_id


def _p(pid, platform, url):
    return PostRecord(post_id=pid, platform=platform, published_at=datetime(2026, 10, 1, 19, 30, tzinfo=IST).isoformat(),
                      pillar="pipeline", format="reel", hook_type="result_first", language="hinglish", url=url)


def test_url_helpers():
    assert norm_url("https://www.instagram.com/reel/ABC/?igsh=1") == "instagram.com/reel/abc"
    assert norm_url("https://twitter.com/memanik2079/status/9") == norm_url("https://x.com/memanik2079/status/9/")
    assert "***" in redact("https://graph.instagram.com/v24.0/me/media?access_token=SECRET&limit=5")
    assert status_id("https://x.com/memanik2079/status/123?s=20") == "123"


def test_instagram_pull_matches_permalink_falls_back_and_reads_reels():
    calls = []

    def fake_get(url, headers):
        calls.append(url)
        if "/media?" in url:
            return {"data": [
                {"id": "m1", "permalink": "https://www.instagram.com/reel/AAA/", "media_product_type": "REELS"},
                {"id": "m2", "permalink": "https://www.instagram.com/p/ZZZ/", "media_product_type": "FEED"},
            ]}
        if "m1/insights" in url and "follows" in url:
            raise ApiError("metric not supported")
        if "m1/insights" in url and "ig_reels_avg_watch_time" in url:
            return {"data": [{"name": "ig_reels_avg_watch_time", "values": [{"value": 8400}]}]}
        if "m1/insights" in url:
            return {"data": [{"name": "reach", "values": [{"value": 5000}]}, {"name": "saved", "values": [{"value": 40}]}, {"name": "shares", "values": [{"value": 90}]}]}
        raise AssertionError(url)

    posts = [_p("ig-1", "instagram", "https://instagram.com/reel/AAA"), _p("li-1", "linkedin", "https://x")]
    [snap] = pull_instagram(posts, get=fake_get, env={"IG_ACCESS_TOKEN": "t"})
    assert snap.post_id == "ig-1"
    assert snap.metrics == {"reach": 5000.0, "saves": 40.0, "shares": 90.0, "avg_watch_time_ms": 8400.0}
    assert all("access_token=t" in c for c in calls)


def test_instagram_requires_token():
    with pytest.raises(ApiError):
        pull_instagram([_p("ig-1", "instagram", "https://instagram.com/reel/AAA")], get=lambda u, h: {}, env={})


def test_x_pull():
    def fake_get(url, headers):
        assert headers["Authorization"] == "Bearer b"
        if "/users/by/username/memanik2079" in url:
            return {"data": {"id": "42"}}
        if "/users/42/tweets" in url:
            return {"data": [
                {"id": "111", "public_metrics": {"impression_count": 900, "reply_count": 12, "retweet_count": 3, "like_count": 30, "quote_count": 1, "bookmark_count": 4}},
                {"id": "222", "public_metrics": {"impression_count": 10}},
            ]}
        raise AssertionError(url)

    posts = [_p("x-1", "x", "https://x.com/memanik2079/status/111")]
    [snap] = pull_x(posts, get=fake_get, env={"X_BEARER_TOKEN": "b"})
    assert snap.metrics["replies"] == 12 and snap.metrics["impressions"] == 900 and snap.metrics["bookmarks"] == 4


def test_x_pull_unknown_user():
    with pytest.raises(ApiError, match="could not resolve"):
        pull_x([_p("x-1", "x", "https://x.com/a/status/1")], get=lambda u, h: {"errors": ["nope"]}, env={"X_BEARER_TOKEN": "b"})


def test_import_metrics_csv(tmp_path):
    csv_file = tmp_path / "li.csv"
    csv_file.write_text(
        "Post URL,Impressions,Reactions,Comments,Shares,Saves,Sends\n"
        "https://www.linkedin.com/feed/update/urn:li:activity:1/,\"1,200\",40,6,3,22,9\n"
        "https://www.linkedin.com/feed/update/urn:li:activity:999,10,1,0,0,0,0\n"
        "https://www.linkedin.com/feed/update/urn:li:activity:2,-,,,,,\n",
        encoding="utf-8",
    )
    posts = [_p("li-1", "linkedin", "https://linkedin.com/feed/update/urn:li:activity:1"), _p("li-2", "linkedin", "https://linkedin.com/feed/update/urn:li:activity:2")]
    rep = import_metrics_csv(csv_file, "linkedin", posts, captured_at="2026-10-09T10:00:00+05:30")
    [snap] = rep.snapshots
    assert snap.metrics == {"impressions": 1200.0, "reactions": 40.0, "comments": 6.0, "reposts": 3.0, "saves": 22.0, "sends": 9.0}
    assert len(rep.unmatched) == 1 and len(rep.bad_rows) == 1
