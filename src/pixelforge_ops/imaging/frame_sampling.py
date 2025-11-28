from __future__ import annotations

from typing import Iterable, Mapping


def sample_points(width: int, height: int) -> list[tuple[int, int]]:
    if width <= 0 or height <= 0:
        return []
    candidates = {
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
        (width // 2, height // 2),
        (width // 3, height // 3),
        ((2 * width) // 3, (2 * height) // 3),
    }
    return sorted((x, y) for x, y in candidates if 0 <= x < width and 0 <= y < height)


def edge_band_points(width: int, height: int, band: int = 1) -> list[tuple[int, int]]:
    points: set[tuple[int, int]] = set()
    for y in range(height):
        for x in range(width):
            if x < band or y < band or x >= max(width - band, 0) or y >= max(height - band, 0):
                points.add((x, y))
    return sorted(points)


def seam_points(tile_width: int, tile_height: int, columns: int, rows: int) -> list[tuple[int, int]]:
    points: set[tuple[int, int]] = set()
    full_width = tile_width * max(columns, 0)
    full_height = tile_height * max(rows, 0)
    for column in range(1, columns):
        seam_x = column * tile_width
        for y in range(full_height):
            if 0 <= seam_x - 1 < full_width:
                points.add((seam_x - 1, y))
            if 0 <= seam_x < full_width:
                points.add((seam_x, y))
    for row in range(1, rows):
        seam_y = row * tile_height
        for x in range(full_width):
            if 0 <= seam_y - 1 < full_height:
                points.add((x, seam_y - 1))
            if 0 <= seam_y < full_height:
                points.add((x, seam_y))
    return sorted(points)


def region_sample_points(region: Mapping[str, int], stride: int = 1) -> list[tuple[int, int]]:
    width = max(int(region.get("width", 0)), 0)
    height = max(int(region.get("height", 0)), 0)
    left = int(region.get("x", 0))
    top = int(region.get("y", 0))
    if width == 0 or height == 0:
        return []
    step = max(stride, 1)
    points = []
    for y in range(top, top + height, step):
        for x in range(left, left + width, step):
            points.append((x, y))
    anchor_points = sample_points(width, height)
    points.extend((left + x, top + y) for x, y in anchor_points)
    return sorted(dict.fromkeys(points))


def alpha_candidate_points(matrix: Iterable[Iterable[object]]) -> list[tuple[int, int]]:
    rows = list(matrix)
    points: list[tuple[int, int]] = []
    for y, row in enumerate(rows):
        for x, pixel in enumerate(row):
            if isinstance(pixel, (list, tuple)) and len(pixel) >= 4 and int(pixel[3]) < 255:
                points.append((x, y))
    return sorted(points)

