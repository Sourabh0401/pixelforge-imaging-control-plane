from __future__ import annotations

from typing import Iterable, Mapping, Sequence

from .render_manifest import render_manifest_digest
from .tile_coverage import tile_coverage_summary


def _tile_rows(manifest: Sequence[Mapping[str, object]] | Mapping[str, object]) -> list[dict[str, object]]:
    if isinstance(manifest, Mapping):
        rows = manifest.get("tiles", [])
    else:
        rows = manifest
    return [dict(row) for row in rows]


def normalized_tiles(manifest: Sequence[Mapping[str, object]] | Mapping[str, object]) -> list[dict[str, object]]:
    rows = _tile_rows(manifest)
    rows.sort(key=lambda row: (int(row.get("zoom", 0)), int(row.get("y", 0)), int(row.get("x", 0)), str(row.get("path", ""))))
    return rows


def validate_tile_manifest(
    manifest: Sequence[Mapping[str, object]] | Mapping[str, object],
    expected_tile_count: int | None = None,
    require_unique_paths: bool = True,
) -> list[str]:
    rows = normalized_tiles(manifest)
    issues: list[str] = []
    if expected_tile_count is not None and len(rows) != expected_tile_count:
        issues.append(f"tile_count expected {expected_tile_count} but got {len(rows)}")
    seen_paths: set[str] = set()
    for index, row in enumerate(rows):
        if "path" not in row:
            issues.append(f"tile {index} missing path")
        path = str(row.get("path", ""))
        if require_unique_paths and path in seen_paths:
            issues.append(f"duplicate tile path {path}")
        seen_paths.add(path)
    coverage = tile_coverage_summary(rows)
    issues.extend(str(issue) for issue in coverage["issues"])
    return issues


def manifest_digest(manifest: Sequence[Mapping[str, object]] | Mapping[str, object]) -> str:
    return render_manifest_digest({"artifacts": normalized_tiles(manifest), "bundle_id": "tiles", "lane": "tile-manifest"})


def manifest_summary(manifest: Sequence[Mapping[str, object]] | Mapping[str, object]) -> dict[str, object]:
    rows = normalized_tiles(manifest)
    zoom_levels = sorted({int(row.get("zoom", 0)) for row in rows})
    coverage = tile_coverage_summary(rows)
    return {
        "tile_count": len(rows),
        "zoom_levels": zoom_levels,
        "digest": manifest_digest(rows),
        "issues": validate_tile_manifest(rows),
        "coverage": coverage,
        "passed": not coverage["issues"] and not validate_tile_manifest(rows),
    }
