"""Validate synthesis record provenance/status declarations; no network or model calls."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


def _validate_source(source: dict, identity: str) -> None:
    """Check source/receipt metadata without authenticating its real-world content."""
    if not isinstance(source.get("locator"), str) or not source["locator"].strip():
        raise ValueError(f"source locator required: {identity}")
    try:
        date.fromisoformat(source.get("checked_on", ""))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"valid source checked_on required: {identity}") from exc
    if source.get("kind") == "official_documentation":
        if "published_on" not in source:
            raise ValueError(f"publication date or explicit null required: {identity}")
        if source["published_on"] is not None:
            date.fromisoformat(source["published_on"])


def validate_synthesis(brain: dict) -> dict:
    """Reject incomplete evidence links and unsupported declared adoption/test states."""
    synthesis = brain.get("synthesis")
    if not isinstance(synthesis, dict) or synthesis.get("schema_version") != 1:
        raise ValueError("synthesis schema_version1 required")
    sources = {row["id"]: row for row in brain.get("sources", [])}
    records = synthesis.get("records")
    if not isinstance(records, list):
        raise ValueError("synthesis.records must be a list")
    ids: set[str] = set()
    for row in records:
        if not isinstance(row, dict):
            raise ValueError("record must be an object")
        identity = row.get("id")
        if not isinstance(identity, str) or not identity.strip() or identity in ids:
            raise ValueError("unique nonempty synthesis id required")
        ids.add(identity)
        date.fromisoformat(row.get("checked_on", ""))
        refs = row.get("source_ids")
        if not isinstance(refs, list) or not refs or any(ref not in sources for ref in refs):
            raise ValueError(f"unknown or missing source: {identity}")
        for ref in refs:
            _validate_source(sources[ref], identity)
        for field in ("verified_finding", "application", "recheck_trigger"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"missing {field}: {identity}")
        for field in ("agents", "target_files"):
            if not isinstance(row.get(field), list) or not row[field] or not all(isinstance(x, str) and x.strip() for x in row[field]):
                raise ValueError(f"missing {field}: {identity}")
        if row.get("evidence_level") not in {"documented", "tested_text", "tested_media", "hypothesis", "conflict"}:
            raise ValueError(f"invalid evidence_level: {identity}")
        if row.get("decision") not in {"adopt_rule", "prepare_test", "no_change", "defer", "reject"}:
            raise ValueError(f"invalid decision: {identity}")
        status = row.get("application_status")
        if status not in {"prepared", "saved_record_only", "installed_skill_rule", "pending"}:
            raise ValueError(f"invalid application_status: {identity}")
        if status == "installed_skill_rule" and row.get("installation_evidence_id") not in sources:
            raise ValueError(f"installation evidence required: {identity}")
        if status == "installed_skill_rule" and sources[row["installation_evidence_id"]].get("kind") not in {"skill_persistence_receipt", "tool_observation"}:
            raise ValueError(f"actual installation receipt type required: {identity}")
        if status == "installed_skill_rule":
            _validate_source(sources[row["installation_evidence_id"]], identity)
        if row["evidence_level"] == "conflict" and row["decision"] == "adopt_rule":
            raise ValueError(f"unresolved capability conflict cannot be adopted: {identity}")
        test = row.get("test")
        if not isinstance(test, dict) or test.get("status") not in {"proposed", "executed", "not_applicable"}:
            raise ValueError(f"test status required: {identity}")
        if test.get("kind") not in {"contract", "text", "media", "audio", "customer", "not_applicable"}:
            raise ValueError(f"test kind required: {identity}")
        if test["status"] != "not_applicable":
            for field in ("plan", "failure_signal"):
                if not isinstance(test.get(field), str) or not test[field].strip():
                    raise ValueError(f"observable test {field} required: {identity}")
        if test["status"] == "executed" and test.get("evidence_id") not in sources:
            raise ValueError(f"executed test evidence required: {identity}")
        if test["status"] == "executed":
            _validate_source(sources[test["evidence_id"]], identity)
            evidence_kind = sources[test["evidence_id"]].get("kind")
            allowed = {"local_test_result", "independent_text_review", "human_review", "media_test_result", "audio_test_result", "customer_test_result"}
            if evidence_kind not in allowed:
                raise ValueError(f"test result source type required: {identity}")
            if test["kind"] in {"media", "audio"} and evidence_kind not in {"media_test_result", "audio_test_result"}:
                raise ValueError(f"matching media/audio result required: {identity}")
        if test["status"] == "proposed" and test.get("evidence_id") is not None:
            raise ValueError(f"proposed test cannot claim execution evidence: {identity}")
        if row["evidence_level"] in {"tested_text", "tested_media"} and test["status"] != "executed":
            raise ValueError(f"tested evidence requires an executed test: {identity}")
        if row["evidence_level"] == "tested_media" and test["kind"] not in {"media", "audio"}:
            raise ValueError(f"media evidence requires a media/audio test: {identity}")
    return {"status": "valid_declarations_only", "records": len(records), "source_truth_verified_by_validator": False}


def main() -> None:
    """Validate one existing brain's synthesis section."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brain", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate_synthesis(json.loads(args.brain.read_text(encoding="utf-8")))))


if __name__ == "__main__":
    main()
