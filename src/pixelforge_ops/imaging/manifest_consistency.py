from __future__ import annotations

"""
Consistency checks between render manifests and older accepted packets.

Render-manifest validation tells us whether a single manifest is internally
well-formed. This module looks sideways instead: how did the current manifest
change compared with a reference packet, what category does that change belong
to, and can the release team explain it without hand-parsing both payloads.
"""

from collections import Counter
from typing import Iterable, Mapping

from pixelforge_ops.utils import json_digest


def _artifact_key(row: Mapping[str, object]) -> tuple[str, str, str]:
    return (
        str(row.get("path", "")),
        str(row.get("codec", "unknown")),
        str(row.get("artifact_type", "frame")),
    )


def _artifact_map(rows: Iterable[Mapping[str, object]]) -> dict[tuple[str, str, str], dict[str, object]]:
    items = { _artifact_key(row): dict(row) for row in rows }
    return dict(sorted(items.items(), key=lambda item: item[0]))


def artifact_delta(left: Mapping[str, object], right: Mapping[str, object]) -> dict[str, list[str]]:
    left_items = _artifact_map(left.get("artifacts", []))
    right_items = _artifact_map(right.get("artifacts", []))
    left_keys = set(left_items)
    right_keys = set(right_items)
    return {
        "added": sorted("/".join(key) for key in right_keys - left_keys),
        "removed": sorted("/".join(key) for key in left_keys - right_keys),
        "shared": sorted("/".join(key) for key in left_keys & right_keys),
    }


def metadata_delta(left: Mapping[str, object], right: Mapping[str, object]) -> dict[str, object]:
    left_meta = dict(left.get("metadata", {}))
    right_meta = dict(right.get("metadata", {}))
    all_keys = sorted(set(left_meta) | set(right_meta))
    added = []
    removed = []
    changed = []
    unchanged = []
    for key in all_keys:
        if key not in left_meta:
            added.append(key)
        elif key not in right_meta:
            removed.append(key)
        elif left_meta[key] != right_meta[key]:
            changed.append(key)
        else:
            unchanged.append(key)
    return {"added": added, "removed": removed, "changed": changed, "unchanged": unchanged}


def lane_contract_delta(left: Mapping[str, object], right: Mapping[str, object]) -> dict[str, object]:
    left_contract = dict(left.get("lane_contract", {}))
    right_contract = dict(right.get("lane_contract", {}))
    changed = {}
    for key in sorted(set(left_contract) | set(right_contract)):
        if left_contract.get(key) != right_contract.get(key):
            changed[key] = {"left": left_contract.get(key), "right": right_contract.get(key)}
    return changed


def classify_manifest_drift(left: Mapping[str, object], right: Mapping[str, object]) -> list[str]:
    artifact = artifact_delta(left, right)
    metadata = metadata_delta(left, right)
    contract = lane_contract_delta(left, right)
    categories = []
    if artifact["added"] or artifact["removed"]:
        categories.append("artifact-set-changed")
    if metadata["changed"] or metadata["added"] or metadata["removed"]:
        categories.append("metadata-changed")
    if contract:
        categories.append("lane-contract-changed")
    if str(left.get("release_channel")) != str(right.get("release_channel")):
        categories.append("release-channel-changed")
    if not categories and str(left.get("digest")) != str(right.get("digest")):
        categories.append("digest-only-change")
    return categories


def changed_codecs(left: Mapping[str, object], right: Mapping[str, object]) -> list[str]:
    left_codecs = Counter(str(row.get("codec", "unknown")) for row in left.get("artifacts", []))
    right_codecs = Counter(str(row.get("codec", "unknown")) for row in right.get("artifacts", []))
    return sorted(codec for codec in set(left_codecs) | set(right_codecs) if left_codecs[codec] != right_codecs[codec])


def changed_lanes(left: Mapping[str, object], right: Mapping[str, object]) -> list[str]:
    left_lanes = Counter(str(row.get("lane", "unknown")) for row in left.get("artifacts", []))
    right_lanes = Counter(str(row.get("lane", "unknown")) for row in right.get("artifacts", []))
    return sorted(lane for lane in set(left_lanes) | set(right_lanes) if left_lanes[lane] != right_lanes[lane])


def stable_digest_pair(left: Mapping[str, object], right: Mapping[str, object]) -> str:
    payload = {
        "left_digest": str(left.get("digest", "")),
        "right_digest": str(right.get("digest", "")),
        "left_bundle": str(left.get("bundle_id", "")),
        "right_bundle": str(right.get("bundle_id", "")),
    }
    return json_digest(payload)


def manifest_consistency_summary(
    current: Mapping[str, object],
    previous: Mapping[str, object] | None = None,
    allowed_categories: Iterable[str] = (),
) -> dict[str, object]:
    if previous is None:
        return {
            "status": "ok",
            "severity": "ok",
            "passed": True,
            "issue_codes": [],
            "issues": [],
            "categories": [],
            "artifact_delta": {"added": [], "removed": [], "shared": []},
            "metadata_delta": {"added": [], "removed": [], "changed": [], "unchanged": []},
            "contract_delta": {},
            "changed_codecs": [],
            "changed_lanes": [],
            "digest_pair": stable_digest_pair(current, current),
        }
    categories = classify_manifest_drift(previous, current)
    allowed = {str(value) for value in allowed_categories}
    blocking_categories = [category for category in categories if category not in allowed]
    issues = [f"manifest consistency category: {category}" for category in blocking_categories]
    status = "block" if blocking_categories else "warn" if categories else "ok"
    return {
        "status": status,
        "severity": status,
        "passed": status != "block",
        "issue_codes": ["manifest-consistency"] if categories else [],
        "issues": issues,
        "categories": categories,
        "artifact_delta": artifact_delta(previous, current),
        "metadata_delta": metadata_delta(previous, current),
        "contract_delta": lane_contract_delta(previous, current),
        "changed_codecs": changed_codecs(previous, current),
        "changed_lanes": changed_lanes(previous, current),
        "digest_pair": stable_digest_pair(previous, current),
    }
