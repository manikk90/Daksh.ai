import json
from datetime import timedelta

from ai_social.cli import main
from ai_social.storage import read_json

from helpers import slot_experiment


def test_cli_full_loop(repo, tmp_path, capsys):
    home = ["--home", str(repo.root)]
    posts, snaps = slot_experiment()
    post_file = tmp_path / "posts.json"
    post_file.write_text(json.dumps([p.to_dict() for p in posts]), encoding="utf-8")
    assert main(home + ["log-post", str(post_file)]) == 0

    rows = ["post_id,impressions,saves"] + [f"{s.post_id},{int(s.metrics['impressions'])},{int(s.metrics['saves'])}" for s in snaps]
    csv_file = tmp_path / "m.csv"
    csv_file.write_text("\n".join(rows) + "\n", encoding="utf-8")
    captured = (posts[-1].published_dt + timedelta(days=9)).isoformat()
    assert main(home + ["import-metrics", "--platform", "linkedin", "--csv", str(csv_file), "--captured-at", captured]) == 0

    assert main(home + ["retro", "--today", "2026-09-30"]) == 0
    capsys.readouterr()
    diff_path = repo.retro / "2026-W40.diff.json"
    assert diff_path.exists() and (repo.retro / "2026-W40.md").exists()

    assert main(home + ["apply-diff", str(diff_path)]) == 1  # no --approve
    assert main(home + ["apply-diff", str(diff_path), "--approve"]) == 0
    assert read_json(repo.playbook_rules)["version"] == 2

    assert main(home + ["suggest", "--platform", "linkedin", "--dimension", "slot", "--seed", "1"]) == 0
    assert main(home + ["status"]) == 0


def test_cli_ingest_and_profile(repo, fixtures, capsys):
    home = ["--home", str(repo.root)]
    assert main(home + ["ingest", "--linkedin", str(fixtures / "linkedin"), "--meta", str(fixtures / "meta"), "--x", str(fixtures / "x")]) == 0
    first = capsys.readouterr().out
    assert main(home + ["ingest", "--linkedin", str(fixtures / "linkedin")]) == 0
    assert '"new_events": 0' in capsys.readouterr().out  # idempotent
    assert main(home + ["profile"]) == 0
    assert read_json(repo.liking_profile)["total_events"] == json.loads(first)["total_events"]


def test_cli_errors_are_exit_codes(repo, capsys):
    home = ["--home", str(repo.root)]
    assert main(home + ["ingest"]) == 2
    assert main(home + ["apply-diff", "nope.json", "--approve"]) == 2


def test_log_post_straight_from_a_draft(repo):
    from pathlib import Path

    from ai_social.metrics import load_posts

    draft = Path(__file__).resolve().parents[1] / "assets" / "launch" / "2026-W44" / "w44-x-1.json"
    home = ["--home", str(repo.root)]
    assert main(home + ["log-post", str(draft), "--url", "https://x.com/memanik2079/status/123"]) == 0
    [post] = load_posts(repo)
    assert post.post_id == "w44-x-1" and post.url.endswith("/123") and post.slot == "tue_2030"
