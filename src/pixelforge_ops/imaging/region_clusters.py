from __future__ import annotations

"""
Cluster region-level mismatches into operator-friendly components.

Region diff already tells us whether required rectangles matched. That is good
for gating, but operators also want to know how the mismatches group: one
isolated pixel, a small halo, a seam-like vertical strip, or a large rectangle
that probably points at a transform or crop bug.

This module turns raw mismatch coordinates into connected components and then
derives a few shapes from them. The output is deterministic and intentionally
lightweight so it can be used in quality reports, replay investigations, and
release notes without depending on heavy image libraries.
"""

from collections import deque
from typing import Iterable, Mapping, Sequence

from .pixel_tolerance import PixelMatrix, _coerce_channels, matrix_dimensions


def _coordinate_set(points: Iterable[tuple[int, int]]) -> set[tuple[int, int]]:
    return {(int(x), int(y)) for x, y in points}


def mismatch_points(
    actual: PixelMatrix,
    expected: PixelMatrix,
    tolerance: int = 0,
) -> list[tuple[int, int]]:
    actual_width, actual_height, _ = matrix_dimensions(actual)
    expected_width, expected_height, _ = matrix_dimensions(expected)
    if (actual_width, actual_height) != (expected_width, expected_height):
        raise ValueError("region cluster matrices must share dimensions")
    points = []
    for y, (actual_row, expected_row) in enumerate(zip(actual, expected, strict=True)):
        for x, (actual_pixel, expected_pixel) in enumerate(zip(actual_row, expected_row, strict=True)):
            left = _coerce_channels(actual_pixel)
            right = _coerce_channels(expected_pixel)
            width = max(len(left), len(right))
            left = left + (255,) * (width - len(left))
            right = right + (255,) * (width - len(right))
            if any(abs(int(a) - int(b)) > tolerance for a, b in zip(left, right, strict=True)):
                points.append((x, y))
    return points


def _neighbors(point: tuple[int, int], diagonal: bool = True) -> list[tuple[int, int]]:
    x, y = point
    offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if diagonal:
        offsets.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
    return [(x + dx, y + dy) for dx, dy in offsets]


def connected_components(points: Iterable[tuple[int, int]], diagonal: bool = True) -> list[list[tuple[int, int]]]:
    remaining = _coordinate_set(points)
    components = []
    while remaining:
        start = min(remaining, key=lambda item: (item[1], item[0]))
        queue = deque([start])
        remaining.remove(start)
        component = [start]
        while queue:
            current = queue.popleft()
            for neighbor in _neighbors(current, diagonal=diagonal):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)
                    component.append(neighbor)
        component.sort(key=lambda item: (item[1], item[0]))
        components.append(component)
    components.sort(key=lambda component: (component[0][1], component[0][0], len(component)))
    return components


def bounding_box(points: Sequence[tuple[int, int]]) -> dict[str, int]:
    if not points:
        return {"min_x": 0, "min_y": 0, "max_x": 0, "max_y": 0, "width": 0, "height": 0}
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    min_x = min(xs)
    min_y = min(ys)
    max_x = max(xs)
    max_y = max(ys)
    return {
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "width": max_x - min_x + 1,
        "height": max_y - min_y + 1,
    }


def cluster_shape(points: Sequence[tuple[int, int]]) -> str:
    box = bounding_box(points)
    width = int(box["width"])
    height = int(box["height"])
    count = len(points)
    if count == 0:
        return "empty"
    if count == 1:
        return "single-pixel"
    if width == 1 and height > 1:
        return "vertical-strip"
    if height == 1 and width > 1:
        return "horizontal-strip"
    if width == height and count >= width * height:
        return "filled-block"
    if width >= 4 and height >= 4 and count <= max(width, height):
        return "sparse-box"
    if count < max(width, height):
        return "scatter"
    return "cluster"


def cluster_density(points: Sequence[tuple[int, int]]) -> float:
    box = bounding_box(points)
    area = max(int(box["width"]) * int(box["height"]), 1)
    return round(len(points) / area, 6)


def cluster_perimeter(points: Sequence[tuple[int, int]]) -> int:
    if not points:
        return 0
    point_set = _coordinate_set(points)
    edges = 0
    for point in point_set:
        x, y = point
        for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if neighbor not in point_set:
                edges += 1
    return edges


def cluster_summary(points: Sequence[tuple[int, int]]) -> dict[str, object]:
    box = bounding_box(points)
    return {
        "point_count": len(points),
        "box": box,
        "shape": cluster_shape(points),
        "density": cluster_density(points),
        "perimeter": cluster_perimeter(points),
        "points": list(points),
    }


def cluster_issue_code(summary: Mapping[str, object]) -> str:
    shape = str(summary.get("shape", "cluster"))
    point_count = int(summary.get("point_count", 0) or 0)
    if shape in {"vertical-strip", "horizontal-strip"} and point_count >= 4:
        return "region-seam-drift"
    if shape == "single-pixel":
        return "region-single-pixel-drift"
    if point_count >= 25:
        return "region-large-cluster"
    return "region-cluster"


def region_cluster_summary(
    actual: PixelMatrix,
    expected: PixelMatrix,
    tolerance: int = 0,
    diagonal: bool = True,
) -> dict[str, object]:
    points = mismatch_points(actual, expected, tolerance=tolerance)
    components = connected_components(points, diagonal=diagonal)
    summaries = [cluster_summary(component) for component in components]
    for summary in summaries:
        summary["issue_code"] = cluster_issue_code(summary)
    summaries.sort(
        key=lambda item: (
            -int(item["point_count"]),
            int(dict(item["box"])["min_y"]),
            int(dict(item["box"])["min_x"]),
            str(item["shape"]),
        )
    )
    dominant = summaries[0] if summaries else None
    issues = []
    if dominant:
        if str(dominant["shape"]) in {"vertical-strip", "horizontal-strip"}:
            issues.append("clustered drift follows a seam-like shape")
        elif int(dominant["point_count"]) >= 25:
            issues.append("clustered drift covers a large connected region")
        elif len(summaries) > 3:
            issues.append("drift is spread across many disconnected regions")
    status = "block" if dominant and int(dominant["point_count"]) >= 25 else "warn" if summaries else "ok"
    return {
        "status": status,
        "severity": status,
        "passed": status != "block",
        "issue_codes": sorted({str(summary["issue_code"]) for summary in summaries}),
        "issues": issues,
        "cluster_count": len(summaries),
        "total_points": len(points),
        "largest_cluster_points": int(dominant["point_count"]) if dominant else 0,
        "clusters": summaries,
    }
