from __future__ import annotations

from typing import Mapping

from .issue_digest import digest_issues, lane_counts, normalized_issues, render_issue_lines, severity_counts


def _issues_from_summary(lane: str, kind: str, summary: Mapping[str, object]) -> list[dict[str, object]]:
    status = str(summary.get("status", "ok"))
    if status == "ok" and not summary.get("issues"):
        return []
    severity = "block" if status == "block" else "warn"
    issues = []
    for message in summary.get("issues", []):
        issues.append(
            {
                "severity": severity,
                "code": f"{kind}:{status}",
                "lane": lane,
                "kind": kind,
                "message": str(message),
                "details": dict(summary),
            }
        )
    if not issues:
        issues.append(
            {
                "severity": severity,
                "code": f"{kind}:{status}",
                "lane": lane,
                "kind": kind,
                "message": f"{kind} reported {status}",
                "details": dict(summary),
            }
        )
    return issues


def gate_imaging_release(
    bundle_id: str,
    lane: str,
    histogram: Mapping[str, object] | None = None,
    color_delta: Mapping[str, object] | None = None,
    region_diff: Mapping[str, object] | None = None,
    tile_coverage: Mapping[str, object] | None = None,
    metadata_policy: Mapping[str, object] | None = None,
    codec_profile: Mapping[str, object] | None = None,
    render_manifest: Mapping[str, object] | None = None,
    partner_export: Mapping[str, object] | None = None,
) -> dict[str, object]:
    raw_issues = []
    for kind, summary in (
        ("histogram", histogram),
        ("color-delta", color_delta),
        ("region-diff", region_diff),
        ("tile-coverage", tile_coverage),
        ("metadata-policy", metadata_policy),
        ("codec-profile", codec_profile),
        ("render-manifest", render_manifest),
        ("partner-export", partner_export),
    ):
        if summary is not None:
            raw_issues.extend(_issues_from_summary(lane, kind, summary))
    issues = normalized_issues(raw_issues)
    blocked = [issue for issue in issues if issue["severity"] == "block"]
    warned = [issue for issue in issues if issue["severity"] == "warn"]
    status = "block" if blocked else "warn" if warned else "ok"
    return {
        "bundle_id": bundle_id,
        "lane": lane,
        "passed": status != "block",
        "status": status,
        "severity": status,
        "issue_count": len(issues),
        "blocked_count": len(blocked),
        "warn_count": len(warned),
        "issues": issues,
        "severity_summary": severity_counts(issues),
        "lane_summary": lane_counts(issues),
        "digest": digest_issues(issues),
        "brief_lines": render_issue_lines(issues),
    }


def merge_lane_gates(gates: list[Mapping[str, object]]) -> dict[str, object]:
    normalized = [dict(gate) for gate in gates]
    issues = []
    for gate in normalized:
        issues.extend(gate.get("issues", []))
    blocked_lanes = sorted(str(gate["lane"]) for gate in normalized if str(gate.get("status")) == "block")
    warned_lanes = sorted(str(gate["lane"]) for gate in normalized if str(gate.get("status")) == "warn")
    status = "block" if blocked_lanes else "warn" if warned_lanes else "ok"
    return {
        "passed": status != "block",
        "status": status,
        "severity": status,
        "blocked_lanes": blocked_lanes,
        "warned_lanes": warned_lanes,
        "lane_count": len(normalized),
        "issues": normalized_issues(issues),
        "severity_summary": severity_counts(issues),
        "digest": digest_issues(issues),
    }


def render_gate_markdown(gate: Mapping[str, object]) -> str:
    lines = [f"# Imaging release gate for {gate['bundle_id']}", "", f"- lane: {gate['lane']}", f"- status: {gate['status']}", ""]
    lines.append("## Issues")
    for line in gate.get("brief_lines", []):
        lines.append(f"- {line}")
    return "\n".join(lines) + "\n"

