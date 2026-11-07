#!/usr/bin/env python3
"""Validate the Daksh specification and preview a DAG. Never execute a worker.

JSON schemas are checked with jsonschema when installed. The structural checks and
plan preview use only the standard library and never contact an external service.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class SpecError(ValueError):
    """A source specification is inconsistent or unsafe to interpret."""


def load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SpecError(f"Cannot read valid JSON at {path}: {exc}") from exc


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SpecError(message)


def unique(items: list[dict], label: str) -> dict[str, dict]:
    result = {}
    for item in items:
        ident = item.get("id")
        require(isinstance(ident, str) and bool(re.fullmatch(r"[a-z][a-z0-9-]*", ident)),
                f"{label}: invalid id {ident!r}")
        require(ident not in result, f"{label}: duplicate id {ident}")
        result[ident] = item
    return result


def safe_repo_path(root: Path, value: str) -> Path:
    require(isinstance(value, str) and bool(value), "Repository path must be nonblank text")
    require(not Path(value).is_absolute(), f"Absolute source path forbidden: {value}")
    path = (root / value).resolve()
    require(path.is_relative_to(root.resolve()), f"Source path escapes repository: {value}")
    return path


def waves(nodes: list[dict]) -> list[list[str]]:
    """Topological batches, preserving declaration order for deterministic output."""
    by_id = unique(nodes, "workflow nodes")
    for node in nodes:
        deps = node.get("depends_on")
        require(isinstance(deps, list) and all(isinstance(d, str) for d in deps),
                f"{node['id']}: depends_on must be a string list")
        require(len(deps) == len(set(deps)), f"{node['id']}: duplicate dependency")
        require(node["id"] not in deps, f"{node['id']}: self dependency")
        require(all(d in by_id for d in deps), f"{node['id']}: unknown dependency")
    completed: set[str] = set()
    result = []
    while len(completed) < len(nodes):
        ready = [n["id"] for n in nodes if n["id"] not in completed
                 and set(n["depends_on"]) <= completed]
        require(bool(ready), "Workflow contains a dependency cycle")
        result.append(ready)
        completed.update(ready)
    return result


def ancestors(nodes: list[dict], node_id: str) -> set[str]:
    by_id = {n["id"]: n for n in nodes}
    found: set[str] = set()
    pending = list(by_id[node_id]["depends_on"])
    while pending:
        dep = pending.pop()
        if dep not in found:
            found.add(dep)
            pending.extend(by_id[dep]["depends_on"])
    return found


def validate_agents(data: dict, root: Path) -> dict[str, dict]:
    require(data.get("root_agent_id") == "daksh-brain", "Daksh Brain must be the root")
    agents = unique(data.get("agents", []), "agents")
    require("daksh-brain" in agents, "Missing Daksh Brain controller")
    for ident, agent in agents.items():
        require(agent.get("parent") == (None if ident == "daksh-brain" else "daksh-brain"),
                f"{ident}: parent must be Daksh Brain (root has no parent)")
        for field in ("mission", "execution_status", "write_scope"):
            require(isinstance(agent.get(field), str) and bool(agent[field].strip()),
                    f"{ident}: missing {field}")
        for field in ("inputs", "owns", "must_preserve", "outputs", "done_checks", "escalate_when"):
            require(isinstance(agent.get(field), list) and bool(agent[field])
                    and all(isinstance(s, str) and s.strip() for s in agent[field]),
                    f"{ident}: {field} must contain explicit requirements")
        for path in [agent["contract"], *agent.get("skill_paths", [])]:
            require(safe_repo_path(root, path).is_file(), f"{ident}: missing source {path}")
    return agents


def validate_workflows(data: dict, agents: dict[str, dict]) -> dict[str, dict]:
    require(data.get("root_agent_id") == "daksh-brain", "Workflow root must be Daksh Brain")
    workflows = unique(data.get("workflows", []), "workflows")
    require(bool(workflows), "No workflow templates defined")
    for ident, flow in workflows.items():
        nodes = flow.get("nodes", [])
        require(bool(nodes), f"{ident}: no nodes")
        waves(nodes)
        require(bool(flow.get("required_inputs")), f"{ident}: no required inputs")
        require(bool(flow.get("acceptance_checks")), f"{ident}: no acceptance checks")
        for node in nodes:
            require(node.get("agent") in agents, f"{ident}/{node['id']}: unknown agent")
            require(node.get("effect") in ("draft", "read", "authorized_external"),
                    f"{ident}/{node['id']}: invalid effect classification")
            require(node.get("required") is True, f"{ident}/{node['id']}: required flag missing")
        terminals = [n for n in nodes if not any(n['id'] in m['depends_on'] for m in nodes)]
        require(len(terminals) == 1, f"{ident}: workflow needs one accountable terminal")
        terminal = terminals[0]
        require(terminal["agent"] == "daksh-brain", f"{ident}: Daksh Brain must deliver")
        require(len(ancestors(nodes, terminal["id"])) == len(nodes)-1,
                f"{ident}: delivery bypasses required work")
        reviews = [n for n in nodes if n["agent"] == "independent-qc"]
        if len(nodes) >= 5:
            require(bool(reviews), f"{ident}: substantial workflow needs explicit QC")
            require(any(n["id"] in ancestors(nodes, terminal["id"]) for n in reviews),
                    f"{ident}: final QC is not a delivery dependency")
            production = {n["id"] for n in nodes
                          if n["agent"] not in ("daksh-brain", "independent-qc")}
            require(any(production <= ancestors(nodes, review["id"]) for review in reviews),
                    f"{ident}: final QC must review every required production branch")
    return workflows


def validate_catalog(root: Path, agents: dict[str, dict]) -> dict:
    path = root / "catalog/skills.json"
    require(path.is_file(), "Missing catalog/skills.json")
    catalog = load(path)
    skills = catalog.get("skills", [])
    require(bool(skills), "Empty skill catalog")
    seen: set[str] = set()
    repo_paths = set()
    for skill in skills:
        require(skill["id"] not in seen, f"Duplicate catalog id {skill['id']}")
        seen.add(skill["id"])
        require(skill["owner_agent_id"] in agents, f"Unknown skill owner {skill['owner_agent_id']}")
        for owner in skill.get("secondary_owner_agent_ids", []):
            require(owner in agents, f"Unknown secondary owner {owner}")
        require(not str(skill["source_locator"]).startswith(("/Users/", "/home/")),
                "Catalog contains a machine-specific home path")
        require(skill["availability"].get("runtime_verified") is False,
                "Inventory cannot claim runtime capability verification")
        if skill.get("availability", {}).get("repository_present"):
            repo_paths.add(skill["source_locator"])
    actual = {p.relative_to(root).as_posix() for p in (root / "skills").glob("*/SKILL.md")}
    # Accept a portable repo: prefix without relying on a machine-specific path.
    normalized = {p.removeprefix("repo:").removeprefix("repository:").removeprefix("repository/") for p in repo_paths}
    require(actual <= normalized, f"Catalog omits bundled skills: {sorted(actual-normalized)}")
    return {"catalogued_skills": len(skills), "bundled_skills": len(actual)}


def validate(root: Path, *, catalog: bool = True) -> dict:
    agents = validate_agents(load(root / "architecture/agents.json"), root)
    workflows = validate_workflows(load(root / "architecture/workflows.json"), agents)
    policy = load(root / "architecture/policies.json")
    require(policy["control"]["canonical_writer"] == "daksh-brain", "Canonical writer mismatch")
    require(policy["control"]["root_agent_id"] == "daksh-brain", "Policy root mismatch")
    aliases = load(root / "architecture/legacy-role-map.json")["mapping"]
    require(all(v in agents for v in aliases.values()), "Unknown compatibility alias target")
    schemas = sorted((root / "architecture/contracts").glob("*.schema.json"))
    require(len(schemas) == 4, "Four handoff contracts must be present")
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        raise SpecError("Install jsonschema>=4.20,<5 for the full schema gate") from exc
    for path in schemas:
        Draft202012Validator.check_schema(load(path))
    for example in sorted((root / "architecture/examples").glob("*.example.json")):
        value = load(example)
        kind = example.name.split(".")[0]
        schema = load(root / "architecture/contracts" / f"{kind}.schema.json")
        errors = list(Draft202012Validator(
            schema, format_checker=Draft202012Validator.FORMAT_CHECKER).iter_errors(value))
        require(not errors, f"{example.name}: contract validation failed: "
                + "; ".join(error.message for error in errors))
        for key in ("owner", "from_agent", "to_agent", "producer"):
            if key in value:
                require(value[key] in agents, f"{example.name}: unknown {key}")
    result = {"agents": len(agents), "workflows": len(workflows), "contracts": len(schemas),
              "status": "specification_valid", "executed_workers": 0, "provider_calls": 0}
    if catalog:
        result.update(validate_catalog(root, agents))
    return result


def preview(root: Path, workflow_id: str, inputs: dict, max_parallel: int = 3) -> dict:
    require(type(max_parallel) is int and max_parallel >= 1, "max_parallel must be positive")
    agents = validate_agents(load(root / "architecture/agents.json"), root)
    workflows = validate_workflows(load(root / "architecture/workflows.json"), agents)
    require(workflow_id in workflows, f"Unknown workflow {workflow_id}")
    require(isinstance(inputs, dict), "inputs must be a JSON object")
    flow = deepcopy(workflows[workflow_id])
    text_fields = {"objective", "goal", "question", "synopsis", "audience", "dialect",
                   "purpose", "jurisdiction", "research_goal", "target_buyer"}
    def provided(key: str) -> bool:
        value = inputs.get(key)
        if key in text_fields:
            return isinstance(value, str) and bool(value.strip())
        if isinstance(value, str):
            return bool(value.strip())
        if type(value) in (int, float):
            return value > 0
        if isinstance(value, (list, dict)):
            return bool(value)
        return False
    missing = [key for key in flow["required_inputs"] if not provided(key)]
    # A preview never serializes private input values into its result.
    batches = [batch[i:i+max_parallel] for batch in waves(flow["nodes"])
               for i in range(0, len(batch), max_parallel)]
    return {"workflow": workflow_id, "status": "missing_inputs" if missing else "plan_preview",
            "missing_inputs": missing, "max_parallel": max_parallel, "waves": batches,
            "nodes": flow["nodes"], "acceptance_checks": flow["acceptance_checks"],
            "workers_launched": 0, "provider_calls": 0,
            "note": "Design preview only. Does not dispatch, grant access, generate media, approve sources or save a run ledger. Multi-show/season placeholders require per-item DAG expansion before execution."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    plan = commands.add_parser("plan")
    plan.add_argument("workflow")
    plan.add_argument("--inputs", type=Path, required=True)
    plan.add_argument("--max-parallel", type=int, default=3)
    args = parser.parse_args(argv)
    try:
        result = validate(args.root) if args.command == "validate" else preview(
            args.root, args.workflow, load(args.inputs), args.max_parallel)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result.get("status") == "missing_inputs" else 0
    except (SpecError, ValueError, KeyError, TypeError) as exc:
        print(f"Daksh specification error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
