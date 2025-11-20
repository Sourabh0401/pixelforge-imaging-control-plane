from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeBudget:
    case_id: str
    base_ms: int
    ceiling_ms: int
    late_threshold_ms: int
    queue_bucket: str


def budget_for(case_id: str, base_ms: int, hidden: bool, comparator: str) -> RuntimeBudget:
    multiplier = 1.35 if hidden else 1.0
    if comparator in {"artifact_manifest", "csv_rows", "regex_groups"}:
        multiplier += 0.2
    ceiling = int(base_ms * multiplier)
    return RuntimeBudget(
        case_id=case_id,
        base_ms=base_ms,
        ceiling_ms=ceiling,
        late_threshold_ms=int(ceiling * 0.85),
        queue_bucket="long" if ceiling >= 1500 else "short",
    )


def classify_runtime(runtime_ms: int, budget: RuntimeBudget) -> str:
    if runtime_ms > budget.ceiling_ms:
        return "timeout"
    if runtime_ms > budget.late_threshold_ms:
        return "late"
    return "on-time"


def queue_weight(budget: RuntimeBudget) -> int:
    return 3 if budget.queue_bucket == "long" else 1


def aggregate_runtime(items: list[RuntimeBudget]) -> dict[str, int]:
    return {
        "case_count": len(items),
        "ceiling_total_ms": sum(item.ceiling_ms for item in items),
        "late_total_ms": sum(item.late_threshold_ms for item in items),
    }
