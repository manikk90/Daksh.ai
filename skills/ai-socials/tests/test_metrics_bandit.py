from datetime import datetime

import pytest

from ai_social.bandit import suggest
from ai_social.metrics import NORTH_STAR, mature_snapshot, score_posts
from ai_social.models import IST

from helpers import li_post, slot_experiment, snap


def test_mature_snapshot_picks_earliest_after_seven_days():
    p = li_post("a", datetime(2026, 9, 1, 8, tzinfo=IST))
    early, day8, day20 = snap(p, 3, impressions=10), snap(p, 8, impressions=100), snap(p, 20, impressions=900)
    assert mature_snapshot(p, [day20, early, day8]) == day8
    assert mature_snapshot(p, [early]) is None


def test_north_star_zero_denominator_is_none():
    assert NORTH_STAR["linkedin"]({"saves": 5}) is None
    assert NORTH_STAR["x"]({"impressions": 1000, "replies": 10}) == 20.0


def test_score_posts_normalises_against_baseline():
    posts, snaps = slot_experiment()
    scored = {s.post.post_id: s for s in score_posts(posts, snaps)}
    assert scored["wed-5"].raw == 60.0 and scored["tue-5"].raw == 20.0
    # wed-5 baseline: 6 earlier Tue (20) + 5 Wed (60) -> median 20
    assert scored["wed-5"].normalized == pytest.approx(3.0)
    # tue-5 baseline: 5 Tue + 5 Wed -> median 40
    assert scored["tue-5"].normalized == pytest.approx(0.5)


def test_cold_start_single_post_has_no_normalised_score():
    p = li_post("solo", datetime(2026, 9, 1, 8, tzinfo=IST))
    [only] = score_posts([p], [snap(p, 8, impressions=100, saves=1)])
    assert only.normalized is None


def test_bandit_explores_untried_arms_first():
    posts, snaps = slot_experiment()
    scored = score_posts(posts, snaps)
    out = suggest(scored, "linkedin", "slot", ["tue_1030", "wed_0800", "thu_0800"], seed=1)
    assert out["choice"] == "thu_0800" and "exploring" in out["reason"]


def test_bandit_prefers_winner_once_explored():
    posts, snaps = slot_experiment()
    scored = score_posts(posts, snaps)
    picks = [suggest(scored, "linkedin", "slot", ["tue_1030", "wed_0800"], seed=s)["choice"] for s in range(50)]
    assert picks.count("wed_0800") >= 45
    assert suggest(scored, "linkedin", "slot", ["tue_1030", "wed_0800"], seed=3) == suggest(scored, "linkedin", "slot", ["tue_1030", "wed_0800"], seed=3)


def test_bandit_requires_candidates():
    with pytest.raises(ValueError):
        suggest([], "linkedin", "slot", [])
