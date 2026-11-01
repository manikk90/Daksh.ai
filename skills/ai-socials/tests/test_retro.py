from datetime import date

import pytest

from ai_social.metrics import score_posts
from ai_social.retro import DiffRejected, apply_diff, bootstrap_ci, bootstrap_ratio_ci, propose_diff
from ai_social.storage import read_json

from helpers import slot_experiment


def _diff(repo, today=date(2026, 9, 30), weeks=6):
    posts, snaps = slot_experiment(weeks)
    rules = read_json(repo.playbook_rules)
    return propose_diff(score_posts(posts, snaps), rules, today), rules


def test_retro_confirms_seed_and_learns_avoid(repo):
    diff, _ = _diff(repo)
    assert any(c["rule_id"] == "linkedin:slot:wed_0800" for c in diff["confirmations"])
    avoid = [c for c in diff["changes"] if c["rule_id"] == "linkedin:slot:tue_1030"]
    assert avoid and avoid[0]["direction"] == "avoid" and avoid[0]["action"] == "add"
    assert avoid[0]["n"] == 6 and avoid[0]["lift_vs_rest_pct"] < -20
    assert set(avoid[0]["evidence_post_ids"]) == {f"tue-{k}" for k in range(6)}
    assert diff["guards"]["changes_within_cap"] and diff["guards"]["only_learnable_dimensions"]


def test_retro_small_sample_changes_nothing(repo):
    diff, _ = _diff(repo, weeks=2)
    assert diff["changes"] == [] and diff["confirmations"] == []
    assert diff["version_to"] == diff["version_from"]


def test_retro_expires_unconfirmed_rules_and_caps_changes(repo):
    diff, _ = _diff(repo, today=date(2027, 2, 1))
    assert len(diff["changes"]) == 3
    assert diff["deferred_changes"]
    assert any("unconfirmed" in c["reason"] for c in diff["changes"])


def test_apply_diff_requires_approval_and_matching_version(repo):
    diff, rules = _diff(repo)
    with pytest.raises(DiffRejected, match="approve"):
        apply_diff(rules, diff, approve=False)
    with pytest.raises(DiffRejected, match="re-run retro"):
        apply_diff({**rules, "version": 9}, diff, approve=True)
    new = apply_diff(rules, diff, approve=True, today=date(2026, 9, 30))
    assert new["version"] == 2
    ids = {r["id"]: r for r in new["rules"]}
    assert ids["linkedin:slot:tue_1030"]["origin"] == "learned"
    assert ids["linkedin:slot:wed_0800"]["last_confirmed"] == "2026-09-30"
    assert new["changelog"][-1]["version"] == 2


def test_apply_diff_rejects_hard_rule_dimension(repo):
    diff, rules = _diff(repo)
    diff["changes"] = [{**diff["changes"][0], "dimension": "hashtags"}]
    with pytest.raises(DiffRejected, match="hard rule"):
        apply_diff(rules, diff, approve=True)


def test_uniform_dimension_never_becomes_a_rule(repo):
    diff, _ = _diff(repo)
    touched = {c["rule_id"] for c in diff["changes"]} | {c["rule_id"] for c in diff["confirmations"]}
    assert not any(r.startswith(("linkedin:pillar", "linkedin:format", "linkedin:language", "linkedin:hook_type")) for r in touched)


def test_bootstrap_ci_edges():
    assert bootstrap_ci([1.2]) == (1.2, 1.2)
    lo, hi = bootstrap_ci([0.8, 1.0, 1.2, 1.4])
    assert lo < 1.1 < hi
    with pytest.raises(ValueError):
        bootstrap_ci([])
    lo, hi = bootstrap_ratio_ci([2.0, 2.2, 1.8, 2.1], [1.0, 0.9, 1.1, 1.0])
    assert 1.5 < lo <= hi < 2.6
    with pytest.raises(ValueError):
        bootstrap_ratio_ci([1.0], [])
