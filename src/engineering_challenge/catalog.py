from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from .models import AssessmentCase, ExerciseBundle
from .utils import read_json, read_jsonl, slugify


def load_bundle(path: Path) -> ExerciseBundle:
    manifest = read_json(path / "bundle.json")
    cases = tuple(AssessmentCase.from_row(row) for row in read_jsonl(path / "cases.jsonl"))
    return ExerciseBundle(
        bundle_id=str(manifest["bundle_id"]),
        version=str(manifest["version"]),
        domain=str(manifest["domain"]),
        owner=str(manifest["owner"]),
        title=str(manifest["title"]),
        tags=tuple(str(tag) for tag in manifest.get("tags", [])),
        rubric=dict(manifest.get("rubric", {})),
        metadata=dict(manifest.get("metadata", {})),
        cases=cases,
        root=path,
    )


def discover_bundles(root: Path) -> tuple[Path, ...]:
    return tuple(sorted(path for path in root.iterdir() if path.is_dir() and (path / "bundle.json").exists()))


def load_corpus(root: Path) -> tuple[ExerciseBundle, ...]:
    return tuple(load_bundle(path) for path in discover_bundles(root))


def bundle_summary(bundle: ExerciseBundle) -> dict[str, object]:
    section_counts = Counter(case.section for case in bundle.cases)
    comparator_counts = Counter(case.comparator for case in bundle.cases)
    return {
        "bundle_id": bundle.bundle_id,
        "domain": bundle.domain,
        "owner": bundle.owner,
        "version": bundle.version,
        "case_count": len(bundle.cases),
        "public_case_count": len(bundle.public_cases()),
        "hidden_case_count": len(bundle.hidden_cases()),
        "sections": dict(sorted(section_counts.items())),
        "comparators": dict(sorted(comparator_counts.items())),
        "tags": list(bundle.tags),
    }


def corpus_summary(root: Path) -> dict[str, object]:
    bundles = load_corpus(root)
    by_owner = Counter(bundle.owner for bundle in bundles)
    by_domain = Counter(bundle.domain for bundle in bundles)
    cases = sum(len(bundle.cases) for bundle in bundles)
    return {
        "bundle_count": len(bundles),
        "case_count": cases,
        "owners": dict(sorted(by_owner.items())),
        "domains": dict(sorted(by_domain.items())),
        "bundle_ids": [bundle.bundle_id for bundle in bundles],
    }


def case_index(bundle: ExerciseBundle) -> dict[str, AssessmentCase]:
    return {case.case_id: case for case in bundle.cases}


def duplicate_case_ids(bundle: ExerciseBundle) -> tuple[str, ...]:
    counts = Counter(case.case_id for case in bundle.cases)
    return tuple(sorted(case_id for case_id, count in counts.items() if count > 1))


def section_matrix(bundles: Iterable[ExerciseBundle]) -> dict[str, dict[str, int]]:
    matrix: dict[str, dict[str, int]] = defaultdict(dict)
    for bundle in bundles:
        counts = Counter(case.section for case in bundle.cases)
        for section, count in counts.items():
            matrix[section][bundle.bundle_id] = count
    return {section: dict(sorted(values.items())) for section, values in sorted(matrix.items())}


def normalized_owner_token(bundle: ExerciseBundle) -> str:
    return slugify(bundle.owner)
