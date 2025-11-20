from __future__ import annotations

from typing import Sequence


RGBA = Sequence[int | float]
AlphaMatrix = Sequence[Sequence[RGBA]]


def transparent_edge_summary(matrix: AlphaMatrix) -> dict[str, int]:
    color_leak_pixels = 0
    unpremultiplied_pixels = 0
    edge_noise_pixels = 0
    height = len(matrix)
    width = len(matrix[0]) if height else 0
    for y, row in enumerate(matrix):
        for x, pixel in enumerate(row):
            red, green, blue, alpha = (int(round(float(channel))) for channel in pixel[:4])
            if alpha == 0 and any(channel != 0 for channel in (red, green, blue)):
                color_leak_pixels += 1
            if alpha > 0 and max(red, green, blue) > alpha:
                unpremultiplied_pixels += 1
            if (x in {0, width - 1} or y in {0, height - 1}) and 0 < alpha < 255:
                edge_noise_pixels += 1
    return {
        "color_leak_pixels": color_leak_pixels,
        "unpremultiplied_pixels": unpremultiplied_pixels,
        "edge_noise_pixels": edge_noise_pixels,
        "width": width,
        "height": height,
    }


def audit_alpha_matrix(
    matrix: AlphaMatrix,
    max_color_leak: int = 0,
    max_unpremultiplied: int = 0,
    max_edge_noise: int = 0,
) -> dict[str, int | bool]:
    summary = transparent_edge_summary(matrix)
    passed = (
        summary["color_leak_pixels"] <= max_color_leak
        and summary["unpremultiplied_pixels"] <= max_unpremultiplied
        and summary["edge_noise_pixels"] <= max_edge_noise
    )
    return {
        **summary,
        "passed": passed,
        "max_color_leak": max_color_leak,
        "max_unpremultiplied": max_unpremultiplied,
        "max_edge_noise": max_edge_noise,
    }
