from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class AssessmentCase:
    case_id: str
    section: str
    comparator: str
    difficulty: str
    hidden: bool
    weight: float
    time_limit_ms: int
    input_payload: Mapping[str, Any]
    expected: Any
    tags: tuple[str, ...] = ()

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "AssessmentCase":
        return cls(
            case_id=str(row["case_id"]),
            section=str(row["section"]),
            comparator=str(row["comparator"]),
            difficulty=str(row["difficulty"]),
            hidden=bool(row["hidden"]),
            weight=float(row["weight"]),
            time_limit_ms=int(row["time_limit_ms"]),
            input_payload=dict(row.get("input_payload", {})),
            expected=row.get("expected"),
            tags=tuple(str(tag) for tag in row.get("tags", [])),
        )

    def visibility(self) -> str:
        return "hidden" if self.hidden else "public"


@dataclass(frozen=True)
class ExerciseBundle:
    bundle_id: str
    version: str
    domain: str
    owner: str
    title: str
    tags: tuple[str, ...]
    rubric: Mapping[str, Any]
    metadata: Mapping[str, Any]
    cases: tuple[AssessmentCase, ...]
    root: Path | None = None

    def public_cases(self) -> tuple[AssessmentCase, ...]:
        return tuple(case for case in self.cases if not case.hidden)

    def hidden_cases(self) -> tuple[AssessmentCase, ...]:
        return tuple(case for case in self.cases if case.hidden)

    def sections(self) -> tuple[str, ...]:
        return tuple(sorted({case.section for case in self.cases}))


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    status: str
    runtime_ms: int
    points: float
    max_points: float
    hidden: bool
    section: str
    message: str


@dataclass(frozen=True)
class SubmissionRun:
    run_id: str
    bundle_id: str
    participant_id: str
    profile: str
    started_at: str
    finished_at: str
    case_results: tuple[CaseResult, ...]
    notes: tuple[str, ...] = ()

    def totals(self) -> dict[str, float]:
        earned = sum(item.points for item in self.case_results)
        possible = sum(item.max_points for item in self.case_results)
        passed = sum(1 for item in self.case_results if item.status == "pass")
        return {"earned": earned, "possible": possible, "passed_cases": float(passed)}


@dataclass(frozen=True)
class Scorecard:
    run_id: str
    bundle_id: str
    percent: float
    band: str
    public_percent: float
    hidden_percent: float
    section_totals: Mapping[str, Mapping[str, float]]
    policy_flags: tuple[str, ...]
    owner: str


@dataclass(frozen=True)
class ReleaseManifest:
    release_id: str
    created_at: str
    bundle_ids: tuple[str, ...]
    bundle_stats: Mapping[str, Any]
    digest: str
    notes: tuple[str, ...] = ()
