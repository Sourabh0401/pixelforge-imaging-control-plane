from __future__ import annotations

from pixelforge_ops.models import SubmissionRun


def run_transcript(run: SubmissionRun) -> list[dict[str, object]]:
    rows = []
    for index, result in enumerate(run.case_results, start=1):
        rows.append(
            {
                "sequence": index,
                "run_id": run.run_id,
                "case_id": result.case_id,
                "status": result.status,
                "runtime_ms": result.runtime_ms,
                "hidden": result.hidden,
                "section": result.section,
                "message": result.message,
            }
        )
    return rows


def status_timeline(run: SubmissionRun) -> list[str]:
    return [f"{result.case_id}:{result.status}" for result in run.case_results]


def slowest_cases(run: SubmissionRun, limit: int = 5) -> list[dict[str, object]]:
    ordered = sorted(run.case_results, key=lambda item: item.runtime_ms, reverse=True)
    return [
        {
            "case_id": item.case_id,
            "runtime_ms": item.runtime_ms,
            "status": item.status,
        }
        for item in ordered[:limit]
    ]


def transcript_markdown(run: SubmissionRun) -> str:
    lines = [f"# Run transcript: {run.run_id}", "", "| Case | Status | Runtime ms | Section |", "| --- | --- | ---: | --- |"]
    for result in run.case_results:
        lines.append(f"| {result.case_id} | {result.status} | {result.runtime_ms} | {result.section} |")
    return "\n".join(lines) + "\n"


