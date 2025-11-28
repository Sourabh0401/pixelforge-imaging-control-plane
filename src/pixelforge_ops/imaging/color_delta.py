from __future__ import annotations

import math
from typing import Iterable, Sequence

from .pixel_tolerance import Pixel, PixelMatrix, _coerce_channels, matrix_dimensions


def _channel_weights(channel_count: int, weights: Sequence[float] | None = None) -> tuple[float, ...]:
    if weights is None:
        defaults = (0.299, 0.587, 0.114, 1.0)
        return tuple(defaults[index] if index < len(defaults) else 1.0 for index in range(channel_count))
    values = [float(value) for value in weights]
    if len(values) < channel_count:
        values.extend([1.0] * (channel_count - len(values)))
    return tuple(values[:channel_count])


def weighted_channel_delta(left: Pixel, right: Pixel, weights: Sequence[float] | None = None) -> tuple[float, tuple[int, ...]]:
    left_channels = _coerce_channels(left)
    right_channels = _coerce_channels(right)
    if len(left_channels) != len(right_channels):
        raise ValueError("pixel channel counts do not match")
    deltas = tuple(abs(a - b) for a, b in zip(left_channels, right_channels))
    factors = _channel_weights(len(deltas), weights)
    value = sum(delta * weight for delta, weight in zip(deltas, factors, strict=True))
    return round(value, 6), deltas


def delta_map(actual: PixelMatrix, expected: PixelMatrix, weights: Sequence[float] | None = None) -> list[list[float]]:
    if matrix_dimensions(actual) != matrix_dimensions(expected):
        raise ValueError("matrices must share dimensions")
    rows: list[list[float]] = []
    for actual_row, expected_row in zip(actual, expected, strict=True):
        rows.append([weighted_channel_delta(left, right, weights=weights)[0] for left, right in zip(actual_row, expected_row, strict=True)])
    return rows


def percentile(values: Iterable[float], percent: float) -> float:
    data = sorted(float(value) for value in values)
    if not data:
        return 0.0
    target = max(0.0, min(percent, 100.0))
    if len(data) == 1:
        return round(data[0], 6)
    position = (len(data) - 1) * (target / 100.0)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return round(data[lower], 6)
    ratio = position - lower
    return round(data[lower] + (data[upper] - data[lower]) * ratio, 6)


def color_delta_summary(
    actual: PixelMatrix,
    expected: PixelMatrix,
    weights: Sequence[float] | None = None,
    warn_threshold: float = 6.0,
    block_threshold: float = 18.0,
    percentile_threshold: float = 12.0,
    alpha_weight: float = 2.0,
) -> dict[str, object]:
    if matrix_dimensions(actual) != matrix_dimensions(expected):
        actual_dims = matrix_dimensions(actual)
        expected_dims = matrix_dimensions(expected)
        return {
            "passed": False,
            "status": "block",
            "severity": "block",
            "issue_codes": ["dimension-mismatch"],
            "issues": [f"dimension mismatch {actual_dims} != {expected_dims}"],
            "mean_delta": 255.0,
            "rms_delta": 255.0,
            "max_delta": 255.0,
            "p95_delta": 255.0,
            "alpha_only_pixels": 0,
            "high_delta_pixels": 0,
        }

    width, height, channels = matrix_dimensions(actual)
    effective_weights = list(_channel_weights(channels, weights))
    if channels >= 4:
        effective_weights[3] = alpha_weight
    deltas: list[float] = []
    alpha_only_pixels = 0
    high_delta_pixels = 0
    issues: list[str] = []
    for actual_row, expected_row in zip(actual, expected, strict=True):
        for left, right in zip(actual_row, expected_row, strict=True):
            value, channel_deltas = weighted_channel_delta(left, right, weights=effective_weights)
            deltas.append(value)
            if channels >= 4 and channel_deltas[3] > 0 and sum(channel_deltas[:3]) == 0:
                alpha_only_pixels += 1
            if value >= percentile_threshold:
                high_delta_pixels += 1
    total = max(width * height, 1)
    mean_delta = round(sum(deltas) / total, 6)
    rms_delta = round(math.sqrt(sum(value * value for value in deltas) / total), 6)
    max_delta = round(max(deltas, default=0.0), 6)
    p95_delta = percentile(deltas, 95.0)
    if max_delta >= block_threshold or p95_delta >= percentile_threshold * 2:
        status = "block"
        issues.append("color delta exceeded blocking threshold")
    elif mean_delta >= warn_threshold or p95_delta >= percentile_threshold:
        status = "warn"
        issues.append("color delta exceeded warning threshold")
    else:
        status = "ok"
    if alpha_only_pixels and status != "ok":
        issues.append("alpha-only differences detected")
    return {
        "passed": status != "block",
        "status": status,
        "severity": status,
        "issue_codes": ["color-delta"] if issues else [],
        "issues": issues,
        "mean_delta": mean_delta,
        "rms_delta": rms_delta,
        "max_delta": max_delta,
        "p95_delta": p95_delta,
        "alpha_only_pixels": alpha_only_pixels,
        "high_delta_pixels": high_delta_pixels,
        "pixel_count": total,
    }
