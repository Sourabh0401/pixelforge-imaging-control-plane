from __future__ import annotations

from .channel_histogram import histogram_summary
from .color_delta import color_delta_summary
from .pixel_tolerance import PixelMatrix, diff_summary


def diff_region_bounds(actual: PixelMatrix, expected: PixelMatrix, tolerance: int = 0) -> dict[str, int | None]:
    if len(actual) != len(expected) or (actual and expected and len(actual[0]) != len(expected[0])):
        return {"min_x": None, "min_y": None, "max_x": None, "max_y": None}
    min_x: int | None = None
    min_y: int | None = None
    max_x: int | None = None
    max_y: int | None = None
    for y, (actual_row, expected_row) in enumerate(zip(actual, expected, strict=True)):
        for x, (actual_pixel, expected_pixel) in enumerate(zip(actual_row, expected_row, strict=True)):
            summary = diff_summary([[actual_pixel]], [[expected_pixel]], tolerance=tolerance)
            if summary["mismatched_pixels"]:
                min_x = x if min_x is None else min(min_x, x)
                min_y = y if min_y is None else min(min_y, y)
                max_x = x if max_x is None else max(max_x, x)
                max_y = y if max_y is None else max(max_y, y)
    return {"min_x": min_x, "min_y": min_y, "max_x": max_x, "max_y": max_y}


def golden_diff(
    actual: PixelMatrix,
    expected: PixelMatrix,
    tolerance: int = 0,
    max_mismatched_pixels: int = 0,
    mean_delta_limit: float | None = None,
) -> dict[str, float | int | bool | None]:
    summary = diff_summary(
        actual,
        expected,
        tolerance=tolerance,
        max_mismatched_pixels=max_mismatched_pixels,
        mean_delta_limit=mean_delta_limit,
    )
    histogram = histogram_summary(actual, expected)
    color = color_delta_summary(actual, expected)
    total_pixels = int(summary.get("width", 0)) * int(summary.get("height", 0))
    mismatch_ratio = round(int(summary["mismatched_pixels"]) / max(total_pixels, 1), 6)
    return {
        **summary,
        "difference_ratio": mismatch_ratio,
        "status": "block" if not summary["passed"] or histogram["status"] == "block" or color["status"] == "block" else "warn" if histogram["status"] == "warn" or color["status"] == "warn" else "ok",
        "histogram_status": histogram["status"],
        "color_status": color["status"],
        **diff_region_bounds(actual, expected, tolerance=tolerance),
    }


def passes_golden_diff(
    actual: PixelMatrix,
    expected: PixelMatrix,
    tolerance: int = 0,
    max_mismatched_pixels: int = 0,
    mean_delta_limit: float | None = None,
) -> bool:
    return bool(
        golden_diff(
            actual,
            expected,
            tolerance=tolerance,
            max_mismatched_pixels=max_mismatched_pixels,
            mean_delta_limit=mean_delta_limit,
        )["passed"]
    )
