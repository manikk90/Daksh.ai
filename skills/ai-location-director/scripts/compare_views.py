#!/usr/bin/env python3
"""Compare already aligned views for human inspection; never certify visual quality.

Landmarks JSON format: {"reference": {"gate": [0.2, 0.4]},
"candidate": {"gate": [0.22, 0.4]}}. Coordinates are normalized to [0, 1].
Both sides must contain the same nonempty set of landmark IDs.
"""

import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image


def landmark_errors(data, width, height):
    if not isinstance(data, dict) or set(data) != {"reference", "candidate"}:
        raise ValueError("Landmarks require reference and candidate objects")
    ref, candidate = data["reference"], data["candidate"]
    if not isinstance(ref, dict) or not isinstance(candidate, dict):
        raise ValueError("Landmark sets must be objects")
    if not ref or set(ref) != set(candidate):
        raise ValueError("Landmark IDs must be nonempty and match exactly")
    for points in (ref, candidate):
        for name, point in points.items():
            if (not isinstance(point, list) or len(point) != 2 or
                    any(isinstance(v, bool) or not isinstance(v, (int, float)) or
                        not math.isfinite(v) or not 0 <= v <= 1 for v in point)):
                raise ValueError(f"Invalid normalized landmark: {name}")
    errors = {}
    for name in sorted(ref):
        dx = (candidate[name][0] - ref[name][0]) * (width - 1)
        dy = (candidate[name][1] - ref[name][1]) * (height - 1)
        errors[name] = {"dx_pixels": dx, "dy_pixels": dy,
                        "distance_pixels": math.hypot(dx, dy)}
    return errors


def compare_views(reference, candidate, output_dir, landmarks=None):
    with Image.open(reference) as source, Image.open(candidate) as target:
        if source.size != target.size:
            raise ValueError(f"Dimensions differ: {source.size} vs {target.size}; align externally")
        if source.size[0] < 2 or source.size[1] < 2:
            raise ValueError("Images must be at least 2 by 2 pixels")
        # Composite transparency consistently; diagnostic concerns visible pixels.
        def visible_rgb(im):
            rgba = im.convert("RGBA")
            return Image.alpha_composite(Image.new("RGBA", im.size, "white"), rgba).convert("RGB")
        ref, cand = visible_rgb(source), visible_rgb(target)
    width, height = ref.size
    errors = landmark_errors(landmarks, width, height) if landmarks is not None else None
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths = {"overlay": destination / "overlay.png", "absolute_difference": destination / "absolute_difference.png",
             "report": destination / "comparison.json"}
    inputs = {Path(reference).resolve(), Path(candidate).resolve()}
    if any(path.resolve() in inputs for path in paths.values()):
        raise ValueError("Output paths must not overwrite an input image")
    delta = np.abs(np.asarray(ref, dtype=np.int16) - np.asarray(cand, dtype=np.int16)).astype(np.uint8)
    Image.blend(ref, cand, 0.5).save(paths["overlay"])
    Image.fromarray(delta).save(paths["absolute_difference"])
    report = {"reference": str(reference), "candidate": str(candidate),
              "dimensions": {"width": width, "height": height},
              "mean_absolute_pixel_difference": float(delta.mean()),
              "pixel_difference_scale": "0–255 per RGB channel; white-composited transparency",
              "interpretation": "Diagnostic only, not a quality or similarity score. Requires human visual inspection; no automatic visual PASS.",
              "alignment": "Caller-provided alignment; equal dimensions do not establish camera alignment.",
              "outputs": {key: str(path) for key, path in paths.items()}}
    if errors is not None:
        report["landmark_errors"] = errors
    paths["report"].write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--landmarks", type=Path)
    args = parser.parse_args()
    try:
        points = json.loads(args.landmarks.read_text()) if args.landmarks else None
        report = compare_views(args.reference, args.candidate, args.output_dir, points)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
