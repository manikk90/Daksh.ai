#!/usr/bin/env python3
"""Read-only conversion of a declared COLMAP images.txt world-to-camera pose.

This is not a reconstruction, rig-pose resolver or project-coordinate import.
"""
import argparse
import json
import math
from pathlib import Path


def vector(value, length, name):
    if (not isinstance(value, list) or len(value) != length or
            any(type(v) not in (int, float) or not math.isfinite(v) for v in value)):
        raise ValueError(name + " requires finite numeric components")
    return value


def inspect_pose(record):
    if not isinstance(record, dict) or record.get("format") != "colmap-images-txt-world-to-camera":
        raise ValueError("Declare the COLMAP images.txt image-level world-to-camera convention")
    q = vector(record.get("qvec_wxyz"), 4, "qvec_wxyz")
    t = vector(record.get("tvec"), 3, "tvec")
    norm = math.hypot(*q)
    if not math.isfinite(norm) or abs(norm - 1) > 1e-5:
        raise ValueError("Expected unit Hamilton quaternion (w,x,y,z); no implicit convention repair")
    w, x, y, z = [v / norm for v in q]
    r = [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
         [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
         [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]
    centre = [-sum(r[j][i]*t[j] for j in range(3)) for i in range(3)]
    if any(not math.isfinite(v) for v in centre):
        raise ValueError("Camera centre overflowed")
    return {"rotation_world_to_camera": r, "camera_center_source_world": centre,
            "right_source_world": r[0], "up_source_world": [-v for v in r[1]],
            "forward_source_world": r[2], "source_quaternion_norm": norm,
            "roundoff_normalized": norm != 1,
            "alignment_status": "PENDING_PROJECT_ALIGNMENT",
            "limitations": "Image-level pose arithmetic only. Source units/orientation are not "
                           "assumed to be metres or project east/north/up. No rig/body pose resolution, "
                           "intrinsics conversion, landmark verification, asset writes or approval changes."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        report = inspect_pose(json.loads(args.record.read_text()))
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
