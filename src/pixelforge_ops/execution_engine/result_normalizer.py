from __future__ import annotations

from typing import Any


def normalize_answer(answer: Any) -> Any:
    if isinstance(answer, str):
        return answer.strip()
    if isinstance(answer, list):
        return [normalize_answer(item) for item in answer]
    if isinstance(answer, dict):
        return {str(key): normalize_answer(value) for key, value in sorted(answer.items())}
    return answer


def normalize_status(raw_status: str, *, has_error: bool, timed_out: bool) -> str:
    if timed_out:
        return "timeout"
    if has_error:
        return "error"
    return raw_status


def normalize_message(status: str, answer: Any) -> str:
    if status == "pass":
        return "matched expected output"
    if status == "timeout":
        return "runtime exceeded case budget"
    if status == "error":
        return str(answer or "execution error")
    if status == "missing":
        return "case missing from payload"
    return "output mismatch"


def partition_results(results: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    output = {"hidden": [], "public": []}
    for row in results:
        output["hidden" if row.get("hidden") else "public"].append(row)
    return output


def status_counts(results: list[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in results:
        status = str(row["status"])
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))
