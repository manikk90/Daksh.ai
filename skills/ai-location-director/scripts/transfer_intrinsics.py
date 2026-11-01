#!/usr/bin/env python3
"""Transfer known pinhole intrinsics through an explicit pixel scale/translation.

Read-only JSON diagnostic; does not calibrate a photo or change any scene/asset.
The caller must supply the actual preprocessing convention, including offsets.
"""
import argparse
import json
import math
from pathlib import Path


def matrix(value, name):
    if (not isinstance(value, list) or len(value) != 3 or
            any(not isinstance(row, list) or len(row) != 3 for row in value)):
        raise ValueError(name + " must be a 3x3 matrix")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or
           not math.isfinite(v) for row in value for v in row):
        raise ValueError(name + " must contain finite numbers")
    if (value[2] != [0, 0, 1] or value[0][1] != 0 or value[1][0] != 0 or
            value[0][0] <= 0 or value[1][1] <= 0):
        raise ValueError(name + " requires positive diagonal scale, no skew/rotation, and [0,0,1] last row")
    return value


def transfer(data):
    if not isinstance(data, dict) or data.get("camera_model") != "pinhole":
        raise ValueError("Only explicitly declared pinhole input is supported")
    for name in ("source_pixels", "output_pixels"):
        pair = data.get(name)
        if (not isinstance(pair, list) or len(pair) != 2 or
                any(type(v) is not int or v <= 0 for v in pair)):
            raise ValueError(name + " requires positive integer width/height")
    if not isinstance(data.get("pixel_convention"), str) or not data["pixel_convention"].strip():
        raise ValueError("Document the actual pixel-origin/resampling convention")
    k = matrix(data.get("K"), "K")
    a = matrix(data.get("pixel_transform"), "pixel_transform")
    result = [[sum(a[i][n] * k[n][j] for n in range(3)) for j in range(3)] for i in range(3)]
    if any(not math.isfinite(v) for row in result for v in row):
        raise ValueError("Transferred intrinsics overflowed")
    return {"camera_model": "pinhole", "source_pixels": data["source_pixels"],
            "output_pixels": data["output_pixels"], "K": result,
            "pixel_transform": a, "pixel_convention": data["pixel_convention"],
            "operation": "K_output = pixel_transform @ K_source",
            "limitations": "Caller-supplied transform, not estimated calibration or alignment. "
                            "No image resampling, undistortion, pose change, panorama conversion, "
                            "automatic visual PASS or asset/approval modification."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        result = transfer(json.loads(args.record.read_text()))
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
