#!/usr/bin/env python3
"""Build a metadata-only skill inventory from explicit local roots.

This script never executes a skill, contacts a provider, or copies skill bodies.
Run from any directory; use --scan-host to include standard local installations.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re

try:
    import yaml
except ImportError:
    yaml = None

REPO = Path(__file__).resolve().parent.parent
CATALOG = REPO / "catalog"

PACKAGE_OWNERS = {
    "apollo": "sales", "common-room": "sales", "bio-research": "research-intelligence",
    "brand-voice": "socials", "customer-support": "support", "data": "data-analytics",
    "data-analytics": "data-analytics", "design": "design", "engineering": "engineering",
    "enterprise-search": "knowledge", "finance": "finance", "human-resources": "people",
    "legal": "legal", "marketing": "socials", "operations": "operations",
    "productivity": "operations", "sales": "sales", "slack-by-salesforce": "operations",
    "atlassian": "operations", "figma": "design", "firecrawl": "research-intelligence",
    "frontend-design": "design", "huggingface-skills": "engineering", "pinecone": "knowledge",
    "posthog": "data-analytics", "google-drive": "documents", "documents": "documents",
    "pdf": "documents", "spreadsheets": "documents", "pages": "knowledge",
    "sites": "engineering", "work-pets": "capability-operator", "chatgpt-meetings": "operations",
    "stripe": "finance", "vercel": "engineering", "plugin-management": "capability-operator",
    "cowork-plugin-management": "capability-operator", "plugin-dev": "engineering",
    "hookify": "engineering", "claude-code-setup": "engineering", "coderabbit": "independent-qc",
    "qodo": "independent-qc", "qodo-skills": "independent-qc", "superpowers": "engineering",
    "app-68de829bf7648191acd70a907364c67c": "music-director",
    "app-69312da8e4dc81919370cb86fd172b6c": "design",
}
EXACT_OWNERS = {
    "daksh": "daksh-brain", "daksh-orchestrator": "daksh-brain",
    "ai-native-director": "native-director", "ai-location-director": "location-director",
    "ai-music-director": "music-director", "ai-dubbing": "dubbing-director",
    "ai-socials": "socials", "fashion-campaign-director": "fashion-campaigner",
    "suno-instrumental-prompts": "suno-helper", "brain-evals": "brain-evals",
    "god-mode": "business-strategy", "maniik": "operations", "ai-writer": "writer",
    "writer": "writer", "write-like-me": "writer", "writing-style": "writer",
    "promo-scriptwriter": "writer", "regional-language-cowriter": "writer",
    "regional-script-converter": "writer", "seedance-2-pro-director": "native-director",
    "video-analyst": "independent-qc", "stage-asset-pipeline": "reference-mapper",
    "elevenlabs-voice-workflow": "dubbing-director", "motion-promo-partner": "native-director",
    "remotion-video-engine": "engineering", "competitor-intel": "research-intelligence",
    "mckinsey-research": "business-strategy", "okr-deck-builder": "documents",
    "content-calendar-planner": "socials", "ai-creative-director": "native-director",
    "dual-brain-architect": "daksh-brain", "consolidate-memory": "knowledge",
    "imagegen": "design", "canvas-design": "design", "algorithmic-art": "design",
    "brand-guidelines": "design", "theme-factory": "design", "slack-gif-creator": "design",
    "docx": "documents", "pptx": "documents", "xlsx": "documents", "docs": "documents",
    "doc-coauthoring": "documents", "web-artifacts-builder": "engineering",
    "google-workspace": "documents", "internal-comms": "operations", "schedule": "operations",
    "morning": "operations", "import-memory": "knowledge", "canvas": "design",
    "caveman": "writer", "openai-docs": "research-intelligence",
}
DOMAINS = {
    "daksh-brain": "orchestration", "research-intelligence": "research", "business-strategy": "strategy",
    "action-style": "action_style_learning", "writer": "writing", "native-director": "filmmaking",
    "reference-mapper": "references_and_assets", "location-director": "locations",
    "music-director": "music", "dubbing-director": "voice_and_dubbing", "suno-helper": "music_prompts",
    "fashion-campaigner": "fashion", "socials": "marketing_and_social", "engineering": "software",
    "design": "design", "data-analytics": "data", "documents": "documents",
    "operations": "operations", "knowledge": "knowledge", "sales": "sales", "support": "support",
    "finance": "finance", "legal": "legal", "people": "people", "independent-qc": "quality",
    "brain-evals": "agent_evaluation", "capability-operator": "capability_operations", "maniik-advisor": "work_advisory",
}


def clean(value: object) -> str:
    """Remove machine-specific home paths from descriptive metadata."""
    text = re.sub(r"/Users/[^/\s]+", "<home>", str(value))
    text = re.sub(r"/home/[^/\s]+", "<home>", text)
    return text.strip()


def frontmatter(path: Path) -> tuple[dict, str | None]:
    """Read frontmatter only; no skill-body content enters the inventory."""
    lines = []
    with path.open(encoding="utf-8-sig") as stream:
        if stream.readline().strip() != "---":
            return {}, "frontmatter_missing"
        for line in stream:
            if line.strip() == "---":
                break
            lines.append(line)
        else:
            return {}, "frontmatter_unterminated"
    raw = "".join(lines)
    if yaml:
        try:
            data = yaml.safe_load(raw)
            return (data if isinstance(data, dict) else {}), None
        except Exception as error:
            return {}, "frontmatter_parse_error:" + type(error).__name__
    # A dependency-free fallback supports the scalar fields used by the catalog.
    result, key, multiline = {}, None, False
    for line in lines:
        if line[:1].isspace() and key and multiline:
            result[key] += " " + line.strip()
        else:
            match = re.match(r"^([\w-]+):\s*(.*?)\s*$", line)
            if not match:
                continue
            key, value = match.groups()
            multiline = value.startswith((">", "|"))
            result[key] = "" if multiline else value.strip("\"'")
    return result, "scalar_parser_used"


def package_coordinates(locator: str) -> tuple[str, str | None, str | None]:
    parts = locator.split("/")
    if parts[0] == "plugin-cache" and len(parts) >= 5:
        return parts[1], parts[2], parts[3]
    return parts[0], None, None


def session_match(locator: str, name: str, manifest: dict) -> tuple[bool, bool, str | None]:
    pieces = locator.split("/")
    leaf = pieces[-2]
    aliases = {name, leaf, name.split(":")[-1]}
    if pieces[0] == "local-agent-skills":
        selected = set(manifest["local_agent_skills"].split())
        matches = aliases & selected
        return bool(matches), False, "local:" + sorted(matches)[0] if matches else None
    if pieces[0] == "system-skills":
        matches = aliases & set(manifest["system_skills"].split())
        return bool(matches), False, "system:" + sorted(matches)[0] if matches else None
    if pieces[0] == "plugin-cache" and len(pieces) >= 5:
        coordinate = "/".join(pieces[1:4])
        relative = pieces[4:]
        # The exposed catalog names these exact roots, not legacy variants such
        # as skills/v1 or alternate implementations such as skills-figquery.
        primary_skill = len(relative) == 3 and relative[0] == "skills"
        migrated_command = len(relative) == 4 and relative[:2] == [".codex-plugin", "migrated-command-skills"]
        if not (primary_skill or migrated_command):
            return False, False, None
        matches = aliases & set(manifest["plugin_packages"].get(coordinate, "").split())
        disabled = coordinate in manifest.get("policy_disabled_packages", [])
        return bool(matches), disabled, coordinate + ":" + sorted(matches)[0] if matches else None
    return False, False, None


def owner_for(name: str, package: str | None) -> str:
    if name in EXACT_OWNERS:
        return EXACT_OWNERS[name]
    if package in PACKAGE_OWNERS:
        return PACKAGE_OWNERS[package]
    if any(x in name for x in ("skill", "plugin", "setup-cowork", "explain-usage")):
        return "capability-operator"
    if any(x in name for x in ("review", "test", "eval", "autofix")):
        return "independent-qc"
    if any(x in name for x in ("research", "search", "docs")):
        return "research-intelligence"
    if any(x in name for x in ("memory", "knowledge")):
        return "knowledge"
    return "engineering"


def skill_paths(root: Path):
    """Follow aliases but avoid cycles; canonical files are deduplicated later."""
    if not root.exists():
        return
    for directory, subdirs, files in os.walk(root, followlinks=True):
        subdirs[:] = sorted(d for d in subdirs if d not in {".git", "node_modules", ".venv", "__pycache__"})
        current = Path(directory)
        ancestors = set()
        for parent in [current, *current.parents]:
            resolved = parent.resolve()
            if resolved in ancestors:
                subdirs[:] = []
                break
            ancestors.add(resolved)
        if "SKILL.md" in files:
            yield current / "SKILL.md"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan-host", action="store_true", help="Include standard local agent, system, and plugin skill directories")
    parser.add_argument("--snapshot-date", default=date.today().isoformat())
    args = parser.parse_args()
    manifest = json.loads((CATALOG / "session-skill-manifest.json").read_text())
    roots = [(REPO, "repository", "repository_skill")]
    if args.scan_host:
        roots += [(Path.home() / ".agents/skills", "local-agent-skills", "user_installed_skill"),
                  (Path.home() / ".codex/skills/.system", "system-skills", "system_skill"),
                  (Path.home() / ".codex/plugins/cache", "plugin-cache", "plugin_skill")]
    files, errors = {}, []
    missing_roots = []
    for root, locator_root, source_kind in roots:
        if not root.exists():
            missing_roots.append(locator_root)
            continue
        for path in skill_paths(root):
            locator = locator_root + "/" + path.relative_to(root).as_posix()
            canonical = path.resolve()
            if canonical in files:
                files[canonical]["source_aliases"].append(locator)
                continue
            try:
                metadata, warning = frontmatter(path)
            except (OSError, UnicodeError) as error:
                errors.append({"source_locator": locator, "error": type(error).__name__})
                continue
            provider, package, version = package_coordinates(locator)
            name = clean(metadata.get("name", path.parent.name))
            listed, disabled, manifest_key = session_match(locator, name, manifest)
            owner = owner_for(name, package)
            repository = source_kind == "repository_skill"
            dependency = repository and "external_dependencies/" in locator
            if dependency:
                source_kind = "repository_external_dependency"
            description = clean(metadata.get("description", ""))
            source_metadata = {
                key: metadata[key] for key in ("license", "disable-model-invocation", "user-invocable", "compatibility")
                if key in metadata and isinstance(metadata[key], (str, bool, int, float))
            }
            qualified_name = name if provider in {"repository", "local-agent-skills", "system-skills"} else f"{package}:{name}"
            files[canonical] = {
                "id": "skill-" + hashlib.sha256(locator.encode()).hexdigest()[:16],
                "name": name, "qualified_name": qualified_name, "source_kind": source_kind,
                "source_locator": locator, "source_aliases": [locator], "provider": provider,
                "package": package, "version": version, "description": description,
                "metadata_sha256": hashlib.sha256(json.dumps(metadata, sort_keys=True, default=str).encode()).hexdigest(),
                "domain": DOMAINS[owner], "owner_agent_id": owner,
                "secondary_owner_agent_ids": ["daksh-brain", "independent-qc"] if owner not in {"daksh-brain", "independent-qc"} else [],
                "ownership_basis": "curated_name_mapping" if name in EXACT_OWNERS else "package_default" if package in PACKAGE_OWNERS else "name_heuristic_requires_review",
                "metadata": {key: clean(value) if isinstance(value, str) else value for key, value in source_metadata.items()},
                "metadata_warning": warning,
                "availability": {
                    "on_disk_readable": True, "session_listed": listed, "policy_disabled": disabled,
                    "repository_present": repository, "runtime_verified": False, "credentials_verified": False,
                    "adapter_required": True,
                    "activation": "repository_source_requires_adapter" if repository else "session_listed_policy_disabled" if listed and disabled else "session_listed_requires_runtime_checks" if listed else "disk_inventory_only",
                },
                "session_manifest_key": manifest_key,
                "redistribution": "metadata_only; install from licensed upstream source" if not repository else "existing_repository_source; upstream terms still apply",
                "upstream_license_review_required": not repository or dependency,
                "reconstruction_status": "reconstructed_in_repository" if repository and name in {"ai-writer", "writer"} else "existing_source_metadata",
            }
    records = sorted(files.values(), key=lambda s: (s["source_kind"], s["qualified_name"], s["source_locator"]))
    expected = {"local:" + n for n in manifest["local_agent_skills"].split()} | {"system:" + n for n in manifest["system_skills"].split()}
    expected |= {coordinate + ":" + n for coordinate, names in manifest["plugin_packages"].items() for n in names.split()}
    matched = {s["session_manifest_key"] for s in records if s["session_manifest_key"]}
    counts = {
        "canonical_readable_skills": len(records), "source_file_aliases": sum(len(s["source_aliases"]) for s in records),
        "session_listed": sum(s["availability"]["session_listed"] for s in records),
        "session_listed_policy_disabled": sum(s["availability"]["session_listed"] and s["availability"]["policy_disabled"] for s in records),
        "repository_skill_sources": sum(s["source_kind"] == "repository_skill" for s in records),
        "repository_external_dependencies": sum(s["source_kind"] == "repository_external_dependency" for s in records),
        "disk_inventory_only": sum(s["availability"]["activation"] == "disk_inventory_only" for s in records),
        "by_source_kind": dict(sorted(Counter(s["source_kind"] for s in records).items())),
        "by_owner_agent_id": dict(sorted(Counter(s["owner_agent_id"] for s in records).items())),
        "by_provider": dict(sorted(Counter(s["provider"] for s in records).items())),
    }
    catalog = {
        "schema_version": "1.0.0", "snapshot_date": args.snapshot_date,
        "scope": {
            "roots_scanned": [name for _, name, _ in roots], "missing_roots": missing_roots,
            "metadata_only": True, "bodies_copied": False, "credentials_included": False,
            "version_semantics": "Each canonical source file is a record; separate installed versions are separate records.",
            "availability_semantics": "A recorded skill is not an authorized, installed-in-repository, connected, or tested runtime capability.",
        }, "counts": counts, "skills": records,
        "scan_errors": errors, "session_manifest_unmatched": sorted(expected - matched),
    }
    (CATALOG / "skills.json").write_text(json.dumps(catalog, indent=2, ensure_ascii=False, default=str) + "\n")
    write_reports(catalog)
    if (CATALOG / "tools.json").exists():
        write_tool_report(json.loads((CATALOG / "tools.json").read_text()))
    print(json.dumps({"counts": counts, "scan_errors": errors, "session_manifest_unmatched": sorted(expected - matched)}, indent=2))


def md(value: object) -> str:
    return (str(value).replace("|", "\\|").replace("\n", " ")
            .replace("[", "\\[").replace("]", "\\]").replace("<", "&lt;").replace(">", "&gt;"))


def write_reports(catalog: dict):
    counts = catalog["counts"]
    lines = ["# Skill inventory snapshot", "", f"Snapshot: {catalog['snapshot_date']}. Generated from readable metadata; skill bodies and secrets are excluded.", "",
             "Presence in this inventory is not permission to invoke a skill. Session exposure is a separate fact from credentials, adapter readiness, service connection, and a successful live test.", "",
             "## Completeness", "", "| Measure | Count |", "| --- | ---: |"]
    for key in ("canonical_readable_skills", "source_file_aliases", "session_listed", "session_listed_policy_disabled", "repository_skill_sources", "repository_external_dependencies", "disk_inventory_only"):
        lines.append(f"| {key} | {counts[key]} |")
    lines += [f"| unreadable/parse scan errors | {len(catalog['scan_errors'])} |", f"| unmatched explicit session entries | {len(catalog['session_manifest_unmatched'])} |", "",
              "Canonical symlink aliases are combined. Different installed versions remain separate because their behavior and licensing may differ. The session manifest records the current exposed versions, not every cached copy.", "",
              "## Ownership", "", "Ownership is a routing recommendation. `curated_name_mapping` is explicit; package defaults and heuristics need task-specific review by Daksh Brain. Every record retains this basis.", "", "| Owner agent | Skill source records |", "| --- | ---: |"]
    lines += [f"| `{owner}` | {count} |" for owner, count in counts["by_owner_agent_id"].items()]
    lines += ["", "## Every discovered skill source", "", "| Skill | Owner | Availability | Source |", "| --- | --- | --- | --- |"]
    for skill in catalog["skills"]:
        lines.append(f"| {md(skill['qualified_name'])} | `{skill['owner_agent_id']}` | {skill['availability']['activation']} | `{skill['source_locator']}` |")
    if catalog["session_manifest_unmatched"]:
        lines += ["", "## Explicit session entries absent from scan", ""] + [f"- `{x}`" for x in catalog["session_manifest_unmatched"]]
    lines += ["", "## Provenance and redistribution", "",
              "`skills.json` contains frontmatter metadata, portable source coordinates, selected flags, a metadata hash, and availability observations. It does not vendor third-party skill instructions. Install or enable dependencies from their licensed upstream packages and inspect the relevant license before redistributing them.", "",
              "`repository/...` identifies material already present in this repository. `plugin-cache/<collection>/<package>/<version>/...`, `local-agent-skills/...`, and `system-skills/...` identify source classes without tying the catalog to a user's home directory. These locators are identifiers, not URLs or proof that another machine can resolve them.", "",
              "A missing license declaration is not an open-source license. No automatic installation, authentication, billing, permission change, or provider call is performed by the inventory builder.", ""]
    (CATALOG / "SKILLS.md").write_text("\n".join(lines))


def write_tool_report(catalog: dict):
    lines = ["# Tool capability snapshot", "", f"Snapshot: {catalog['snapshot_date']}. {catalog['counts']['registry_tools']} registry tools and {catalog['counts']['native_declarations']} native declarations.", "",
             "This is a name-and-summary inventory. No connector credentials, tool argument schemas, private messages, runtime instructions, or remote data are included. Listed tools still require a supported host adapter, an available connection, and task-specific authorization.", "",
             "## Registry tools", "", "| Tool | Provider | Owner | Capability summary |", "| --- | --- | --- | --- |"]
    for tool in catalog["tools"]:
        lines.append(f"| `{md(tool['name'])}` | {md(tool['provider'])} | `{tool['owner_agent_id']}` | {md(tool['summary'])} |")
    lines += ["", "## Native runtime declarations", "", "| Tool | Provider | Condition | Capability summary |", "| --- | --- | --- | --- |"]
    for tool in catalog["native_declarations"]:
        lines.append(f"| `{tool['name']}` | {tool['provider']} | {tool['availability']['conditional']} | {md(tool['summary'])} |")
    lines += ["", "Tool names in this snapshot are host-specific capability identifiers. They are not importable Python/JavaScript packages, universal MCP endpoints, or proof that the repository implements them.", ""]
    (CATALOG / "TOOLS.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
