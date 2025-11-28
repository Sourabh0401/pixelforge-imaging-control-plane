from __future__ import annotations

from typing import Iterable, Mapping, Sequence

from pixelforge_ops.utils import json_digest

from .artifact_inventory import artifact_inventory_summary, normalized_artifacts
from .lane_contracts import lane_contract, lane_release_channel
from .tile_coverage import tile_coverage_summary


def build_render_manifest(
    bundle_id: str,
    lane: str,
    artifacts: Iterable[Mapping[str, object]],
    metadata: Mapping[str, object] | None = None,
    release_channel: str | None = None,
) -> dict[str, object]:
    items = normalized_artifacts(artifacts)
    contract = lane_contract(lane)
    inventory = artifact_inventory_summary(
        items,
        required_codecs=contract["required_codecs"],
        required_lanes=[lane],
    )
    manifest = {
        "bundle_id": bundle_id,
        "lane": lane,
        "release_channel": release_channel or lane_release_channel(lane),
        "lane_contract": contract,
        "artifacts": items,
        "metadata": dict(metadata or {}),
        "inventory": inventory,
    }
    manifest["digest"] = render_manifest_digest(manifest)
    return manifest


def render_manifest_digest(manifest: Mapping[str, object]) -> str:
    payload = {key: value for key, value in dict(manifest).items() if key != "digest"}
    return json_digest(payload)


def validate_render_manifest(
    manifest: Mapping[str, object],
    expected_tile_columns: int | None = None,
    expected_tile_rows: int | None = None,
    expected_tile_width: int | None = None,
    expected_tile_height: int | None = None,
) -> list[str]:
    payload = dict(manifest)
    issues: list[str] = []
    bundle_id = str(payload.get("bundle_id", "")).strip()
    lane = str(payload.get("lane", "")).strip()
    if not bundle_id:
        issues.append("render manifest missing bundle_id")
    if not lane:
        issues.append("render manifest missing lane")
    digest = str(payload.get("digest", "")).strip()
    if digest and digest != render_manifest_digest(payload):
        issues.append("render manifest digest mismatch")
    inventory = payload.get("inventory", {})
    if isinstance(inventory, Mapping):
        issues.extend(str(issue) for issue in inventory.get("issues", []))
    tiles = [row for row in payload.get("artifacts", []) if str(row.get("artifact_type")) == "tile"]
    if tiles:
        tile_summary = tile_coverage_summary(
            tiles,
            expected_columns=expected_tile_columns,
            expected_rows=expected_tile_rows,
            tile_width=expected_tile_width,
            tile_height=expected_tile_height,
        )
        issues.extend(str(issue) for issue in tile_summary["issues"])
    return sorted(dict.fromkeys(issues))


def compare_render_manifests(left: Mapping[str, object], right: Mapping[str, object]) -> dict[str, object]:
    left_payload = dict(left)
    right_payload = dict(right)
    left_artifacts = {(str(row.get("path")), str(row.get("codec")), str(row.get("artifact_type"))) for row in left_payload.get("artifacts", [])}
    right_artifacts = {(str(row.get("path")), str(row.get("codec")), str(row.get("artifact_type"))) for row in right_payload.get("artifacts", [])}
    return {
        "digest_changed": render_manifest_digest(left_payload) != render_manifest_digest(right_payload),
        "added_artifacts": sorted("/".join(item) for item in right_artifacts - left_artifacts),
        "removed_artifacts": sorted("/".join(item) for item in left_artifacts - right_artifacts),
        "metadata_changed": dict(left_payload.get("metadata", {})) != dict(right_payload.get("metadata", {})),
    }


def render_manifest_summary(manifest: Mapping[str, object]) -> dict[str, object]:
    payload = dict(manifest)
    issues = validate_render_manifest(payload)
    artifacts = normalized_artifacts(payload.get("artifacts", []))
    return {
        "bundle_id": payload.get("bundle_id"),
        "lane": payload.get("lane"),
        "artifact_count": len(artifacts),
        "digest": render_manifest_digest(payload),
        "issues": issues,
        "passed": not issues,
        "release_channel": payload.get("release_channel"),
    }
