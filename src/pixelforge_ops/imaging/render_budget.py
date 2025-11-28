from __future__ import annotations

from typing import Iterable, Mapping

from .lane_contracts import lane_priority


def budget_for_lane(lane: str) -> dict[str, int]:
    priority = lane_priority(lane)
    return {
        "max_runtime_ms": 180 if priority >= 90 else 240 if priority >= 80 else 320,
        "max_bytes": 650_000 if priority >= 90 else 900_000 if priority >= 80 else 1_250_000,
        "max_tile_count": 256 if "tiling" in lane or "thumbnail" in lane else 64,
    }


def summarize_budget(rows: Iterable[Mapping[str, object]], lane: str) -> dict[str, object]:
    budget = budget_for_lane(lane)
    items = [dict(row) for row in rows]
    runtimes = [int(item.get("runtime_ms", 0) or 0) for item in items]
    sizes = [int(item.get("bytes", item.get("size_bytes", 0)) or 0) for item in items]
    tile_count = sum(1 for item in items if str(item.get("artifact_type", "")) == "tile")
    issues = []
    if max(runtimes, default=0) > budget["max_runtime_ms"]:
        issues.append("render runtime exceeded lane budget")
    if sum(sizes) > budget["max_bytes"]:
        issues.append("artifact size exceeded lane budget")
    if tile_count > budget["max_tile_count"]:
        issues.append("tile count exceeded lane budget")
    status = "block" if issues else "ok"
    return {
        "passed": not issues,
        "status": status,
        "severity": status,
        "issue_codes": ["render-budget"] if issues else [],
        "issues": issues,
        "budget": budget,
        "max_runtime_ms": max(runtimes, default=0),
        "total_bytes": sum(sizes),
        "tile_count": tile_count,
    }

