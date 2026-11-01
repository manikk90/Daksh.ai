"""Regression: the shipped launch week must always pass the hard-rule validator."""
import json
from pathlib import Path

import pytest

from ai_social.validate import check_draft, check_plan

LAUNCH = Path(__file__).resolve().parents[1] / "assets" / "launch" / "2026-W44"
DRAFTS = sorted(LAUNCH.glob("w44-*.json"))


def test_launch_week_has_all_platforms():
    platforms = {json.loads(p.read_text(encoding="utf-8"))["platform"] for p in DRAFTS}
    assert platforms == {"linkedin", "instagram", "facebook", "x"}


@pytest.mark.parametrize("path", DRAFTS, ids=lambda p: p.stem)
def test_launch_draft_passes_without_warnings(path, repo):
    res = check_draft(json.loads(path.read_text(encoding="utf-8")), repo)
    assert res["pass"] and not res["warnings"], res


def test_launch_plan_passes(repo):
    res = check_plan(json.loads((LAUNCH / "plan.json").read_text(encoding="utf-8")), repo)
    assert res["pass"] and not res["warnings"], res


def test_ready_pack_renders_every_post(tmp_path):
    from ai_social.ready import render_ready

    md = render_ready(LAUNCH, "2026-W44")
    for path in DRAFTS:
        assert f"`{path.stem}`" in md
    assert "Needs your answer" in md and "| When | Platform |" in md


def test_ready_rejects_draft_without_slot(tmp_path):
    from ai_social.ready import render_ready

    (tmp_path / "a.json").write_text('{"post_id": "a", "text": "x"}', encoding="utf-8")
    with pytest.raises(ValueError, match="slot_ist"):
        render_ready(tmp_path, "w")
