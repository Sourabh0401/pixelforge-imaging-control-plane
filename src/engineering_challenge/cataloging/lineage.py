from __future__ import annotations

from collections import defaultdict

from engineering_challenge.models import ExerciseBundle


def lineage_rows(bundles: list[ExerciseBundle]) -> list[dict[str, object]]:
    rows = []
    for bundle in bundles:
        rows.append(
            {
                "bundle_id": bundle.bundle_id,
                "owner": bundle.owner,
                "version": bundle.version,
                "release_channel": bundle.metadata.get("release_channel", "unknown"),
                "case_count": len(bundle.cases),
            }
        )
    return sorted(rows, key=lambda row: (row["owner"], row["bundle_id"]))


def owner_lineage(bundles: list[ExerciseBundle]) -> dict[str, list[str]]:
    owners: dict[str, list[str]] = defaultdict(list)
    for bundle in bundles:
        owners[bundle.owner].append(bundle.bundle_id)
    return {owner: sorted(bundle_ids) for owner, bundle_ids in sorted(owners.items())}


def version_train(bundles: list[ExerciseBundle]) -> dict[str, list[str]]:
    trains: dict[str, list[str]] = defaultdict(list)
    for bundle in bundles:
        trains[bundle.version].append(bundle.bundle_id)
    return {version: sorted(bundle_ids) for version, bundle_ids in sorted(trains.items())}


def supersedes_map(bundles: list[ExerciseBundle]) -> dict[str, str]:
    ordered = sorted(bundles, key=lambda bundle: (bundle.owner, bundle.bundle_id))
    mapping: dict[str, str] = {}
    previous: dict[str, str] = {}
    for bundle in ordered:
        if bundle.owner in previous:
            mapping[bundle.bundle_id] = previous[bundle.owner]
        previous[bundle.owner] = bundle.bundle_id
    return mapping
