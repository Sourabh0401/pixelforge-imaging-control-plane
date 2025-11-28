from __future__ import annotations

from typing import Sequence


RGBA = Sequence[int | float]
AlphaMatrix = Sequence[Sequence[RGBA]]


def halo_pixels(matrix: AlphaMatrix, alpha_floor: int = 1, alpha_ceiling: int = 64, color_floor: int = 8) -> list[tuple[int, int]]:
    points = []
    for y, row in enumerate(matrix):
        for x, pixel in enumerate(row):
            red, green, blue, alpha = (int(round(float(channel))) for channel in pixel[:4])
            if alpha_floor <= alpha <= alpha_ceiling and max(red, green, blue) >= color_floor:
                points.append((x, y))
    return points


def transparency_halo_summary(matrix: AlphaMatrix, max_halo_pixels: int = 0) -> dict[str, object]:
    points = halo_pixels(matrix)
    issues = []
    if len(points) > max_halo_pixels:
        issues.append("transparency halo exceeded threshold")
    status = "block" if issues else "ok"
    return {
        "passed": not issues,
        "status": status,
        "severity": status,
        "issue_codes": ["transparency-halo"] if issues else [],
        "issues": issues,
        "halo_pixels": len(points),
        "sample_points": points[:12],
    }

