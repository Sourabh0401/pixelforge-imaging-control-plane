from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engineering_challenge.auditpack import contracts, evidence_store, trace
from engineering_challenge.release import manifest_to_dict
from engineering_challenge.utils import json_digest


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    severity: str
    message: str
    path: str = ""


def expected_paths(bundle_id: str, run_id: str) -> dict[str, str]:
    return evidence_store.evidence_map(bundle_id, run_id)


def _issue(code: str, severity: str, message: str, path: str = "") -> ValidationIssue:
    return ValidationIssue(code, severity, message, path)


def validate_required_paths(packet: dict[str, Any]) -> list[ValidationIssue]:
    bundle_id = str(packet["bundle"]["bundle_id"])
    run_id = str(packet["run"]["run_id"])
    expected = expected_paths(bundle_id, run_id)
    present = packet.get("artifact_paths", expected)
    missing = set(expected) - set(present)
    unexpected = set(present) - set(expected)
    issues: list[ValidationIssue] = []
    for path in sorted(missing):
        issues.append(_issue("missing-path", "error", f"required artifact path missing: {path}", path))
    for path in sorted(unexpected):
        issues.append(_issue("unexpected-path", "warn", f"unexpected artifact path present: {path}", path))
    return issues


def validate_required_fields(packet: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    sources = {
        "bundle": packet.get("bundle", {}),
        "run": packet.get("run", {}),
        "scorecard": packet.get("scorecard", {}),
        "release_manifest": packet.get("release_manifest", {}),
    }
    for source, payload in sources.items():
        for field in contracts.validate_record_fields(source, payload):
            issues.append(_issue("missing-field", "error", f"{source} missing required field {field}", f"{source}.{field}"))
    return issues


def validate_trace_payload(packet: dict[str, Any]) -> list[ValidationIssue]:
    rows = packet.get("trace_rows", [])
    run_results = packet.get("run", {}).get("case_results", [])
    run_case_ids = {row["case_id"] for row in run_results}
    trace_case_ids = {row["case_id"] for row in rows}
    issues: list[ValidationIssue] = []
    for case_id in sorted(run_case_ids - trace_case_ids):
        issues.append(_issue("missing-trace-row", "error", f"trace row missing for {case_id}", case_id))
    for case_id in sorted(trace_case_ids - run_case_ids):
        issues.append(_issue("unexpected-trace-row", "warn", f"trace row has unknown case {case_id}", case_id))
    return issues


def validate_manifest_digest(packet: dict[str, Any]) -> list[ValidationIssue]:
    manifest = packet.get("release_manifest", {})
    digest = manifest.get("digest")
    if not digest:
        return [_issue("missing-manifest-digest", "error", "release manifest missing digest", "release_manifest.digest")]
    copied = dict(manifest)
    copied.pop("digest", None)
    rebuilt = json_digest(copied)
    if rebuilt != digest:
        return [_issue("manifest-drift", "error", "release manifest digest does not match payload", "release_manifest.digest")]
    return []


def validate_packet_digest(packet: dict[str, Any]) -> list[ValidationIssue]:
    digest = packet.get("digest")
    if not digest:
        return [_issue("missing-packet-digest", "error", "packet missing digest", "digest")]
    copied = dict(packet)
    copied.pop("digest", None)
    rebuilt = json_digest(copied)
    if rebuilt != digest:
        return [_issue("packet-drift", "error", "packet digest does not match payload", "digest")]
    return []


def validate_channel_retention(packet: dict[str, Any]) -> list[ValidationIssue]:
    manifest = packet.get("release_manifest", {})
    channel = manifest.get("notes", ["internal"])[0] if manifest.get("notes") else "internal"
    if channel not in {"internal", "rehearsal", "pilot", "partner", "ops-only"}:
        return [_issue("unknown-channel", "warn", f"packet references unknown channel {channel}", "release_manifest.notes")]
    return []


def validate_packet(packet: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    issues.extend(validate_required_fields(packet))
    issues.extend(validate_required_paths(packet))
    issues.extend(validate_trace_payload(packet))
    issues.extend(validate_manifest_digest(packet))
    issues.extend(validate_packet_digest(packet))
    issues.extend(validate_channel_retention(packet))
    return issues


def severity_counts(issues: list[ValidationIssue]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for issue in issues:
        counts[issue.severity] = counts.get(issue.severity, 0) + 1
    return dict(sorted(counts.items()))


def blocking_issues(issues: list[ValidationIssue]) -> list[ValidationIssue]:
    return [issue for issue in issues if issue.severity == "error"]


def issue_summary(issues: list[ValidationIssue]) -> dict[str, object]:
    return {
        "count": len(issues),
        "severity_counts": severity_counts(issues),
        "codes": sorted({issue.code for issue in issues}),
        "blocking": [issue.code for issue in blocking_issues(issues)],
    }


def packet_with_trace(bundle: dict[str, Any], run: dict[str, Any], scorecard: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    rows = [
        {
            "case_id": row["case_id"],
            "section": row["section"],
            "status": row["status"],
            "runtime_ms": row["runtime_ms"],
            "points": row["points"],
            "hidden": row["hidden"],
        }
        for row in run["case_results"]
    ]
    packet = {
        "bundle": bundle,
        "run": run,
        "scorecard": scorecard,
        "release_manifest": manifest,
        "trace_rows": rows,
    }
    packet["artifact_paths"] = expected_paths(bundle["bundle_id"], run["run_id"])
    packet["digest"] = json_digest(packet)
    return packet
