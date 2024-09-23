from __future__ import annotations

from engineering_challenge.models import SubmissionRun


def trace_rows(run: SubmissionRun) -> list[dict[str, object]]:
    return [
        {
            "run_id": run.run_id,
            "case_id": item.case_id,
            "status": item.status,
            "runtime_ms": item.runtime_ms,
            "points": item.points,
            "max_points": item.max_points,
        }
        for item in run.case_results
    ]


def trace_digest_payload(run: SubmissionRun) -> dict[str, object]:
    return {
        "run_id": run.run_id,
        "bundle_id": run.bundle_id,
        "cases": [item.case_id for item in run.case_results],
    }
