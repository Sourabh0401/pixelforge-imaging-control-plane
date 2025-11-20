from __future__ import annotations

from dataclasses import asdict
from typing import Any, Mapping

from .config import RuntimeProfile
from .catalog import case_index
from .execution_engine.comparator import compare
from .models import AssessmentCase, CaseResult, ExerciseBundle, SubmissionRun
from .policy import difficulty_weight
from .utils import utcnow_text


def _compare(case: AssessmentCase, answer: Any) -> bool:
    try:
        return bool(compare(case.comparator, answer, case.expected))
    except KeyError as exc:
        raise ValueError(f"Unsupported comparator: {case.comparator}") from exc


def _max_points(case: AssessmentCase, profile: RuntimeProfile) -> float:
    multiplier = profile.hidden_case_multiplier if case.hidden else profile.public_case_multiplier
    return round(case.weight * difficulty_weight(case.difficulty) * multiplier, 4)


def evaluate_attempt(
    bundle: ExerciseBundle,
    attempt_payload: Mapping[str, Any],
    profile: RuntimeProfile | None = None,
) -> SubmissionRun:
    profile = profile or RuntimeProfile()
    answers = {str(item["case_id"]): item for item in attempt_payload.get("case_results", [])}
    results: list[CaseResult] = []
    for case in bundle.cases:
        attempt_case = answers.get(case.case_id)
        max_points = _max_points(case, profile)
        if attempt_case is None:
            results.append(CaseResult(case.case_id, "missing", 0, 0.0, max_points, case.hidden, case.section, "case missing"))
            continue
        runtime_ms = int(attempt_case.get("runtime_ms", 0))
        if runtime_ms > int(case.time_limit_ms * profile.timeout_multiplier):
            results.append(CaseResult(case.case_id, "timeout", runtime_ms, 0.0, max_points, case.hidden, case.section, "runtime exceeded"))
            continue
        if attempt_case.get("error"):
            results.append(CaseResult(case.case_id, "error", runtime_ms, 0.0, max_points, case.hidden, case.section, str(attempt_case["error"])))
            continue
        passed = _compare(case, attempt_case.get("answer"))
        late_penalty = profile.late_result_penalty if runtime_ms > case.time_limit_ms * 0.85 else 0.0
        points = max_points * (1.0 - late_penalty) if passed else 0.0
        status = "pass" if passed else "fail"
        message = "matched expected output" if passed else "output mismatch"
        results.append(CaseResult(case.case_id, status, runtime_ms, round(points, 4), max_points, case.hidden, case.section, message))
    return SubmissionRun(
        run_id=str(attempt_payload.get("run_id", "run-local")),
        bundle_id=bundle.bundle_id,
        participant_id=str(attempt_payload.get("participant_id", "unknown")),
        profile=profile.name,
        started_at=str(attempt_payload.get("started_at", utcnow_text())),
        finished_at=str(attempt_payload.get("finished_at", utcnow_text())),
        case_results=tuple(results),
        notes=tuple(str(note) for note in attempt_payload.get("notes", [])),
    )


def run_to_dict(run: SubmissionRun) -> dict[str, Any]:
    return {
        "run_id": run.run_id,
        "bundle_id": run.bundle_id,
        "participant_id": run.participant_id,
        "profile": run.profile,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
        "notes": list(run.notes),
        "case_results": [asdict(item) for item in run.case_results],
        "totals": run.totals(),
    }


def case_result_lookup(run: SubmissionRun) -> dict[str, CaseResult]:
    return {result.case_id: result for result in run.case_results}
