from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping

from pixelforge_ops.utils import json_digest


def artifact_signature(row: Mapping[str, object]) -> str:
    payload = {
        "path": str(row.get("path", "")),
        "codec": str(row.get("codec", "")),
        "lane": str(row.get("lane", "")),
        "artifact_type": str(row.get("artifact_type", "")),
        "digest": str(row.get("digest", "")),
    }
    return json_digest(payload)


def lineage_from_manifests(manifests: Iterable[Mapping[str, object]]) -> dict[str, list[dict[str, object]]]:
    history: dict[str, list[dict[str, object]]] = defaultdict(list)
    for manifest in manifests:
        bundle_id = str(manifest.get("bundle_id", "bundle"))
        lane = str(manifest.get("lane", "lane"))
        manifest_digest = str(manifest.get("digest", ""))
        for artifact in manifest.get("artifacts", []):
            record = dict(artifact)
            record["bundle_id"] = bundle_id
            record["lane"] = lane
            record["manifest_digest"] = manifest_digest
            history[str(record.get("path", ""))].append(record)
    for path in history:
        history[path].sort(key=lambda row: (str(row.get("manifest_digest")), str(row.get("codec")), str(row.get("artifact_type"))))
    return dict(sorted(history.items()))


def changed_paths(manifests: Iterable[Mapping[str, object]]) -> list[str]:
    changed = []
    for path, rows in lineage_from_manifests(manifests).items():
        signatures = {artifact_signature(row) for row in rows}
        if len(signatures) > 1:
            changed.append(path)
    return sorted(changed)


def lineage_summary(manifests: Iterable[Mapping[str, object]]) -> dict[str, object]:
    lineage = lineage_from_manifests(manifests)
    changed = changed_paths(manifests)
    return {
        "path_count": len(lineage),
        "changed_paths": changed,
        "stable_paths": sorted(path for path in lineage if path not in set(changed)),
        "lineage": lineage,
    }
