from __future__ import annotations

"""
Evidence status helpers sit between the low-level validator and the people
actually triaging a release. The validator is intentionally strict and speaks
in issue codes, severities, and paths. That is good for tests and for packet
replay, but it is not always the fastest way for an owner to understand what
they should do next.

This module groups issues into operational states, maps them to likely owners,
and produces short summaries that can be dropped into a release brief, a
support note, or a retention review. The goal is not to replace the validator.
The goal is to give the next human a stable explanation layer on top of it.
That layer is meant for release week, not just for tests.
"""

from pixelforge_ops.auditpack.evidence_validator import ValidationIssue


STATUS_DESCRIPTIONS = {
    "green": "Packet is structurally complete, contract fields are present, and no blocking repair work is outstanding.",
    "yellow": "Packet is usable but one or more warnings should be reviewed before the release is called stable.",
    "red": "Packet is missing required information or fails a structural contract and should not be treated as export-safe.",
}

SEVERITY_GUIDANCE = {
    "error": "Blocking issue. Do not treat the packet as a valid export and do not let retention logic assume it is safe to prune related rows.",
    "warn": "Non-blocking issue. The packet may still be usable, but the discrepancy should be explained before the next release decision or cleanup pass.",
    "info": "Observed condition that is worth recording for future triage, even when the packet remains healthy enough to ship.",
}

OWNER_ROUTE = {
    "bundle": "metadata_ops",
    "run": "pipeline_ops",
    "scorecard": "codec_ops",
    "release_manifest": "release_ops",
    "trace_rows": "pipeline_ops",
    "artifact_paths": "image_quality_ops",
    "packet_digest": "audit_ops",
    "retention_link": "archive_ops",
    "history_import": "reporting_ops",
    "owner_dashboard": "partner_ops",
    "retention_summary": "archive_ops",
    "query_snapshot": "pipeline_ops",
}

REMEDIATION_MATRIX = {
    "metadata_ops": {
        "primary_action": "Review bundle metadata, title-note alignment, and any wording changes that affect hidden cases.",
        "secondary_action": "Confirm that release notes and authoring notes describe the same workflow change before asking for a rescore.",
        "escalate_when": "The packet is structurally valid but the explanation layer is still inconsistent across bundle, note, and dashboard surfaces.",
    },
    "pipeline_ops": {
        "primary_action": "Inspect runtime, transcript, trace rows, and snapshot compatibility before changing thresholds or metadata.",
        "secondary_action": "Confirm that retries, queue latency, and worker-version movement explain the observed issue shape.",
        "escalate_when": "The same packet or query failure shows up across more than one owner or bundle family.",
    },
    "codec_ops": {
        "primary_action": "Compare scorecard payload, policy flags, and release readiness notes before approving another train.",
        "secondary_action": "Check whether public-hidden movement reflects a true quality change or a narrow hidden-case regression.",
        "escalate_when": "Threshold interpretation or close timing is the main blocker rather than packet integrity itself.",
    },
    "release_ops": {
        "primary_action": "Confirm manifest lineage, release id, train timing, and owner capacity context are all in sync.",
        "secondary_action": "Rebuild manifests and packets together if any release-note or bundle-membership field changed.",
        "escalate_when": "The packet is healthy but the release should still not proceed because of scheduling or capacity policy.",
    },
    "image_quality_ops": {
        "primary_action": "Inspect path maps, evidence coverage, and partner-control wording before allowing a release to proceed.",
        "secondary_action": "Use the packet and field dictionary together to decide whether a control gap is real or just a documentation gap.",
        "escalate_when": "Evidence structure is intact but the partner-facing control language still changed in a risky way.",
    },
    "audit_ops": {
        "primary_action": "Recompute packet and manifest digests only after every logical payload source is stable.",
        "secondary_action": "Treat digest drift as a real lineage problem until all nested payload changes are understood.",
        "escalate_when": "Repeated exports from identical inputs still produce inconsistent packet state.",
    },
    "archive_ops": {
        "primary_action": "Pause prune or archive actions until packet validity and release lineage are both confirmed.",
        "secondary_action": "Review channel retention rules alongside close-window expectations before cleanup decisions are made.",
        "escalate_when": "Retention pressure is driving the decision more than the bundle quality itself.",
    },
    "reporting_ops": {
        "primary_action": "Compare history rows, snapshots, and dashboard payloads so the reporting layer reflects the same packet lineage.",
        "secondary_action": "Regenerate rollups only after schema and payload compatibility are verified.",
        "escalate_when": "Query or dashboard drift affects multiple owners or release channels at once.",
    },
    "partner_ops": {
        "primary_action": "Check whether queue-facing notes, remediation wording, and owner dashboards still point to the same next action.",
        "secondary_action": "Separate narrative drift from real packet or score drift before escalating to another owner.",
        "escalate_when": "The support queue is masking a deeper content, runtime, or release problem.",
    },
}


def status_for_issues(issues: list[ValidationIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "red"
    if issues:
        return "yellow"
    return "green"


def description(status: str) -> str:
    return STATUS_DESCRIPTIONS[status]


def route_for_issue(issue: ValidationIssue) -> str:
    prefix = issue.path.split(".", 1)[0] if issue.path else issue.code
    return OWNER_ROUTE.get(prefix, "partner_ops")


def severity_guidance(severity: str) -> str:
    return SEVERITY_GUIDANCE[severity]


def owner_summary(issues: list[ValidationIssue]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for issue in issues:
        owner = route_for_issue(issue)
        counts[owner] = counts.get(owner, 0) + 1
    return dict(sorted(counts.items()))


def severity_summary(issues: list[ValidationIssue]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for issue in issues:
        counts[issue.severity] = counts.get(issue.severity, 0) + 1
    return dict(sorted(counts.items()))


def owner_digest(issues: list[ValidationIssue]) -> dict[str, dict[str, object]]:
    digest: dict[str, dict[str, object]] = {}
    for issue in issues:
        owner = route_for_issue(issue)
        payload = digest.setdefault(owner, {"count": 0, "codes": set(), "paths": []})
        payload["count"] = int(payload["count"]) + 1
        payload["codes"].add(issue.code)
        if issue.path:
            payload["paths"].append(issue.path)
    return {
        owner: {
            "count": int(payload["count"]),
            "codes": sorted(payload["codes"]),
            "paths": sorted(payload["paths"]),
        }
        for owner, payload in sorted(digest.items())
    }


def status_payload(issues: list[ValidationIssue]) -> dict[str, object]:
    status = status_for_issues(issues)
    return {
        "status": status,
        "description": description(status),
        "owner_summary": owner_summary(issues),
        "severity_summary": severity_summary(issues),
        "owner_digest": owner_digest(issues),
        "issue_count": len(issues),
    }


def notification_lines(issues: list[ValidationIssue]) -> list[str]:
    status = status_for_issues(issues)
    lines = [f"audit packet status: {status}"]
    lines.append(description(status))
    for owner, count in owner_summary(issues).items():
        lines.append(f"{owner}: {count} issue(s)")
    if issues:
        severities = sorted({issue.severity for issue in issues})
        for severity in severities:
            lines.append(f"{severity}: {severity_guidance(severity)}")
    return lines


def owner_action_cards(issues: list[ValidationIssue]) -> dict[str, dict[str, str]]:
    cards: dict[str, dict[str, str]] = {}
    for owner in owner_summary(issues):
        cards[owner] = dict(REMEDIATION_MATRIX.get(owner, {}))
    return cards


def remediation_summary(issues: list[ValidationIssue]) -> dict[str, str]:
    summary: dict[str, str] = {}
    for owner, card in owner_action_cards(issues).items():
        pieces = []
        if card.get("primary_action"):
            pieces.append(f"primary action: {card['primary_action'].strip()}")
        if card.get("escalate_when"):
            pieces.append(f"escalate when: {card['escalate_when'].strip()}")
        summary[owner] = " ".join(piece for piece in pieces if piece)
    return summary


def render_status_brief(issues: list[ValidationIssue]) -> str:
    payload = status_payload(issues)
    lines = ["# Audit packet status brief", ""]
    lines.append(f"- status: {payload['status']}")
    lines.append(f"- issue count: {payload['issue_count']}")
    lines.append(f"- description: {payload['description']}")
    if payload["severity_summary"]:
        lines.append(f"- severity summary: {payload['severity_summary']}")
    lines.extend(["", "## Owner routing"])
    for owner, count in payload["owner_summary"].items():
        lines.append(f"- {owner}: {count} issue(s)")
        card = REMEDIATION_MATRIX.get(owner)
        if card:
            lines.append(f"  - primary action: {card['primary_action']}")
            lines.append(f"  - secondary action: {card['secondary_action']}")
            lines.append(f"  - escalate when: {card['escalate_when']}")
        digest = payload["owner_digest"].get(owner, {})
        if digest:
            lines.append(f"  - codes: {', '.join(digest['codes'])}")
            if digest["paths"]:
                lines.append(f"  - paths: {', '.join(digest['paths'])}")
    return "\n".join(lines) + "\n"


