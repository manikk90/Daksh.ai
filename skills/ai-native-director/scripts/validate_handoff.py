#!/usr/bin/env python3
"""Validate versioned Mapping/QC envelopes; never certify media quality."""
import argparse
import json
import sys
from pathlib import Path

STATUSES = {"PASS", "FAIL", "PENDING", "NOT_APPLICABLE"}
DOMAINS = {"planning", "reference_binding", "performance_action",
           "composition_camera", "visual", "temporal", "audio_sync", "edit", "delivery"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def evidence(value):
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate(data, run_id, scene_version, artifact_id, required_domains=()):
    require(isinstance(data, dict), "Handoff must be an object")
    for key, expected in [("run_id", run_id), ("scene_version", scene_version),
                          ("artifact_id", artifact_id)]:
        require(data.get(key) == expected, f"Stale or incorrect {key}")
    require(nonempty(data.get("reviewer")),
            "Reviewer identity required")
    require(data.get("execution") in {"independent", "self_review"},
            "Execution must distinguish independent review from self-review")
    stage = data.get("stage")
    if stage == "mapping":
        require(not required_domains, "Required QC domains apply only to QC handoffs")
        mapping = data.get("mapping")
        require(isinstance(mapping, dict), "Mapping object required")
        require(mapping.get("status") in STATUSES, "Invalid mapping status")
        for key in ["entities", "shots", "conflicts", "pending"]:
            require(isinstance(mapping.get(key), list), f"Mapping {key} list required")
        register = {}
        for entity in mapping["entities"]:
            require(isinstance(entity, dict), "Entity must be an object")
            eid = entity.get("entity_id")
            require(nonempty(eid) and eid not in register,
                    "Unique entity_id required")
            require(entity.get("approval") in {"APPROVED", "PROPOSED"}, "Invalid approval")
            tags = entity.get("tags")
            require(isinstance(tags, list) and all(isinstance(t, str) and len(t) > 1 and t.startswith("@")
                                                 and not any(c.isspace() for c in t) for t in tags),
                    f"Invalid exact tag list for {eid}")
            require(len(tags) == len(set(tags)), f"Duplicate tags for {eid}")
            if entity["approval"] == "APPROVED":
                require(bool(tags) and nonempty(entity.get("approval_evidence")),
                        f"Approved tags need source evidence for {eid}")
            require(entity.get("inspection") in {"VERIFIED", "PENDING"},
                    f"Invalid inspection status for {eid}")
            if entity["inspection"] == "VERIFIED":
                require(nonempty(entity.get("asset_id")) and evidence(entity.get("inspection_evidence")),
                        f"Verified inspection needs asset and evidence for {eid}")
            register[eid] = entity
        shot_ids = set()
        for shot in mapping["shots"]:
            require(isinstance(shot, dict), "Shot must be an object")
            sid = shot.get("shot_id")
            require(nonempty(sid) and sid not in shot_ids, "Unique shot_id required")
            shot_ids.add(sid)
            require(shot.get("status") in STATUSES, f"Invalid shot status for {sid}")
            eids = shot.get("entity_ids")
            require(isinstance(eids, list) and all(e in register for e in eids),
                    f"Unregistered shot entity for {sid}")
            require(len(eids) == len(set(eids)), f"Duplicate shot entities for {sid}")
            require(all(register[e]["approval"] == "APPROVED" for e in eids),
                    f"Proposed entity bound without approval in {sid}")
            known_tags = {t for eid in eids for t in register[eid]["tags"]}
            require(isinstance(shot.get("tags"), list) and set(shot["tags"]) == known_tags,
                    f"Shot tags disagree with entity register in {sid}")
            require(len(shot["tags"]) == len(set(shot["tags"])), f"Duplicate shot tags for {sid}")
            bindings = shot.get("input_bindings")
            require(isinstance(bindings, list), f"Input bindings required for {sid}")
            for binding in bindings:
                require(isinstance(binding, dict), "Input binding must be an object")
                eid = binding.get("entity_id")
                require(eid in eids and nonempty(binding.get("asset_id"))
                        and binding["asset_id"] == register[eid].get("asset_id"),
                        f"Wrong asset binding in {sid}")
                require(binding.get("bound") is True and evidence(binding.get("binding_evidence")),
                        f"Actual input binding needs attachment evidence in {sid}; use proposed_bindings otherwise")
            proposed = shot.get("proposed_bindings", [])
            require(isinstance(proposed, list), f"Proposed bindings must be a list in {sid}")
            for binding in proposed:
                require(isinstance(binding, dict), "Proposed binding must be an object")
                eid = binding.get("entity_id")
                require(eid in eids and nonempty(binding.get("asset_id"))
                        and binding["asset_id"] == register[eid].get("asset_id"),
                        f"Wrong proposed source in {sid}")
                require(binding.get("bound") is not True, f"Attached source belongs in input_bindings in {sid}")
            if shot["status"] == "PASS":
                require(bool(eids) and all(register[e]["inspection"] == "VERIFIED" for e in eids)
                        and {b["entity_id"] for b in bindings} == set(eids),
                        f"PASS requires inspected bound sources in {sid}")
        if mapping["status"] == "PASS":
            require(bool(mapping["entities"]) and bool(mapping["shots"])
                    and not mapping["conflicts"] and not mapping["pending"]
                    and all(s["status"] == "PASS" for s in mapping["shots"]),
                    "Overall PASS conflicts with unresolved mapping")
        if mapping["status"] == "FAIL":
            require(bool(mapping["conflicts"]) or any(s["status"] == "FAIL" for s in mapping["shots"]),
                    "Overall FAIL needs a conflict or failed shot")
    elif stage == "qc":
        reviews = data.get("reviews")
        require(isinstance(reviews, list) and bool(reviews), "Scoped QC reviews required")
        seen = set()
        by_domain = {}
        for review in reviews:
            require(isinstance(review, dict), "Review must be an object")
            domain = review.get("domain")
            require(domain in DOMAINS and domain not in seen, "Unique valid QC domain required")
            seen.add(domain)
            status = review.get("status")
            require(status in STATUSES, f"Invalid QC status for {domain}")
            require(nonempty(review.get("inspection_extent")), "Inspection scope required")
            if status in {"PASS", "FAIL"}:
                require(evidence(review.get("evidence")), f"{status} needs evidence for {domain}")
            by_domain[domain] = status
        require(set(required_domains).issubset(seen), "Required QC domain omitted")
        statuses = set(by_domain.values())
        overall = ("FAIL" if "FAIL" in statuses else "PENDING" if "PENDING" in statuses
                   else "PASS" if "PASS" in statuses else "NOT_APPLICABLE")
        if "overall_status" in data:
            require(data["overall_status"] == overall, "Overall QC status contradicts domain results")
        require(isinstance(data.get("findings"), list), "Findings list required")
        for finding in data["findings"]:
            require(isinstance(finding, dict), "Finding must be an object")
            require(finding.get("domain") in seen, "Finding lacks matching review domain")
            require(finding.get("severity") in {"Blocker", "Major", "Minor"}, "Invalid severity")
            require(all(nonempty(finding.get(k)) for k in ["shot_id", "evidence", "correction"]),
                    "Finding needs source, correction and recheck status")
            require(finding.get("recheck") in {"PASS", "FAIL", "PENDING"},
                    "Invalid finding recheck status")
            if finding["severity"] == "Blocker":
                require(by_domain[finding["domain"]] == "FAIL", "Blocker contradicts review status")
    else:
        raise ValueError("Stage must be mapping or qc")
    return {"contract": "VALID", "stage": stage, "artifact_id": artifact_id,
            "note": "Envelope consistency only; does not prove asset inspection or media quality."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handoff", type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--scene-version", required=True)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--required-domain", action="append", choices=sorted(DOMAINS), default=[],
                        help="Require this QC domain; repeat for each task gate")
    args = parser.parse_args()
    try:
        result = validate(json.loads(args.handoff.read_text()), args.run_id,
                          args.scene_version, args.artifact_id, args.required_domain)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"contract": "INVALID", "error": str(error)}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
