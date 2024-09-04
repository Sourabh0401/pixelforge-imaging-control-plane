from __future__ import annotations

from engineering_challenge.auditpack.contracts import required_artifact_paths


def evidence_map(bundle_id: str, run_id: str) -> dict[str, str]:
    return {
        path: f"{bundle_id}/{run_id}/{path}"
        for path in required_artifact_paths()
    }


def missing_paths(present: list[str]) -> list[str]:
    required = set(required_artifact_paths())
    return sorted(required - set(present))


def unexpected_paths(present: list[str]) -> list[str]:
    required = set(required_artifact_paths())
    return sorted(set(present) - required)
