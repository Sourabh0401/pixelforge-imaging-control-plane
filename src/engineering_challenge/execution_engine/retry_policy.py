from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from engineering_challenge.models import CaseResult, SubmissionRun


@dataclass(frozen=True)
class RetryDecision:
    case_id: str
    action: str
    reason: str
    delay_seconds: int
    owner: str
    section: str
    budget_cost: int


RETRY_BACKOFF = {
    "timeout": (60, 180, 420),
    "error": (45, 120, 300),
    "fail": (0, 0, 0),
    "missing": (0, 0, 0),
}

SECTION_ESCALATION_OWNER = {
    "validation": "support_ops",
    "catalog": "content_ops",
    "execution": "platform_ops",
    "scoring": "finance_ops",
    "audit": "risk_ops",
}


def classify_case_result(result: CaseResult) -> str:
    if result.status == "timeout":
        return "retryable-timeout"
    if result.status == "error":
        return "retryable-error"
    if result.status == "missing":
        return "authoring-gap"
    if result.status == "fail":
        return "content-mismatch"
    return "stable"


def retry_budget(profile: str) -> int:
    budgets = {
        "default": 8,
        "aggressive": 12,
        "conservative": 5,
    }
    return budgets.get(profile, 8)


def owner_for_section(section: str) -> str:
    return SECTION_ESCALATION_OWNER.get(section, "support_ops")


def retry_schedule(status: str, attempt_number: int) -> int:
    schedule = RETRY_BACKOFF.get(status, (0, 0, 0))
    index = max(min(attempt_number - 1, len(schedule) - 1), 0)
    return int(schedule[index])


def decision_for_result(result: CaseResult, attempt_number: int = 1) -> RetryDecision:
    category = classify_case_result(result)
    if category == "retryable-timeout":
        return RetryDecision(result.case_id, "retry", "runtime exceeded", retry_schedule(result.status, attempt_number), owner_for_section(result.section), result.section, 2)
    if category == "retryable-error":
        return RetryDecision(result.case_id, "retry", "runtime error", retry_schedule(result.status, attempt_number), owner_for_section(result.section), result.section, 3)
    if category == "authoring-gap":
        return RetryDecision(result.case_id, "triage", "case result missing", 0, owner_for_section("catalog"), result.section, 1)
    if category == "content-mismatch":
        return RetryDecision(result.case_id, "review", "answer mismatch", 0, owner_for_section(result.section), result.section, 1)
    return RetryDecision(result.case_id, "none", "case already stable", 0, owner_for_section(result.section), result.section, 0)


def run_retry_plan(run: SubmissionRun, attempt_number: int = 1) -> list[RetryDecision]:
    decisions = [decision_for_result(result, attempt_number) for result in run.case_results if result.status != "pass"]
    decisions.sort(key=lambda item: (item.action, item.section, item.case_id))
    return decisions


def total_budget_cost(decisions: list[RetryDecision]) -> int:
    return sum(item.budget_cost for item in decisions)


def exceeded_budget(run: SubmissionRun, attempt_number: int = 1) -> bool:
    return total_budget_cost(run_retry_plan(run, attempt_number)) > retry_budget(run.profile)


def blocked_sections(run: SubmissionRun) -> list[str]:
    sections = {result.section for result in run.case_results if result.status in {"timeout", "error", "missing"}}
    return sorted(sections)


def owner_queue(decisions: list[RetryDecision]) -> dict[str, list[str]]:
    queue: dict[str, list[str]] = {}
    for item in decisions:
        if item.action == "none":
            continue
        queue.setdefault(item.owner, []).append(item.case_id)
    return {owner: sorted(case_ids) for owner, case_ids in sorted(queue.items())}


def delay_buckets(decisions: list[RetryDecision]) -> dict[str, int]:
    buckets = {"instant": 0, "short": 0, "medium": 0, "long": 0}
    for item in decisions:
        if item.delay_seconds == 0:
            buckets["instant"] += 1
        elif item.delay_seconds <= 60:
            buckets["short"] += 1
        elif item.delay_seconds <= 180:
            buckets["medium"] += 1
        else:
            buckets["long"] += 1
    return buckets


def should_pause_bundle(run: SubmissionRun, attempt_number: int = 1) -> bool:
    decisions = run_retry_plan(run, attempt_number)
    retry_count = sum(1 for item in decisions if item.action == "retry")
    hard_count = sum(1 for item in decisions if item.action == "triage")
    return retry_count >= 4 or hard_count >= 2 or exceeded_budget(run, attempt_number)


def reason_summary(decisions: list[RetryDecision]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in decisions:
        counts[item.reason] = counts.get(item.reason, 0) + 1
    return dict(sorted(counts.items()))


def schedule_summary(run: SubmissionRun, attempt_number: int = 1) -> dict[str, object]:
    decisions = run_retry_plan(run, attempt_number)
    retryable = [item for item in decisions if item.action == "retry"]
    return {
        "run_id": run.run_id,
        "retryable_count": len(retryable),
        "owner_queue": owner_queue(decisions),
        "delay_buckets": delay_buckets(decisions),
        "blocked_sections": blocked_sections(run),
        "pause_bundle": should_pause_bundle(run, attempt_number),
        "reasons": reason_summary(decisions),
    }


def next_retry_window(run: SubmissionRun, attempt_number: int = 1) -> tuple[int, int]:
    retryable = [item.delay_seconds for item in run_retry_plan(run, attempt_number) if item.action == "retry"]
    if not retryable:
        return (0, 0)
    return (min(retryable), max(retryable))


def retry_horizon(run: SubmissionRun, attempt_number: int = 1) -> str:
    minimum, maximum = next_retry_window(run, attempt_number)
    return f"{timedelta(seconds=minimum)} to {timedelta(seconds=maximum)}"
