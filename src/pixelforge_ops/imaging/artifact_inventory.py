from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping, Sequence

from pixelforge_ops.utils import json_digest


def normalize_artifact(row: Mapping[str, object], default_lane: str = "unknown") -> dict[str, object]:
    payload = dict(row)
    payload["lane"] = str(payload.get("lane", default_lane) or default_lane)
    payload["codec"] = str(payload.get("codec", payload.get("format", "unknown")) or "unknown").lower()
    payload["artifact_type"] = str(payload.get("artifact_type", payload.get("kind", "unknown")) or "unknown").lower()
    payload["path"] = str(payload.get("path", "")).strip()
    payload["width"] = int(payload.get("width", 0) or 0)
    payload["height"] = int(payload.get("height", 0) or 0)
    payload["tile_x"] = int(payload.get("tile_x", payload.get("x", 0)) or 0)
    payload["tile_y"] = int(payload.get("tile_y", payload.get("y", 0)) or 0)
    payload["zoom"] = int(payload.get("zoom", 0) or 0)
    payload["bytes"] = int(payload.get("bytes", payload.get("size_bytes", 0)) or 0)
    payload["alpha"] = bool(payload.get("alpha", False))
    payload["required"] = bool(payload.get("required", False))
    payload["status"] = str(payload.get("status", "present") or "present").lower()
    return payload


def normalized_artifacts(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    items = [normalize_artifact(row) for row in rows]
    items.sort(
        key=lambda row: (
            str(row["lane"]),
            str(row["codec"]),
            str(row["artifact_type"]),
            int(row["zoom"]),
            int(row["tile_y"]),
            int(row["tile_x"]),
            str(row["path"]),
        )
    )
    return items


def lane_groups(rows: Iterable[Mapping[str, object]]) -> dict[str, list[dict[str, object]]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in normalized_artifacts(rows):
        groups[str(row["lane"])].append(row)
    return {lane: items for lane, items in sorted(groups.items())}


def codec_groups(rows: Iterable[Mapping[str, object]]) -> dict[str, list[dict[str, object]]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in normalized_artifacts(rows):
        groups[str(row["codec"])].append(row)
    return {codec: items for codec, items in sorted(groups.items())}


def artifact_type_groups(rows: Iterable[Mapping[str, object]]) -> dict[str, list[dict[str, object]]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in normalized_artifacts(rows):
        groups[str(row["artifact_type"])].append(row)
    return {artifact_type: items for artifact_type, items in sorted(groups.items())}


def path_collisions(rows: Iterable[Mapping[str, object]]) -> list[str]:
    seen: dict[str, tuple[str, str]] = {}
    collisions: list[str] = []
    for row in normalized_artifacts(rows):
        path = str(row["path"])
        identity = (str(row["lane"]), str(row["codec"]))
        previous = seen.get(path)
        if previous is None:
            seen[path] = identity
            continue
        if previous != identity:
            collisions.append(path)
    return sorted(dict.fromkeys(collisions))


def missing_required_fields(rows: Iterable[Mapping[str, object]]) -> list[str]:
    issues: list[str] = []
    for index, row in enumerate(normalized_artifacts(rows)):
        if not row["path"]:
            issues.append(f"artifact {index} missing path")
        if int(row["width"]) < 0 or int(row["height"]) < 0:
            issues.append(f"artifact {index} has negative dimensions")
        if int(row["bytes"]) < 0:
            issues.append(f"artifact {index} has negative size")
        if str(row["status"]) not in {"present", "missing", "generated", "reused"}:
            issues.append(f"artifact {index} has unsupported status {row['status']}")
    return issues


def required_paths(rows: Iterable[Mapping[str, object]]) -> list[str]:
    paths = [str(row["path"]) for row in normalized_artifacts(rows) if bool(row["required"]) and row["path"]]
    return sorted(dict.fromkeys(paths))


def missing_required_paths(rows: Iterable[Mapping[str, object]]) -> list[str]:
    missing = [str(row["path"]) for row in normalized_artifacts(rows) if bool(row["required"]) and str(row["status"]) == "missing"]
    return sorted(dict.fromkeys(path for path in missing if path))


def missing_lane_codecs(rows: Iterable[Mapping[str, object]], required_codecs: Sequence[str]) -> dict[str, list[str]]:
    required = [str(codec).lower() for codec in required_codecs]
    missing: dict[str, list[str]] = {}
    for lane, items in lane_groups(rows).items():
        available = {str(row["codec"]) for row in items}
        absent = [codec for codec in required if codec not in available]
        if absent:
            missing[lane] = absent
    return dict(sorted(missing.items()))


def missing_lanes(rows: Iterable[Mapping[str, object]], required_lanes: Sequence[str]) -> list[str]:
    available = {str(row["lane"]) for row in normalized_artifacts(rows)}
    return sorted(lane for lane in required_lanes if lane not in available)


def size_totals_by_lane(rows: Iterable[Mapping[str, object]]) -> dict[str, int]:
    totals: dict[str, int] = defaultdict(int)
    for row in normalized_artifacts(rows):
        totals[str(row["lane"])] += int(row["bytes"])
    return dict(sorted(totals.items()))


def inventory_payload(rows: Iterable[Mapping[str, object]]) -> dict[str, object]:
    items = normalized_artifacts(rows)
    return {
        "items": items,
        "paths": [str(row["path"]) for row in items],
        "lanes": sorted({str(row["lane"]) for row in items}),
        "codecs": sorted({str(row["codec"]) for row in items}),
    }


def inventory_digest(rows: Iterable[Mapping[str, object]]) -> str:
    return json_digest(inventory_payload(rows))


def artifact_inventory_summary(
    rows: Iterable[Mapping[str, object]],
    required_codecs: Sequence[str] = (),
    required_artifact_types: Sequence[str] = (),
    required_lanes: Sequence[str] = (),
) -> dict[str, object]:
    items = normalized_artifacts(rows)
    artifact_types = artifact_type_groups(items)
    missing_types = [
        artifact_type
        for artifact_type in sorted({str(name).lower() for name in required_artifact_types})
        if artifact_type not in artifact_types
    ]
    issues = []
    issues.extend(missing_required_fields(items))
    issues.extend(f"path collision: {path}" for path in path_collisions(items))
    issues.extend(f"required path missing: {path}" for path in missing_required_paths(items))
    issues.extend(f"missing artifact type: {artifact_type}" for artifact_type in missing_types)
    for lane, codecs in missing_lane_codecs(items, required_codecs).items():
        issues.append(f"lane {lane} missing codecs: {', '.join(codecs)}")
    for lane in missing_lanes(items, required_lanes):
        issues.append(f"missing lane: {lane}")
    return {
        "artifact_count": len(items),
        "lanes": sorted({str(row['lane']) for row in items}),
        "codecs": sorted({str(row['codec']) for row in items}),
        "artifact_types": sorted(artifact_types),
        "required_paths": required_paths(items),
        "size_bytes_by_lane": size_totals_by_lane(items),
        "path_collisions": path_collisions(items),
        "digest": inventory_digest(items),
        "issues": sorted(dict.fromkeys(issues)),
        "passed": not issues,
    }

