from __future__ import annotations

from typing import Iterable, Sequence


Pixel = int | float | Sequence[int | float]
PixelMatrix = Sequence[Sequence[Pixel]]


def _coerce_channels(pixel: Pixel) -> tuple[int, ...]:
    if isinstance(pixel, (int, float)):
        return (int(round(pixel)),)
    return tuple(int(round(float(channel))) for channel in pixel)


def matrix_dimensions(matrix: PixelMatrix) -> tuple[int, int, int]:
    height = len(matrix)
    width = len(matrix[0]) if height else 0
    if height and any(len(row) != width for row in matrix):
        raise ValueError("pixel matrix rows must have a stable width")
    channels = len(_coerce_channels(matrix[0][0])) if height and width else 0
    return (width, height, channels)


def _pixel_delta(left: Pixel, right: Pixel) -> tuple[int, int]:
    left_channels = _coerce_channels(left)
    right_channels = _coerce_channels(right)
    if len(left_channels) != len(right_channels):
        raise ValueError("pixel channel counts do not match")
    channel_deltas = [abs(a - b) for a, b in zip(left_channels, right_channels)]
    return (max(channel_deltas, default=0), sum(channel_deltas))


def diff_summary(
    actual: PixelMatrix,
    expected: PixelMatrix,
    tolerance: int = 0,
    max_mismatched_pixels: int = 0,
    mean_delta_limit: float | None = None,
) -> dict[str, float | int | bool]:
    actual_dims = matrix_dimensions(actual)
    expected_dims = matrix_dimensions(expected)
    if actual_dims != expected_dims:
        return {
            "passed": False,
            "size_match": False,
            "width": actual_dims[0],
            "height": actual_dims[1],
            "expected_width": expected_dims[0],
            "expected_height": expected_dims[1],
            "channels": max(actual_dims[2], expected_dims[2]),
            "mismatched_pixels": max(actual_dims[0] * actual_dims[1], expected_dims[0] * expected_dims[1]),
            "max_channel_delta": 255,
            "mean_pixel_delta": 255.0,
        }

    width, height, channels = actual_dims
    mismatched_pixels = 0
    total_pixel_delta = 0
    max_channel_delta = 0
    for y, (actual_row, expected_row) in enumerate(zip(actual, expected, strict=True)):
        for x, (actual_pixel, expected_pixel) in enumerate(zip(actual_row, expected_row, strict=True)):
            channel_delta, pixel_delta = _pixel_delta(actual_pixel, expected_pixel)
            max_channel_delta = max(max_channel_delta, channel_delta)
            total_pixel_delta += pixel_delta
            if channel_delta > tolerance:
                mismatched_pixels += 1

    total_pixels = width * height
    mean_pixel_delta = round(total_pixel_delta / max(total_pixels, 1), 4)
    passed = mismatched_pixels <= max_mismatched_pixels
    if mean_delta_limit is not None:
        passed = passed and mean_pixel_delta <= float(mean_delta_limit)
    return {
        "passed": passed,
        "size_match": True,
        "width": width,
        "height": height,
        "channels": channels,
        "mismatched_pixels": mismatched_pixels,
        "max_channel_delta": max_channel_delta,
        "mean_pixel_delta": mean_pixel_delta,
    }


def within_tolerance(
    actual: PixelMatrix,
    expected: PixelMatrix,
    tolerance: int = 0,
    max_mismatched_pixels: int = 0,
    mean_delta_limit: float | None = None,
) -> bool:
    return bool(
        diff_summary(
            actual,
            expected,
            tolerance=tolerance,
            max_mismatched_pixels=max_mismatched_pixels,
            mean_delta_limit=mean_delta_limit,
        )["passed"]
    )
