"""Boundary checks for the real pinned module and the Daksh CLI bridge."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import ai_film


def run(*args, cwd=ROOT):
    return subprocess.run([sys.executable, str(ROOT / "tools/ai_film.py"), *map(str, args)],
                          cwd=cwd, capture_output=True, text=True, timeout=60)


def test_real_pin_and_inventory():
    result = ai_film.validate()
    assert result["controller"] == "daksh-brain"
    assert result["skills"] == 61
    assert result["provider_calls"] == 0


def test_media_workflows_preserve_writer_revision_and_owner_gates():
    from daksh_architecture import ancestors, load
    flows = {f["id"]: f for f in load(ROOT / "architecture/workflows.json")["workflows"]}
    viral = flows["ai-film-viral-studio"]["nodes"]
    by_id = {n["id"]: n for n in viral}
    assert by_id["script-revision"]["agent"] == "writer"
    assert by_id["script-revision"]["depends_on"] == ["script-critique"]
    assert by_id["script-gate"]["depends_on"] == ["script-revision"]
    assert {"script-gate", "look-gate"} <= ancestors(viral, "production")
    assert "final-cut-gate" in ancestors(viral, "publish-kit")
    mann = flows["ai-film-mann-edit"]["nodes"]
    assert {"style-gate", "script-gate", "storyboard-gate"} <= ancestors(mann, "render")
    for nodes in (viral, mann):
        for node in nodes:
            if "owner_gate" in node:
                assert node["agent"] == "daksh-brain"
                assert node["owner_gate"].strip()


@pytest.mark.parametrize("mutation, message", [
    (lambda d: d["source"].update(path="modules/missing"), "not initialized"),
    (lambda d: d["source"].update(path="../escape"), "escapes"),
    (lambda d: d["source"].update(commit="0" * 40), "differs"),
    (lambda d: d.update(controller="another-master"), "Daksh Brain"),
    (lambda d: d["role_mapping"].update(mann="imaginary-worker"), "Unknown Daksh owner"),
    (lambda d: d["workflow_ids"].append("imaginary-flow"), "Unknown AI-film workflow"),
])
def test_bad_source_and_mapping_refused(monkeypatch, mutation, message):
    original = ai_film.read_json
    config = deepcopy(original(ROOT / ai_film.MANIFEST))
    mutation(config)
    monkeypatch.setattr(ai_film, "read_json", lambda path: config if path == ROOT / ai_film.MANIFEST else original(path))
    with pytest.raises(ai_film.IntegrationError, match=message):
        ai_film.validate()


def test_inventory_cannot_drop_a_skill(monkeypatch):
    original = ai_film.read_json
    path = ROOT / "catalog/ai-film-skills.json"
    inventory = deepcopy(original(path))
    inventory["skills"].pop()
    monkeypatch.setattr(ai_film, "read_json", lambda p: inventory if p == path else original(p))
    with pytest.raises(ai_film.IntegrationError, match="omits or invents"):
        ai_film.validate()


def test_missing_module_returns_actionable_error_without_dispatch(monkeypatch, capsys):
    def missing():
        raise ai_film.IntegrationError("Run git submodule update --init --recursive -- modules/ai-film")
    monkeypatch.setattr(ai_film, "validate", missing)
    assert ai_film.main(["film", "init", "script.txt", "projects/demo"]) == 2
    assert "git submodule update" in capsys.readouterr().err


def test_real_production_roundtrip_from_foreign_directory(tmp_path):
    caller = tmp_path / "caller with spaces"
    caller.mkdir()
    script = caller / "कहानी.txt"
    script.write_text((ROOT / "modules/ai-film/examples/screenplay.txt").read_text(), encoding="utf-8")
    assert run("film", "init", script.name, "project with spaces", cwd=caller).returncode == 0
    assert (caller / "project with spaces").is_dir()
    plan = ROOT / "modules/ai-film/examples/plan.json"
    assert run("film", "set-plan", "project with spaces", plan, cwd=caller).returncode == 0
    audit = run("film", "audit", "project with spaces", cwd=caller)
    assert audit.returncode == 1
    assert json.loads(audit.stdout)["complete"] is False
    export = run("film", "export-shot", "project with spaces", "SH001", "export with spaces",
                 "--profile", ROOT / "modules/ai-film/profiles/portable-text.json", cwd=caller)
    assert export.returncode == 0, export.stderr
    assert (caller / "export with spaces/RUN_IN_TOOL.md").is_file()
    assert run("film", "audit", "missing-project", cwd=caller).returncode == 2


@pytest.mark.parametrize("command", ["film", "mann"])
def test_upstream_help_flags_reach_the_real_cli(command, tmp_path):
    result = run(command, "--help", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert ("export-shot" if command == "film" else "storyboard") in result.stdout


def test_production_outputs_are_ignored():
    for path in ("projects/demo/film.json", "exports/demo/video.mp4"):
        assert subprocess.run(["git", "check-ignore", "-q", path], cwd=ROOT).returncode == 0
