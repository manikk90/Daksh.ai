"""Behavioral gates for the design-time registry and its non-executing planner."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from daksh_architecture import SpecError, load, main, preview, safe_repo_path, validate, validate_agents, validate_workflows, waves


def test_complete_repository_specification():
    result = validate(ROOT)
    assert result["agents"] >= 28
    assert result["workflows"] >= 27
    assert result["provider_calls"] == result["executed_workers"] == 0


@pytest.mark.parametrize("mutator", [
    lambda d: d.update(root_agent_id="maniik"),
    lambda d: d["agents"][1].update(parent=None),
    lambda d: d["agents"].append(deepcopy(d["agents"][0])),
    lambda d: d["agents"][0].update(skill_paths=["../../private.md"]),
])
def test_wrong_hierarchy_duplicate_and_path_escape_rejected(mutator):
    data = load(ROOT / "architecture/agents.json")
    mutator(data)
    with pytest.raises(SpecError):
        validate_agents(data, ROOT)


@pytest.mark.parametrize("nodes", [
    [{"id":"a","depends_on":["b"]},{"id":"b","depends_on":["a"]}],
    [{"id":"a","depends_on":["missing"]}],
    [{"id":"a","depends_on":["a"]}],
])
def test_unrunnable_dependency_graphs_rejected(nodes):
    with pytest.raises(SpecError):
        waves(nodes)


def test_independent_work_parallel_and_dependencies_wait():
    nodes = [{"id":"a","depends_on":[]},{"id":"b","depends_on":[]},
             {"id":"c","depends_on":["a","b"]}]
    assert waves(nodes) == [["a","b"],["c"]]


def test_unknown_agent_and_bypassed_qc_rejected():
    agents = validate_agents(load(ROOT / "architecture/agents.json"), ROOT)
    for mutation in ("unknown", "bypass"):
        data = load(ROOT / "architecture/workflows.json")
        flow = next(w for w in data["workflows"] if w["id"] == "engineering-change")
        if mutation == "unknown":
            flow["nodes"][1]["agent"] = "imaginary-model"
        else:
            flow["nodes"][-1]["depends_on"] = ["implement"]
        with pytest.raises(SpecError):
            validate_workflows(data, agents)


def test_qc_of_intake_cannot_approve_later_implementation():
    agents = validate_agents(load(ROOT / "architecture/agents.json"), ROOT)
    data = load(ROOT / "architecture/workflows.json")
    flow = next(w for w in data["workflows"] if w["id"] == "engineering-change")
    flow["nodes"][-2]["depends_on"] = ["intake"]
    flow["nodes"][-1]["depends_on"] = ["tests", "review"]
    with pytest.raises(SpecError, match="every required production branch"):
        validate_workflows(data, agents)


def test_planner_blocks_missing_input_and_never_echoes_private_values():
    value = "PRIVATE-SYNOPSIS-DO-NOT-PRINT"
    result = preview(ROOT,"full-launch",{"synopsis":value},max_parallel=1)
    assert result["status"] == "missing_inputs"
    assert "audience" in result["missing_inputs"]
    assert value not in json.dumps(result)
    assert all(len(wave) <= 1 for wave in result["waves"])
    assert result["workers_launched"] == result["provider_calls"] == 0


def test_valid_inputs_create_preview_not_completion():
    result = preview(ROOT,"direct-task",{"objective":"Rewrite supplied text"})
    assert result["status"] == "plan_preview"
    assert result["workers_launched"] == 0


@pytest.mark.parametrize("objective", [False, True, 0, 1, {}, [], " ", "\t\n", None])
def test_missing_or_wrong_type_objective_never_becomes_ready(objective):
    result = preview(ROOT, "direct-task", {"objective": objective})
    assert result["status"] == "missing_inputs"
    assert result["missing_inputs"] == ["objective"]


def test_artifact_contract_preserves_unrun_checks():
    schema = load(ROOT / "architecture/contracts/artifact.schema.json")
    value = load(ROOT / "architecture/examples/artifact.example.json")
    assert any(c["outcome"] == "not_run" for c in value["checks"])
    Draft202012Validator(schema).validate(value)
    value["checks"][0]["outcome"] = "assumed_pass"
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(value)


def test_memory_candidate_rejects_unknown_scope_and_confidence():
    schema = load(ROOT / "architecture/contracts/memory-candidate.schema.json")
    value = load(ROOT / "architecture/examples/memory-candidate.example.json")
    value["confidence"] = 1.1
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(value)


def test_cli_missing_inputs_is_distinct_from_valid_plan(tmp_path, capsys):
    path = tmp_path / "inputs.json"
    path.write_text("{}")
    assert main(["plan","direct-task","--inputs",str(path)]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "missing_inputs"


def test_absolute_and_parent_paths_rejected():
    for value in ("/tmp/private", "../private"):
        with pytest.raises(SpecError):
            safe_repo_path(ROOT,value)
