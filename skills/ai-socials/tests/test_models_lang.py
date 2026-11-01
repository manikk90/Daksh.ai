from datetime import datetime, timezone

import pytest

from ai_social.lang import detect_language
from ai_social.models import MetricSnapshot, PostRecord, ValidationError, parse_ts, slot_label


def _post(**kw):
    base = dict(post_id="p1", platform="linkedin", published_at="2026-10-21T08:15", pillar="pipeline",
                format="carousel", hook_type="constraint_number", language="en")
    base.update(kw)
    return PostRecord(**base)


def test_post_roundtrip_and_slot():
    p = _post(hashtags=("#AIFilmmaking",))
    again = PostRecord.from_dict({**p.to_dict(), "unknown_future_field": 1})
    assert again == p
    assert p.slot == "wed_0800"
    assert p.dimension("slot") == "wed_0800"
    assert p.dimension("hook_type") == "constraint_number"


@pytest.mark.parametrize("field,value", [("platform", "tiktok"), ("format", "story"), ("hook_type", "x"), ("language", "fr"), ("post_id", "  ")])
def test_post_rejects_bad_values(field, value):
    with pytest.raises(ValidationError):
        _post(**{field: value})


def test_dimension_rejects_non_learnable():
    with pytest.raises(ValidationError):
        _post().dimension("text")


def test_naive_timestamps_are_ist_and_utc_converts():
    assert parse_ts("2026-10-21T08:15").utcoffset().total_seconds() == 19800
    assert slot_label(datetime(2026, 10, 21, 2, 50, tzinfo=timezone.utc)) == "wed_0800"
    with pytest.raises(ValidationError):
        parse_ts("not a date")


def test_metric_snapshot_validation():
    MetricSnapshot("p1", "x", "2026-10-28T10:00:00Z", {"impressions": 100})
    with pytest.raises(ValidationError):
        MetricSnapshot("p1", "x", "2026-10-28T10:00:00Z", {"impressions": -1})


@pytest.mark.parametrize("text,expected", [
    ("जय हनुमान, नया एपिसोड आ गया", "hi"),
    ("Bhai ye shot ek insaan ne banaya hai, crew nahi tha", "hinglish"),
    ("Six dialects, one creator, every week.", "en"),
    ("", "en"),
    ("Jai Hanuman 🙏 नया episode", "hinglish"),
])
def test_detect_language(text, expected):
    assert detect_language(text) == expected
