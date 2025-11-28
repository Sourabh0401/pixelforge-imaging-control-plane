from __future__ import annotations

from typing import Iterable, Mapping, Sequence

from .color_delta import color_delta_summary
from .frame_sampling import region_sample_points
from .golden_image_diff import golden_diff
from .pixel_tolerance import PixelMatrix, matrix_dimensions


def normalize_region(region: Mapping[str, object]) -> dict[str, int | str]:
    return {
        "name": str(region.get("name", "region")),
        "x": int(region.get("x", 0)),
        "y": int(region.get("y", 0)),
        "width": int(region.get("width", 0)),
        "height": int(region.get("height", 0)),
    }


def clip_region(region: Mapping[str, object], width: int, height: int) -> dict[str, int | str] | None:
    item = normalize_region(region)
    left = max(int(item["x"]), 0)
    top = max(int(item["y"]), 0)
    right = min(left + int(item["width"]), width)
    bottom = min(top + int(item["height"]), height)
    if right <= left or bottom <= top:
        return None
    return {"name": item["name"], "x": left, "y": top, "width": right - left, "height": bottom - top}


def extract_region(matrix: PixelMatrix, region: Mapping[str, object]) -> list[list[object]]:
    width, height, _ = matrix_dimensions(matrix)
    clipped = clip_region(region, width, height)
    if clipped is None:
        return []
    left = int(clipped["x"])
    top = int(clipped["y"])
    right = left + int(clipped["width"])
    bottom = top + int(clipped["height"])
    return [list(row[left:right]) for row in matrix[top:bottom]]


def missing_required_regions(
    matrix: PixelMatrix,
    required_regions: Sequence[Mapping[str, object]],
) -> list[str]:
    width, height, _ = matrix_dimensions(matrix)
    missing: list[str] = []
    for region in required_regions:
        clipped = clip_region(region, width, height)
        if clipped is None:
            missing.append(str(normalize_region(region)["name"]))
    return sorted(missing)


def region_diff_summary(
    actual: PixelMatrix,
    expected: PixelMatrix,
    required_regions: Sequence[Mapping[str, object]] = (),
    ignore_regions: Sequence[Mapping[str, object]] = (),
    tolerance: int = 0,
    max_mismatched_pixels: int = 0,
    mean_delta_limit: float | None = None,
) -> dict[str, object]:
    actual_dims = matrix_dimensions(actual)
    expected_dims = matrix_dimensions(expected)
    if actual_dims != expected_dims:
        return {
            "passed": False,
            "status": "block",
            "severity": "block",
            "issue_codes": ["dimension-mismatch"],
            "issues": [f"dimension mismatch {actual_dims} != {expected_dims}"],
            "regions": {},
            "ignored_regions": [],
            "required_regions": [],
        }

    missing = missing_required_regions(actual, required_regions) + missing_required_regions(expected, required_regions)
    issues = [f"required region missing: {name}" for name in sorted(dict.fromkeys(missing))]
    summaries: dict[str, dict[str, object]] = {}
    for region in required_regions:
        item = normalize_region(region)
        left = extract_region(actual, item)
        right = extract_region(expected, item)
        if not left or not right:
            continue
        diff = golden_diff(
            left,
            right,
            tolerance=tolerance,
            max_mismatched_pixels=max_mismatched_pixels,
            mean_delta_limit=mean_delta_limit,
        )
        color = color_delta_summary(left, right)
        summaries[str(item["name"])] = {
            "bounds": item,
            "difference_ratio": diff["difference_ratio"],
            "mismatched_pixels": diff["mismatched_pixels"],
            "max_channel_delta": diff["max_channel_delta"],
            "mean_pixel_delta": diff["mean_pixel_delta"],
            "color_status": color["status"],
            "passed": bool(diff["passed"] and color["passed"]),
        }
        if not summaries[str(item["name"])]["passed"]:
            issues.append(f"required region mismatch: {item['name']}")

    ignored = [normalize_region(region) for region in ignore_regions]
    sampled_ignored_points = {
        point
        for region in ignored
        for point in region_sample_points(region, stride=max(int(region["width"]) // 4, 1))
    }
    if sampled_ignored_points:
        issues.append(f"ignored regions sampled: {len(sampled_ignored_points)}")

    status = "block" if any(message.startswith("required region mismatch") or message.startswith("required region missing") for message in issues) else "ok"
    return {
        "passed": status != "block",
        "status": status,
        "severity": status,
        "issue_codes": ["region-diff"] if issues else [],
        "issues": issues,
        "regions": summaries,
        "ignored_regions": ignored,
        "required_regions": [normalize_region(region) for region in required_regions],
    }

