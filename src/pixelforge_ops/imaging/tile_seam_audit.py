from __future__ import annotations

from typing import Iterable, Mapping, Sequence

from .pixel_tolerance import PixelMatrix, _coerce_channels


def _edge_signature(matrix: PixelMatrix, edge: str) -> list[tuple[int, ...]]:
    if not matrix:
        return []
    if edge == "left":
        return [_coerce_channels(row[0]) for row in matrix if row]
    if edge == "right":
        return [_coerce_channels(row[-1]) for row in matrix if row]
    if edge == "top":
        return [_coerce_channels(pixel) for pixel in matrix[0]]
    if edge == "bottom":
        return [_coerce_channels(pixel) for pixel in matrix[-1]]
    raise KeyError(edge)


def seam_difference(left: PixelMatrix, right: PixelMatrix, edge_left: str, edge_right: str) -> float:
    left_edge = _edge_signature(left, edge_left)
    right_edge = _edge_signature(right, edge_right)
    pairs = zip(left_edge, right_edge, strict=False)
    total = 0
    count = 0
    for left_pixel, right_pixel in pairs:
        total += sum(abs(a - b) for a, b in zip(left_pixel, right_pixel, strict=True))
        count += 1
    return round(total / max(count, 1), 6)


def tile_seam_summary(
    seams: Iterable[Mapping[str, object]],
    warn_threshold: float = 4.0,
    block_threshold: float = 10.0,
) -> dict[str, object]:
    issues = []
    worst = 0.0
    for seam in seams:
        delta = seam_difference(
            seam["left_matrix"],
            seam["right_matrix"],
            str(seam.get("left_edge", "right")),
            str(seam.get("right_edge", "left")),
        )
        worst = max(worst, delta)
        if delta >= block_threshold:
            issues.append(f"blocking seam delta at {seam.get('name', 'seam')}: {delta}")
        elif delta >= warn_threshold:
            issues.append(f"warn seam delta at {seam.get('name', 'seam')}: {delta}")
    status = "block" if any(text.startswith("blocking") for text in issues) else "warn" if issues else "ok"
    return {
        "passed": status != "block",
        "status": status,
        "severity": status,
        "issue_codes": ["tile-seam"] if issues else [],
        "issues": issues,
        "worst_delta": worst,
    }

