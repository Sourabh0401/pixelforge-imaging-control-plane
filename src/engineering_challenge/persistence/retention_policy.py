from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable


@dataclass(frozen=True)
class RetentionRule:
    channel: str
    artifact_class: str
    keep_days: int
    archive_after_days: int
    prune_after_days: int
    requires_export: bool
    owner_review_days: int


@dataclass(frozen=True)
class RetentionAction:
    history_id: str
    bundle_id: str
    owner: str
    action: str
    reason: str
    age_days: int


RULES = (
    RetentionRule("internal", "run-history", 21, 30, 45, True, 7),
    RetentionRule("internal", "audit-packet", 90, 180, 365, False, 30),
    RetentionRule("rehearsal", "run-history", 14, 21, 30, True, 5),
    RetentionRule("rehearsal", "audit-packet", 60, 120, 180, False, 21),
    RetentionRule("pilot", "run-history", 45, 75, 90, True, 14),
    RetentionRule("pilot", "audit-packet", 180, 240, 365, False, 45),
    RetentionRule("partner", "run-history", 60, 120, 180, True, 21),
    RetentionRule("partner", "audit-packet", 365, 540, 720, False, 60),
    RetentionRule("ops-only", "run-history", 10, 14, 21, True, 3),
    RetentionRule("ops-only", "audit-packet", 45, 60, 90, False, 14),
)


def rules() -> tuple[RetentionRule, ...]:
    return RULES


def rule_for(channel: str, artifact_class: str) -> RetentionRule:
    for rule in RULES:
        if rule.channel == channel and rule.artifact_class == artifact_class:
            return rule
    raise KeyError((channel, artifact_class))


def parse_started_at(text: str) -> date:
    return datetime.fromisoformat(text.replace("Z", "+00:00")).date()


def age_days(row: dict[str, object], today: date) -> int:
    return (today - parse_started_at(str(row["started_at"]))).days


def artifact_class(row: dict[str, object]) -> str:
    return "audit-packet" if row.get("artifact_digest") and row.get("review_state") == "audit" else "run-history"


def requires_export(row: dict[str, object]) -> bool:
    return artifact_class(row) == "run-history"


def eligible_for_archive(row: dict[str, object], today: date) -> bool:
    rule = rule_for(str(row["release_channel"]), artifact_class(row))
    return age_days(row, today) >= rule.archive_after_days


def eligible_for_prune(row: dict[str, object], today: date, has_export: bool) -> bool:
    rule = rule_for(str(row["release_channel"]), artifact_class(row))
    if rule.requires_export and not has_export:
        return False
    return age_days(row, today) >= rule.prune_after_days


def owner_review_due(row: dict[str, object], today: date) -> bool:
    rule = rule_for(str(row["release_channel"]), artifact_class(row))
    return age_days(row, today) >= rule.owner_review_days


def risk_label(row: dict[str, object], today: date, has_export: bool) -> str:
    if eligible_for_prune(row, today, has_export):
        return "prunable"
    if eligible_for_archive(row, today):
        return "archive-soon"
    if owner_review_due(row, today):
        return "review-window"
    return "active"


def plan_action(row: dict[str, object], today: date, has_export: bool) -> RetentionAction:
    label = risk_label(row, today, has_export)
    reason_map = {
        "prunable": "channel retention window expired",
        "archive-soon": "row should be archived before prune",
        "review-window": "owner review window reached",
        "active": "row is still within active retention window",
    }
    action_map = {
        "prunable": "prune",
        "archive-soon": "archive",
        "review-window": "review",
        "active": "keep",
    }
    return RetentionAction(
        history_id=str(row["history_id"]),
        bundle_id=str(row["bundle_id"]),
        owner=str(row["owner"]),
        action=action_map[label],
        reason=reason_map[label],
        age_days=age_days(row, today),
    )


def plan_actions(rows: Iterable[dict[str, object]], today: date, exported_history_ids: set[str] | None = None) -> list[RetentionAction]:
    exported_history_ids = exported_history_ids or set()
    actions = []
    for row in rows:
        has_export = str(row["history_id"]) in exported_history_ids or not requires_export(row)
        actions.append(plan_action(row, today, has_export))
    actions.sort(key=lambda item: (item.action, item.owner, item.history_id))
    return actions


def action_summary(actions: Iterable[RetentionAction]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for action in actions:
        counts[action.action] = counts.get(action.action, 0) + 1
    return dict(sorted(counts.items()))


def owner_summary(actions: Iterable[RetentionAction]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for action in actions:
        owner = summary.setdefault(action.owner, {})
        owner[action.action] = owner.get(action.action, 0) + 1
    return {owner: dict(sorted(counts.items())) for owner, counts in sorted(summary.items())}


def oldest_eligible(rows: Iterable[dict[str, object]], today: date, exported_history_ids: set[str] | None = None) -> dict[str, int]:
    actions = plan_actions(rows, today, exported_history_ids)
    result: dict[str, int] = {}
    for action in actions:
        if action.action in {"archive", "prune"}:
            result.setdefault(action.action, action.age_days)
            result[action.action] = max(result[action.action], action.age_days)
    return result


def channel_matrix() -> dict[str, dict[str, dict[str, int | bool]]]:
    matrix: dict[str, dict[str, dict[str, int | bool]]] = {}
    for rule in RULES:
        channel = matrix.setdefault(rule.channel, {})
        channel[rule.artifact_class] = {
            "keep_days": rule.keep_days,
            "archive_after_days": rule.archive_after_days,
            "prune_after_days": rule.prune_after_days,
            "requires_export": rule.requires_export,
            "owner_review_days": rule.owner_review_days,
        }
    return matrix


def render_summary(actions: list[RetentionAction]) -> str:
    lines = ["# Retention summary", ""]
    for action, count in action_summary(actions).items():
        lines.append(f"- {action}: {count}")
    lines.extend(["", "## Owners"])
    for owner, counts in owner_summary(actions).items():
        detail = ", ".join(f"{action}={count}" for action, count in counts.items())
        lines.append(f"- {owner}: {detail}")
    return "\n".join(lines) + "\n"
