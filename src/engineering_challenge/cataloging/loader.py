from __future__ import annotations

from pathlib import Path

from engineering_challenge import catalog
from engineering_challenge.cataloging.policy_catalog import canonical_tags, section_weight


def load_bundle_with_policy(path: Path) -> dict[str, object]:
    bundle = catalog.load_bundle(path)
    return {
        "bundle": bundle,
        "summary": catalog.bundle_summary(bundle),
        "canonical_tags": canonical_tags(list(bundle.tags)),
        "section_weights": {section: section_weight(bundle.domain, section) for section in bundle.sections()},
    }


def load_corpus_with_policy(root: Path) -> list[dict[str, object]]:
    return [load_bundle_with_policy(path) for path in catalog.discover_bundles(root)]


def bundles_for_owner(root: Path, owner: str) -> list[str]:
    return [
        bundle.bundle_id
        for bundle in catalog.load_corpus(root)
        if bundle.owner == owner
    ]


def case_budget(root: Path) -> dict[str, int]:
    return {
        bundle.bundle_id: len(bundle.cases)
        for bundle in catalog.load_corpus(root)
    }


def comparator_mix(root: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for bundle in catalog.load_corpus(root):
        for case in bundle.cases:
            counts[case.comparator] = counts.get(case.comparator, 0) + 1
    return dict(sorted(counts.items()))
