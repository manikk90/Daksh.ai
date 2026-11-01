from ai_social.storage import Paths, append_jsonl, iter_jsonl

import pytest


def test_from_env_walks_up_to_repo_root(repo, monkeypatch):
    monkeypatch.delenv("AI_SOCIAL_HOME", raising=False)
    deep = repo.root / "drafts" / "2026-W44"
    deep.mkdir(parents=True)
    assert Paths.from_env(deep).root == repo.root


def test_from_env_prefers_env_var(repo, monkeypatch, tmp_path):
    monkeypatch.setenv("AI_SOCIAL_HOME", str(tmp_path))
    assert Paths.from_env(repo.root).root == tmp_path.resolve()


def test_jsonl_roundtrip_and_bad_line(tmp_path):
    f = tmp_path / "x.jsonl"
    assert append_jsonl(f, [{"a": 1}, {"b": "हनुमान"}]) == 2
    assert list(iter_jsonl(f)) == [{"a": 1}, {"b": "हनुमान"}]
    f.write_text('{"ok": 1}\n{broken\n', encoding="utf-8")
    with pytest.raises(ValueError, match=":2:"):
        list(iter_jsonl(f))
