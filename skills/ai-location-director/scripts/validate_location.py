#!/usr/bin/env python3
"""Check a location manifest's structure; never certify its visual continuity."""
import argparse
import json
import math
from pathlib import Path


STAGES = ["brief_ready", "context_ready", "research_ready", "plan_review", "plan_locked", "master_draft", "master_review", "master_locked", "layout_questions", "layout_ready", "blockout_ready", "camera_references", "final_views", "qc", "delivered"]
AFTER_PLAN = STAGES[5:]
AFTER_MASTER = STAGES[7:]
LEVELS = {"reference-based", "shared-scene-render", "ai-enhanced-render", "viewer-tested-panorama"}
COLLECTIONS = ["objects", "props", "zones", "connections", "routes", "lights", "states", "cameras", "anchors", "tags", "outputs", "qc"]


def validate(data, base, check_files=False):
    errors, notes = [], []

    def require(ok, message):
        if not ok:
            errors.append(message)

    def vector(value, n=3):
        return isinstance(value, list) and len(value) == n and all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in value)

    def positive(value):
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0

    def path_check(path, label):
        if path is not None:
            require(isinstance(path, str) and bool(path.strip()), label + ": invalid path")
        if check_files and isinstance(path, str) and path.strip():
            p = Path(path)
            require((p if p.is_absolute() else base / p).is_file(), label + ": local file missing")

    if not isinstance(data, dict):
        return ["Manifest must be a JSON object"], notes
    require(data.get("schema_version") == 1, "schema_version must be 1")
    for key in ["location_id", "version", "geometry_version", "material_version", "state_version"]:
        require(isinstance(data.get(key), str) and bool(data[key].strip()), key + " is required")
    stage = data.get("stage")
    require(stage in STAGES + ["prop_draft", "prop_design_locked", "prop_views", "revision_requested", "capability_limited"], "Unknown stage")
    mode = data.get("mode", "master-first")
    require(mode in ["master-first", "researched-agent", "props-only"], "Unknown execution mode")
    require(data.get("verification_level") in LEVELS, "Unknown verification_level")
    coords = data.get("coordinates", {})
    require(isinstance(coords, dict), "coordinates must be an object")
    if isinstance(coords, dict):
        require(coords.get("units") == "metres", "Use metres; convert values before validation")
        require(vector(coords.get("origin")), "coordinates.origin must be a finite XYZ")
        require(bool(coords.get("axes")), "Document coordinate axes")
    master = data.get("master", {})
    require(isinstance(master, dict), "master must be an object")
    if isinstance(master, dict):
        require(master.get("status") in ["pending", "draft", "approved", "delegated"], "Invalid master status")
        locked = stage in AFTER_MASTER and mode != "props-only"
        if locked:
            require(master.get("status") in ["approved", "delegated"], "Dependent stage requires master acceptance or delegated authority")
            require(bool(master.get("approval_evidence")), "Master approval/authority evidence missing")
            require(bool(master.get("path")), "Locked master path missing")
            if "version" in master:
                require(bool(master.get("version")) and master.get("approved_version") == master.get("version"), "Master approval does not match current version")
        path_check(master.get("path"), "master")
        for key in ["requested_pixels", "native_pixels", "exported_pixels"]:
            p = master.get(key)
            require(p is None or (vector(p, 2) and all(positive(v) and int(v) == v for v in p)), "master." + key + " must be positive integer pixels")
    plan = data.get("plan", {})
    require(isinstance(plan, dict), "plan must be an object when present")
    if isinstance(plan, dict):
        path_check(plan.get("path"), "plan")
        if mode == "researched-agent":
            require(bool(data.get("run_id")), "Researched agent needs run_id")
            require(bool(plan.get("artifact_id")) and bool(plan.get("version")), "Agent plan ID/version missing")
            has_master = isinstance(master, dict) and master.get("status") in ["draft", "approved", "delegated"]
            if stage in AFTER_PLAN + ["plan_locked"] or has_master:
                require(plan.get("status") in ["approved", "delegated"], "Plan approval required before master production")
                require(bool(plan.get("approval_evidence")), "Plan approval/authority evidence missing")
                require(plan.get("approved_version") == plan.get("version"), "Plan approval does not match current version")
                require(bool(plan.get("path")), "Approved plan must reference a concrete artifact")
    registries = {}
    for key in COLLECTIONS:
        items = data.get(key, []) if key == "props" else data.get(key)
        require(isinstance(items, list), key + " must be a list")
        registry = {}
        for item in items if isinstance(items, list) else []:
            if not isinstance(item, dict):
                errors.append(key + ": each entry must be an object")
                continue
            item_id = item.get("id")
            require(isinstance(item_id, str) and bool(item_id.strip()), key + ": missing ID")
            if not isinstance(item_id, str) or not item_id.strip():
                continue
            require(item_id not in registry, key + ": duplicate ID " + item_id)
            registry[item_id] = item
        registries[key] = registry

    def reference(kind, item_id, label):
        require(isinstance(item_id, str) and item_id in registries[kind], label + ": unknown " + kind + " reference " + str(item_id))

    for prop_id, prop in registries["props"].items():
        for key in ["name", "version", "intrinsic_front"]:
            require(isinstance(prop.get(key), str) and bool(prop[key].strip()), prop_id + ": " + key + " missing")
        require(prop.get("background") == "neutral-grey", prop_id + ": neutral-grey studio background required")
        custom = bool(prop.get("custom_view_evidence"))
        expected_angles = prop.get("view_order", [])
        require(isinstance(expected_angles, list) and bool(expected_angles) and all(isinstance(a, str) and a for a in expected_angles), prop_id + ": invalid view order")
        if custom:
            require(len(set(expected_angles)) == len(expected_angles), prop_id + ": duplicate custom angle")
        else:
            require(expected_angles == ["front", "back", "left", "right"], prop_id + ": required four-view order missing")
        require(prop.get("design_status") in ["source", "observed", "proposed", "approved"], prop_id + ": design status missing")
        state = prop.get("sheet_status")
        require(state in ["identified", "planned", "draft", "approved"], prop_id + ": sheet status missing")
        path_check(prop.get("source_path"), prop_id)
        if prop.get("object_id") is not None:
            reference("objects", prop["object_id"], prop_id)
        views = prop.get("views")
        require(isinstance(views, list), prop_id + ": views must be a list")
        angles, bound_outputs = [], []
        for view in views if isinstance(views, list) else []:
            if not isinstance(view, dict):
                errors.append(prop_id + ": view must be an object")
                continue
            angles.append(view.get("angle"))
            output_id = view.get("output_id")
            bound_outputs.append(output_id)
            reference("outputs", output_id, prop_id)
            if isinstance(output_id, str) and output_id in registries["outputs"]:
                out = registries["outputs"][output_id]
                require(out.get("prop_id") == prop_id, prop_id + ": view bound to another prop")
                require(out.get("prop_version") == prop.get("version"), prop_id + ": view uses stale prop version")
                if state == "approved":
                    require(out.get("status") == "approved", prop_id + ": approved set has unfinished view")
        if state != "identified" or angles:
            require(len(angles) == len(expected_angles) and set(angles) == set(expected_angles), prop_id + ": requested view coverage mismatch")
            if prop.get("delivery_layout") == "combined-sheet":
                cell_ids = [v.get("cell_id") for v in views]
                require(all(isinstance(c, str) and c for c in cell_ids) and len(set(cell_ids)) == len(cell_ids), prop_id + ": combined sheet needs distinct cell IDs")
            else:
                require(len(bound_outputs) == len(set(x for x in bound_outputs if isinstance(x, str))), prop_id + ": separate views need distinct output IDs")
        if state == "approved":
            require(prop.get("design_status") == "approved" and bool(prop.get("source_path")), prop_id + ": approved set lacks locked source design")

    objects, zones = registries["objects"], registries["zones"]
    for obj_id, obj in objects.items():
        require(vector(obj.get("position_m")), obj_id + ": world position missing")
        require(vector(obj.get("dimensions_m")) and all(positive(v) for v in obj.get("dimensions_m", [])), obj_id + ": invalid dimensions")
        require(vector(obj.get("rotation_deg")), obj_id + ": rotation missing")
        require(bool(obj.get("pivot")), obj_id + ": document pivot")
        require(obj.get("design_status") in ["source", "observed", "proposed", "approved"], obj_id + ": design status missing")
        if obj.get("parent_id") is not None:
            reference("objects", obj["parent_id"], obj_id)
        seen, current = set(), obj_id
        while current in objects:
            if current in seen:
                errors.append(obj_id + ": object parent cycle")
                break
            seen.add(current)
            current = objects[current].get("parent_id")
    for zone_id, zone in zones.items():
        if zone.get("parent_id") is not None:
            reference("zones", zone["parent_id"], zone_id)
        members = zone.get("object_ids", [])
        require(isinstance(members, list), zone_id + ": object_ids must be a list")
        for obj_id in members if isinstance(members, list) else []:
            reference("objects", obj_id, zone_id)
        seen, current = set(), zone_id
        while current in zones:
            if current in seen:
                errors.append(zone_id + ": zone parent cycle")
                break
            seen.add(current)
            current = zones[current].get("parent_id")
    for conn_id, conn in registries["connections"].items():
        for key in ["from_zone", "to_zone"]:
            reference("zones", conn.get(key), conn_id)
        require(conn.get("from_zone") != conn.get("to_zone"), conn_id + ": connection must join distinct zones")
        reference("objects", conn.get("shared_object_id"), conn_id)
        require(conn.get("type") in ["opening", "corridor", "stairs", "open-boundary"], conn_id + ": unknown connection type")
        a, b = conn.get("from_point_m"), conn.get("to_point_m")
        require(vector(a) and vector(b), conn_id + ": invalid endpoints")
        if conn.get("type") == "opening" and vector(a) and vector(b):
            tolerance = conn.get("tolerance_m")
            require(positive(tolerance), conn_id + ": opening tolerance required")
            if positive(tolerance):
                require(math.dist(a, b) <= tolerance, conn_id + ": opening endpoints do not coincide")
    for route_id, route in registries["routes"].items():
        points = route.get("points_m")
        require(isinstance(points, list) and len(points) >= 2 and all(vector(p) for p in points), route_id + ": route needs at least two finite XYZ points")
        notes.append(route_id + ": clearance/contact requires a separate scene check")
    for camera_id, cam in registries["cameras"].items():
        reference("zones", cam.get("zone_id"), camera_id)
        p, t = cam.get("position_m"), cam.get("target_m")
        require(vector(p) and vector(t), camera_id + ": invalid camera pose")
        if vector(p) and vector(t):
            require(math.dist(p, t) > 1e-8, camera_id + ": target equals camera position")
        projection = cam.get("projection")
        require(projection in ["perspective", "orthographic", "equirectangular"], camera_id + ": projection missing")
        if projection == "perspective":
            require(positive(cam.get("lens_mm")) and positive(cam.get("sensor_width_mm")), camera_id + ": perspective needs lens and sensor width")
            require(cam.get("sensor_fit") in ["horizontal", "vertical", "auto"], camera_id + ": sensor fit missing")
        if projection == "orthographic":
            require(positive(cam.get("ortho_scale_m")), camera_id + ": ortho scale missing")
        up = cam.get("up")
        require(vector(up) and sum(v * v for v in up) > 0, camera_id + ": up vector required")
        if vector(p) and vector(t) and vector(up):
            d = [t[i] - p[i] for i in range(3)]
            cross = [d[1]*up[2]-d[2]*up[1], d[2]*up[0]-d[0]*up[2], d[0]*up[1]-d[1]*up[0]]
            require(sum(v*v for v in cross) > 1e-12, camera_id + ": up vector is collinear with viewing direction")
        require(vector(cam.get("aspect"), 2) and all(positive(v) for v in cam.get("aspect", [])), camera_id + ": aspect required")
        for key, kind in [("light_id", "lights"), ("state_id", "states")]:
            reference(kind, cam.get(key), camera_id)
        for obj_id in cam.get("visible_object_ids", []):
            reference("objects", obj_id, camera_id)
    for anchor_id, anchor in registries["anchors"].items():
        reference("zones", anchor.get("zone_id"), anchor_id)
        require(vector(anchor.get("position_m")), anchor_id + ": world position missing")
        require(isinstance(anchor.get("zero_heading_deg"), (int, float)) and not isinstance(anchor.get("zero_heading_deg"), bool) and math.isfinite(anchor["zero_heading_deg"]), anchor_id + ": heading missing")
        if anchor.get("panorama_output_id"):
            reference("outputs", anchor["panorama_output_id"], anchor_id)
    model = data.get("model", {})
    require(isinstance(model, dict), "model must be an object")
    if isinstance(model, dict):
        path_check(model.get("path"), "model")
        if data.get("verification_level") in ["shared-scene-render", "ai-enhanced-render"]:
            require(model.get("kind") == "renderable-3d-scene" and bool(model.get("path")), "Shared-scene verification requires an actual model source")
            require(model.get("master_match") == "PASS", "Shared-scene model master match remains unverified")
    tag_strings = set()
    for tag_id, tag in registries["tags"].items():
        literal = tag.get("tag")
        require(isinstance(literal, str) and literal.startswith("@") and not any(c.isspace() for c in literal), tag_id + ": invalid literal tag")
        if isinstance(literal, str):
            require(literal not in tag_strings, tag_id + ": duplicate literal tag")
            tag_strings.add(literal)
        kind = tag.get("entity_kind")
        require(kind in ["objects", "props", "zones", "cameras"], tag_id + ": entity_kind missing")
        if kind in ["objects", "props", "zones", "cameras"]:
            reference(kind, tag.get("entity_id"), tag_id)
        require(tag.get("status") in ["proposed", "verified"], tag_id + ": tag status missing")
        if tag.get("status") == "verified":
            require(bool(tag.get("approval_evidence")) and bool(tag.get("asset_path")), tag_id + ": verified tag needs evidence and asset")
        path_check(tag.get("asset_path"), tag_id)
    for output_id, out in registries["outputs"].items():
        require(out.get("status") in ["planned", "draft", "approved", "stale", "superseded"], output_id + ": output status missing")
        if out.get("prop_id") is not None:
            reference("props", out["prop_id"], output_id)
            if out.get("status") == "approved" and out["prop_id"] in registries["props"]:
                require(out.get("prop_version") == registries["props"][out["prop_id"]].get("version"), output_id + ": approved output has stale prop version")
        for key, kind in [("camera_id", "cameras"), ("anchor_id", "anchors")]:
            if out.get(key) is not None:
                reference(kind, out[key], output_id)
        for dep in out.get("depends_on_output_ids", []):
            reference("outputs", dep, output_id)
            if dep in registries["outputs"] and out.get("status") == "approved":
                require(registries["outputs"][dep].get("status") not in ["stale", "superseded"], output_id + ": approved output depends on stale source")
        path_check(out.get("path"), output_id)
        if out.get("status") == "approved":
            require(bool(out.get("path")), output_id + ": approved output needs a file")
            for key in ["geometry_version", "material_version", "state_version"]:
                require(out.get(key) == data.get(key), output_id + ": approved output uses stale " + key)
        pixels = out.get("pixels")
        if pixels is not None:
            require(vector(pixels, 2) and all(positive(v) and int(v) == v for v in pixels), output_id + ": invalid pixels")
        if out.get("projection") == "equirectangular" and pixels is not None and vector(pixels, 2):
            require(pixels[0] == 2 * pixels[1], output_id + ": full-sphere texture must have 2:1 pixels")
    for qc_id, qc in registries["qc"].items():
        if qc.get("output_id") is not None:
            reference("outputs", qc["output_id"], qc_id)
        require(qc.get("status") in ["PASS", "FAIL", "PENDING", "N/A"], qc_id + ": invalid QC status")
        if qc.get("status") in ["PASS", "FAIL", "N/A"]:
            require(bool(qc.get("evidence")), qc_id + ": executed QC or N/A needs evidence/reason")
    reviews = data.get("reviews", [])
    require(isinstance(reviews, list), "reviews must be a list")
    candidates = {}
    for kind in ["outputs", "cameras", "anchors", "props"]:
        for artifact_id, artifact in registries[kind].items():
            candidates[artifact_id] = artifact.get("version", data.get("version"))
    for artifact in [plan, master]:
        if isinstance(artifact, dict) and isinstance(artifact.get("artifact_id"), str):
            candidates[artifact["artifact_id"]] = artifact.get("version", data.get("version"))
    for review in reviews if isinstance(reviews, list) else []:
        if not isinstance(review, dict):
            errors.append("Review must be an object")
            continue
        if review.get("state", "current") == "stale":
            continue
        require(review.get("run_id") == data.get("run_id") and bool(data.get("run_id")), "Review run_id mismatch")
        require(review.get("location_id") == data.get("location_id"), "Review location_id mismatch")
        require(review.get("location_version") == data.get("version"), "Review location version mismatch")
        require(review.get("candidate_id") in candidates, "Review candidate mismatch")
        if review.get("candidate_id") in candidates:
            require(review.get("candidate_version") == candidates[review["candidate_id"]], "Review candidate version mismatch")
        require(review.get("role") in ["research", "spatial-design", "mapping", "qc"], "Review role missing")
        require(review.get("status") in ["PASS", "FAIL", "PENDING"], "Review status invalid")
        require(isinstance(review.get("findings"), list) and isinstance(review.get("evidence"), list), "Review findings/evidence must be lists")
        if review.get("status") == "PASS":
            require(bool(review.get("evidence")), "Passing review needs inspection/research evidence")
    required_outputs = data.get("required_output_ids", [])
    require(isinstance(required_outputs, list), "required_output_ids must be a list")
    for output_id in required_outputs if isinstance(required_outputs, list) else []:
        reference("outputs", output_id, "required_output_ids")
    if stage == "delivered":
        require(bool(registries["outputs"]), "delivered requires actual outputs")
        unresolved = data.get("unresolved", [])
        require(isinstance(unresolved, list), "unresolved must be a list")
        if isinstance(unresolved, list):
            require(not any(isinstance(u, dict) and u.get("severity") == "critical" for u in unresolved), "Critical unresolved issue in delivered pack")
        require(not any(q.get("status") in ["FAIL", "PENDING"] and q.get("required", True) for q in registries["qc"].values()), "Required QC unresolved in delivered pack")
        for output_id in required_outputs if isinstance(required_outputs, list) else []:
            if output_id in registries["outputs"]:
                require(registries["outputs"][output_id].get("status") == "approved", output_id + ": required output is unfinished")
        for output_id, out in registries["outputs"].items():
            if out.get("status") == "approved":
                checks = [q for q in registries["qc"].values() if q.get("output_id") == output_id]
                require(bool(checks), output_id + ": delivered output has no QC record")
        if data.get("verification_level") == "viewer-tested-panorama":
            require(any(q.get("category") == "viewer" and q.get("status") == "PASS" for q in registries["qc"].values()), "Viewer-tested claim requires recorded executed viewer QC")
    notes.append("Structural checks only; inspect geometry, final images and viewer separately.")
    return errors, notes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--check-files", action="store_true", help="Check populated local file paths exist; does not decode images")
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text())
        errors, notes = validate(data, args.manifest.parent, args.check_files)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        errors, notes = ["Invalid manifest: " + str(exc)], []
    print(json.dumps({"structure": "FAIL" if errors else "PASS", "errors": errors, "notes": notes}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
