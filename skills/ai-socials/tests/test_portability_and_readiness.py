import json
from pathlib import Path

import pytest

from ai_social.validate import check_draft, check_file, check_plan
from social import SKILL_ROOT, initialize


def post(**kw):
    p = dict(post_id="new-1", platform="linkedin", pillar="pipeline", format="text",
             hook_type="story_open", language="en", text="A consistent face takes work.",
             hashtags=[], contains_ai_media=False, ai_label=False, experiment_id="control")
    return {**p, **kw}


def test_comment_cannot_bypass_confidentiality(repo):
    res = check_draft(post(first_comment="The tool is at cut.stage.in"), repo)
    assert not res["pass"] and not res["ready_to_publish"]
    assert any("confidential" in b for b in res["blocking"])


def test_clearance_pending_draft_is_valid_but_not_ready(repo):
    res = check_draft(post(confirm=["Permission to show rejected frames is pending"]), repo)
    assert res["pass"] and not res["ready_to_publish"]
    assert check_draft(post(), repo)["ready_to_publish"]


def test_visible_unknown_cannot_be_ready(repo):
    assert not check_draft(post(text="This saved ⟦confirm: minutes⟧ per shot."), repo)["ready_to_publish"]


def test_high_scores_do_not_override_evaluator_blockers(repo, tmp_path):
    scores = {k: 8 for k in ("hook_strength", "voice_match", "originality", "platform_fit", "factual_safety")}
    scores["confidentiality"] = 10
    p = tmp_path / "eval.json"
    p.write_text(json.dumps(dict(post_id="new-1", scores=scores, **{"pass": True},
        blocking_issues=["Unverified personal benchmark"], fix_instructions=["Remove claim"])))
    assert not check_file("eval", p, repo)["pass"]


def test_experiment_budget_really_reaches_thirty_percent(repo):
    posts = [dict(post_id=f"plan-{i}", platform="linkedin", pillar="pipeline", format="text",
        hook_type="story_open", language="en", slot_ist=f"2026-10-{21+i}T08:00",
        experiment_id="trial" if i==0 else "control", idea="Explain a specific real workflow.") for i in range(4)]
    assert not check_plan(dict(week="2026-W43", posts=posts), repo)["pass"]


def test_init_keeps_examples_out_of_logs_and_preserves_state(tmp_path):
    initialize(tmp_path)
    assert not (tmp_path / "logs" / "posts.jsonl").exists()
    assert len(list((tmp_path / "examples" / "2026-W44").glob("w44-*.json"))) == 9
    state = tmp_path / "brain" / "playbook_rules.json"
    state.write_text('{"version": 77}')
    initialize(tmp_path)
    assert json.loads(state.read_text())["version"] == 77


def test_init_refuses_installed_skill():
    with pytest.raises(ValueError):
        initialize(SKILL_ROOT)
