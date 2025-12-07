from __future__ import annotations

from typing import Mapping

from .issue_taxonomy import classify_issue_messages, issue_rollup
from .operator_guidance import build_operator_brief
from .threshold_profiles import threshold_profile_summary
from pixelforge_ops.utils import json_digest


def build_quality_report(
    bundle_id: str,
    lane: str,
    gate: Mapping[str, object],
    histogram: Mapping[str, object] | None = None,
    color_delta: Mapping[str, object] | None = None,
    region_diff: Mapping[str, object] | None = None,
    tile_coverage: Mapping[str, object] | None = None,
    metadata_policy: Mapping[str, object] | None = None,
    codec_profile: Mapping[str, object] | None = None,
    render_manifest: Mapping[str, object] | None = None,
    partner_export: Mapping[str, object] | None = None,
) -> dict[str, object]:
    issue_codes = classify_issue_messages(
        [
            *list(dict(gate).get("issues", [])),
            *list(dict(histogram or {}).get("issues", [])),
            *list(dict(color_delta or {}).get("issues", [])),
            *list(dict(region_diff or {}).get("issues", [])),
            *list(dict(tile_coverage or {}).get("issues", [])),
            *list(dict(metadata_policy or {}).get("issues", [])),
            *list(dict(codec_profile or {}).get("issues", [])),
            *list(dict(render_manifest or {}).get("issues", [])),
            *list(dict(partner_export or {}).get("issues", [])),
        ]
    )
    operator_brief = build_operator_brief(lane, issue_codes, str(dict(gate).get("status", "unknown")))
    payload = {
        "bundle_id": bundle_id,
        "lane": lane,
        "gate": dict(gate),
        "threshold_profile": threshold_profile_summary(lane),
        "issue_rollup": issue_rollup(issue_codes),
        "operator_brief": operator_brief,
        "signals": {
            "histogram": dict(histogram or {}),
            "color_delta": dict(color_delta or {}),
            "region_diff": dict(region_diff or {}),
            "tile_coverage": dict(tile_coverage or {}),
            "metadata_policy": dict(metadata_policy or {}),
            "codec_profile": dict(codec_profile or {}),
            "render_manifest": dict(render_manifest or {}),
            "partner_export": dict(partner_export or {}),
        },
    }
    payload["digest"] = json_digest({key: value for key, value in payload.items() if key != "digest"})
    return payload


def render_quality_report_markdown(report: Mapping[str, object]) -> str:
    lines = [f"# Imaging quality report: {report['bundle_id']}", "", f"- lane: {report['lane']}", f"- digest: {report['digest']}", ""]
    gate = dict(report.get("gate", {}))
    lines.append("## Gate")
    lines.append("")
    lines.append(f"- status: {gate.get('status', 'unknown')}")
    lines.append(f"- blocked count: {gate.get('blocked_count', 0)}")
    lines.append(f"- warn count: {gate.get('warn_count', 0)}")
    lines.extend(
        [
            "",
            "## Threshold profile",
            "",
            f"- release channel: {dict(report.get('threshold_profile', {})).get('release_channel', 'unknown')}",
            f"- comparators: {', '.join(dict(report.get('threshold_profile', {})).get('comparator_names', []))}",
            f"- release blockers: {', '.join(dict(report.get('threshold_profile', {})).get('release_blockers', []))}",
            "",
            "## Operator brief",
            "",
            f"- owners: {', '.join(dict(report.get('operator_brief', {})).get('owners', []))}",
            f"- issue codes: {', '.join(dict(report.get('operator_brief', {})).get('issue_codes', []))}",
        ]
    )
    for signal_name, payload in dict(report.get("signals", {})).items():
        lines.extend(["", f"## {signal_name}", ""])
        lines.append(f"- status: {payload.get('status', 'unknown')}")
        if payload.get("issues"):
            for issue in payload["issues"]:
                lines.append(f"- issue: {issue}")
    return "\n".join(lines) + "\n"
