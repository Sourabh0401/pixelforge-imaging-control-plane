from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from engineering_challenge.release_ops import owner_capacity
from engineering_challenge.release_ops.rollout_matrix import owner_quota


@dataclass(frozen=True)
class GateDecision:
    owner: str
    channel: str
    requested: int
    remaining: int
    allowed: bool
    reason: str
    week_start: str = ""


def remaining_quota(owner: str, channel: str, already_scheduled: int) -> int:
    return max(owner_quota(owner, channel) - already_scheduled, 0)


def can_schedule(owner: str, channel: str, already_scheduled: int) -> bool:
    return remaining_quota(owner, channel, already_scheduled) > 0


def blackout_weeks(owner: str) -> list[str]:
    weeks: list[str] = []
    for row in owner_capacity.week_rows():
        if owner in row["blackout"]:
            weeks.append(str(row["week_start"]))
    return weeks


def has_blackout(owner: str, week_start: str) -> bool:
    return owner in owner_capacity.blackout_owners(week_start)


def capacity_for_week(owner: str, week_start: str) -> int:
    return owner_capacity.capacity_for_week(owner, week_start)


def evaluate_request(owner: str, channel: str, already_scheduled: int, requested: int, week_start: str) -> GateDecision:
    remaining = remaining_quota(owner, channel, already_scheduled)
    if has_blackout(owner, week_start):
        return GateDecision(owner, channel, requested, remaining, False, "owner blackout for week", week_start)
    if requested > remaining:
        return GateDecision(owner, channel, requested, remaining, False, "owner quota exhausted", week_start)
    if requested > capacity_for_week(owner, week_start):
        return GateDecision(owner, channel, requested, remaining, False, "owner weekly capacity exceeded", week_start)
    return GateDecision(owner, channel, requested, remaining - requested, True, "owner may schedule release", week_start)


def owner_gate_summary(owners: list[str], channel: str, current: dict[str, int]) -> dict[str, dict[str, int | bool | str]]:
    week_start = str(owner_capacity.week_rows()[0]["week_start"])
    return {
        owner: {
            "remaining": remaining_quota(owner, channel, current.get(owner, 0)),
            "blackout": has_blackout(owner, week_start),
            "capacity": capacity_for_week(owner, week_start),
        }
        for owner in owners
    }


def blocked_reasons(owners: list[str], channel: str, current: dict[str, int], requested: int, week_start: str) -> dict[str, str]:
    reasons: dict[str, str] = {}
    for owner in owners:
        decision = evaluate_request(owner, channel, current.get(owner, 0), requested, week_start)
        if not decision.allowed:
            reasons[owner] = decision.reason
    return reasons


def schedule_batch(requests: list[tuple[str, int]], channel: str, current: dict[str, int], week_start: str) -> dict[str, GateDecision]:
    decisions: dict[str, GateDecision] = {}
    running = dict(current)
    for owner, requested in requests:
        decision = evaluate_request(owner, channel, running.get(owner, 0), requested, week_start)
        decisions[owner] = decision
        if decision.allowed:
            running[owner] = running.get(owner, 0) + requested
    return decisions


def scheduleable_owners(
    owners: list[str], channel: str, current: dict[str, int], requested: int, week_start: str
) -> list[str]:
    ready: list[str] = []
    for owner in owners:
        decision = evaluate_request(owner, channel, current.get(owner, 0), requested, week_start)
        if decision.allowed:
            ready.append(owner)
    return sorted(ready)


def batch_summary(decisions: dict[str, GateDecision]) -> dict[str, object]:
    allowed = {owner: decision for owner, decision in decisions.items() if decision.allowed}
    blocked = {owner: decision.reason for owner, decision in decisions.items() if not decision.allowed}
    return {
        "requested_owners": sorted(decisions),
        "allowed_owners": sorted(allowed),
        "blocked_owners": sorted(blocked),
        "blocked_reasons": dict(sorted(blocked.items())),
        "granted_slots": sum(decision.requested for decision in allowed.values()),
    }


def release_window_status(owners: list[str], channel: str, current: dict[str, int], week_start: str) -> dict[str, object]:
    summary = owner_gate_summary(owners, channel, current)
    blocked = blocked_reasons(owners, channel, current, 1, week_start)
    ready = scheduleable_owners(owners, channel, current, 1, week_start)
    return {
        "channel": channel,
        "week_start": week_start,
        "ready_owners": ready,
        "blocked_reasons": blocked,
        "summary": summary,
    }


def render_gate_notes(decision: GateDecision) -> str:
    if decision.allowed:
        return f"{decision.owner} can schedule {decision.requested} item(s) on {decision.channel}; {decision.remaining} slots remain after allocation."
    return f"{decision.owner} cannot schedule {decision.requested} item(s) on {decision.channel}: {decision.reason}."
