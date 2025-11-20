from __future__ import annotations

from pixelforge_ops import catalog
from pixelforge_ops.cataloging.policy_catalog import bundle_envelope


def bundle_manifest_row(bundle) -> dict[str, object]:
    summary = catalog.bundle_summary(bundle)
    summary["policy"] = bundle_envelope(bundle.domain)
    return summary


def manifest_rows(bundles) -> list[dict[str, object]]:
    return [bundle_manifest_row(bundle) for bundle in sorted(bundles, key=lambda item: item.bundle_id)]


def owner_mix(bundles) -> dict[str, int]:
    counts: dict[str, int] = {}
    for bundle in bundles:
        counts[bundle.owner] = counts.get(bundle.owner, 0) + 1
    return dict(sorted(counts.items()))


