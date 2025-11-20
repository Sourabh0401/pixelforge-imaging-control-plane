from __future__ import annotations

from pathlib import Path
from typing import Mapping

from . import catalog, validator
from .execution import evaluate_attempt
from .release import build_release_manifest
from .scoring import score_run


def batch_validate(root: Path) -> dict[str, object]:
    bundles = catalog.load_corpus(root)
    result = {}
    for bundle in bundles:
        issues = validator.validate_bundle(bundle)
        result[bundle.bundle_id] = {
            "error_count": sum(1 for issue in issues if issue.severity == "error"),
            "warning_count": sum(1 for issue in issues if issue.severity == "warning"),
        }
    return result


def batch_score(bundle_paths: Mapping[Path, Mapping[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for path, payload in bundle_paths.items():
        bundle = catalog.load_bundle(path)
        run = evaluate_attempt(bundle, payload)
        scorecard = score_run(run, bundle)
        output.append({"bundle_id": bundle.bundle_id, "scorecard": scorecard})
    return output


def build_release(root: Path, bundle_paths: list[Path], release_id: str) -> dict[str, object]:
    bundles = [catalog.load_bundle(path) for path in bundle_paths]
    manifest = build_release_manifest(release_id, bundles)
    return {"manifest": manifest, "validation": [issue.__dict__ for issue in validator.validate_release_inputs(bundles)]}
