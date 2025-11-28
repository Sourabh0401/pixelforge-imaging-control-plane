from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping, Sequence


def normalize_tile(row: Mapping[str, object]) -> dict[str, object]:
    has_width = "width" in row or "tile_width" in row
    has_height = "height" in row or "tile_height" in row
    return {
        "path": str(row.get("path", "")).strip(),
        "x": int(row.get("x", row.get("tile_x", 0)) or 0),
        "y": int(row.get("y", row.get("tile_y", 0)) or 0),
        "width": int(row.get("width", 0) or 0),
        "height": int(row.get("height", 0) or 0),
        "zoom": int(row.get("zoom", 0) or 0),
        "codec": str(row.get("codec", row.get("format", "unknown")) or "unknown").lower(),
        "lane": str(row.get("lane", "unknown") or "unknown"),
        "_has_dimensions": bool(has_width or has_height),
    }


def normalized_tiles(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    items = [normalize_tile(row) for row in rows]
    items.sort(key=lambda row: (int(row["zoom"]), int(row["y"]), int(row["x"]), str(row["codec"]), str(row["path"])))
    return items


def duplicate_tiles(rows: Iterable[Mapping[str, object]]) -> list[str]:
    seen: set[tuple[int, int, int, str]] = set()
    duplicates: list[str] = []
    for row in normalized_tiles(rows):
        key = (int(row["zoom"]), int(row["x"]), int(row["y"]), str(row["codec"]))
        if key in seen:
            duplicates.append(f"duplicate tile at z{row['zoom']} {row['x']},{row['y']} for {row['codec']}")
        seen.add(key)
    return duplicates


def overlap_pairs(rows: Iterable[Mapping[str, object]]) -> list[str]:
    items = normalized_tiles(rows)
    overlaps: list[str] = []
    for index, left in enumerate(items):
        left_box = (
            int(left["x"]),
            int(left["y"]),
            int(left["x"]) + int(left["width"]),
            int(left["y"]) + int(left["height"]),
        )
        for right in items[index + 1 :]:
            if int(left["zoom"]) != int(right["zoom"]):
                continue
            if str(left["codec"]) != str(right["codec"]):
                continue
            right_box = (
                int(right["x"]),
                int(right["y"]),
                int(right["x"]) + int(right["width"]),
                int(right["y"]) + int(right["height"]),
            )
            horizontal = left_box[0] < right_box[2] and right_box[0] < left_box[2]
            vertical = left_box[1] < right_box[3] and right_box[1] < left_box[3]
            if horizontal and vertical:
                overlaps.append(f"tiles {left['path']} and {right['path']} overlap")
    return overlaps


def expected_positions(columns: int, rows: int, tile_width: int, tile_height: int) -> set[tuple[int, int]]:
    return {(column * tile_width, row * tile_height) for column in range(columns) for row in range(rows)}


def missing_positions(
    rows: Iterable[Mapping[str, object]],
    columns: int,
    row_count: int,
    tile_width: int,
    tile_height: int,
) -> list[tuple[int, int]]:
    expected = expected_positions(columns, row_count, tile_width, tile_height)
    actual = {(int(row["x"]), int(row["y"])) for row in normalized_tiles(rows)}
    return sorted(expected - actual)


def tile_coverage_summary(
    rows: Iterable[Mapping[str, object]],
    expected_columns: int | None = None,
    expected_rows: int | None = None,
    tile_width: int | None = None,
    tile_height: int | None = None,
) -> dict[str, object]:
    items = normalized_tiles(rows)
    issues = []
    issues.extend(duplicate_tiles(items))
    issues.extend(overlap_pairs(items))
    if any(bool(row.get("_has_dimensions")) and (int(row["width"]) <= 0 or int(row["height"]) <= 0) for row in items):
        issues.append("one or more tiles have non-positive dimensions")
    if expected_columns and expected_rows and tile_width and tile_height:
        for x, y in missing_positions(items, expected_columns, expected_rows, tile_width, tile_height):
            issues.append(f"missing tile at {x},{y}")
    lanes: dict[str, int] = defaultdict(int)
    codecs: dict[str, int] = defaultdict(int)
    zoom_levels: dict[int, int] = defaultdict(int)
    for row in items:
        lanes[str(row["lane"])] += 1
        codecs[str(row["codec"])] += 1
        zoom_levels[int(row["zoom"])] += 1
    status = "block" if issues else "ok"
    return {
        "passed": not issues,
        "status": status,
        "severity": status,
        "issue_codes": ["tile-coverage"] if issues else [],
        "issues": sorted(dict.fromkeys(issues)),
        "tile_count": len(items),
        "lane_counts": dict(sorted(lanes.items())),
        "codec_counts": dict(sorted(codecs.items())),
        "zoom_counts": {str(zoom): count for zoom, count in sorted(zoom_levels.items())},
    }
