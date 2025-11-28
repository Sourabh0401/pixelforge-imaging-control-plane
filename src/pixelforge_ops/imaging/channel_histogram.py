from __future__ import annotations

from typing import Iterable, Sequence

from .pixel_tolerance import Pixel, PixelMatrix, _coerce_channels, matrix_dimensions


def _channel_labels(count: int) -> tuple[str, ...]:
    defaults = ("red", "green", "blue", "alpha")
    if count <= len(defaults):
        return defaults[:count]
    return defaults + tuple(f"channel_{index}" for index in range(len(defaults), count))


def _empty_histogram(channel_count: int, bins: int) -> dict[str, list[int]]:
    return {label: [0 for _ in range(bins)] for label in _channel_labels(channel_count)}


def _bin_index(value: int, bins: int) -> int:
    value = max(0, min(255, value))
    return min(int((value / 256) * bins), bins - 1)


def build_histogram(matrix: PixelMatrix, bins: int = 16) -> dict[str, list[int]]:
    width, height, channel_count = matrix_dimensions(matrix)
    histogram = _empty_histogram(channel_count, bins)
    if width == 0 or height == 0:
        return histogram
    labels = _channel_labels(channel_count)
    for row in matrix:
        for pixel in row:
            channels = _coerce_channels(pixel)
            for index, label in enumerate(labels):
                histogram[label][_bin_index(int(channels[index]), bins)] += 1
    return histogram


def normalize_histogram(histogram: dict[str, list[int]]) -> dict[str, list[float]]:
    normalized: dict[str, list[float]] = {}
    for label, counts in histogram.items():
        total = sum(counts)
        if total == 0:
            normalized[label] = [0.0 for _ in counts]
            continue
        normalized[label] = [round(count / total, 6) for count in counts]
    return normalized


def histogram_overlap_score(left: dict[str, list[int]], right: dict[str, list[int]]) -> float:
    score = 0.0
    channels = sorted(set(left) | set(right))
    if not channels:
        return 1.0
    for label in channels:
        left_values = normalize_histogram({label: left.get(label, [])})[label]
        right_values = normalize_histogram({label: right.get(label, [])})[label]
        bins = max(len(left_values), len(right_values))
        left_values = left_values + [0.0] * (bins - len(left_values))
        right_values = right_values + [0.0] * (bins - len(right_values))
        score += sum(min(a, b) for a, b in zip(left_values, right_values, strict=True))
    return round(score / len(channels), 6)


def dominant_bins(histogram: dict[str, list[int]], top_n: int = 3) -> dict[str, list[int]]:
    dominant: dict[str, list[int]] = {}
    for label, counts in histogram.items():
        ranked = sorted(range(len(counts)), key=lambda index: (-counts[index], index))
        dominant[label] = ranked[:top_n]
    return dominant


def histogram_drift(actual: PixelMatrix, expected: PixelMatrix, bins: int = 16) -> dict[str, object]:
    actual_hist = build_histogram(actual, bins=bins)
    expected_hist = build_histogram(expected, bins=bins)
    actual_norm = normalize_histogram(actual_hist)
    expected_norm = normalize_histogram(expected_hist)
    deltas: dict[str, list[float]] = {}
    dominant_shift: dict[str, int] = {}
    max_delta = 0.0
    for label in sorted(set(actual_hist) | set(expected_hist)):
        left = actual_norm.get(label, [])
        right = expected_norm.get(label, [])
        width = max(len(left), len(right))
        left = left + [0.0] * (width - len(left))
        right = right + [0.0] * (width - len(right))
        deltas[label] = [round(abs(a - b), 6) for a, b in zip(left, right, strict=True)]
        max_delta = max(max_delta, max(deltas[label], default=0.0))
        actual_dom = dominant_bins(actual_hist).get(label, [0])
        expected_dom = dominant_bins(expected_hist).get(label, [0])
        dominant_shift[label] = abs(actual_dom[0] - expected_dom[0])
    return {
        "actual_histogram": actual_hist,
        "expected_histogram": expected_hist,
        "actual_normalized": actual_norm,
        "expected_normalized": expected_norm,
        "delta_by_channel": deltas,
        "max_delta": round(max_delta, 6),
        "overlap_score": histogram_overlap_score(actual_hist, expected_hist),
        "dominant_shift": dominant_shift,
    }


def classify_histogram_drift(summary: dict[str, object], warn_threshold: float = 0.03, block_threshold: float = 0.08) -> str:
    max_delta = float(summary.get("max_delta", 0.0))
    overlap = float(summary.get("overlap_score", 1.0))
    if max_delta >= block_threshold or overlap < max(1.0 - block_threshold * 4, 0.0):
        return "block"
    if max_delta >= warn_threshold or overlap < max(1.0 - warn_threshold * 4, 0.0):
        return "warn"
    return "ok"


def histogram_summary(
    actual: PixelMatrix,
    expected: PixelMatrix,
    bins: int = 16,
    warn_threshold: float = 0.03,
    block_threshold: float = 0.08,
    dominant_shift_limit: int = 2,
) -> dict[str, object]:
    summary = histogram_drift(actual, expected, bins=bins)
    issues: list[str] = []
    for label, shift in sorted(dict(summary["dominant_shift"]).items()):
        if shift > dominant_shift_limit:
            issues.append(f"{label} dominant bin shifted by {shift}")
    status = classify_histogram_drift(summary, warn_threshold=warn_threshold, block_threshold=block_threshold)
    if status == "warn" and not issues:
        issues.append("histogram drift exceeded warning threshold")
    if status == "block" and not issues:
        issues.append("histogram drift exceeded blocking threshold")
    return {
        **summary,
        "status": status,
        "severity": status,
        "issue_codes": ["histogram-drift"] if issues else [],
        "issues": issues,
        "passed": status != "block",
    }

