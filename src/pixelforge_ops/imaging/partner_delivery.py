from __future__ import annotations

from typing import Mapping, Sequence

from .lane_contracts import lane_release_channel, required_codecs_for_lane
from .render_manifest import render_manifest_summary


def delivery_contract(lane: str) -> dict[str, object]:
    return {
        "lane": lane,
        "channel": lane_release_channel(lane),
        "required_codecs": list(required_codecs_for_lane(lane)),
        "required_files": ["manifest.json", "release_notes.md", "audit_packet.json"],
    }


def partner_delivery_summary(
    lane: str,
    package: Mapping[str, object],
    manifest: Mapping[str, object],
) -> dict[str, object]:
    contract = delivery_contract(lane)
    files = {str(path) for path in package.get("files", [])}
    issues = []
    for path in contract["required_files"]:
        if path not in files:
            issues.append(f"missing delivery file: {path}")
    available_codecs = {str(codec).lower() for codec in package.get("codecs", [])}
    for codec in contract["required_codecs"]:
        if codec not in available_codecs:
            issues.append(f"missing partner codec: {codec}")
    manifest_summary = render_manifest_summary(manifest)
    issues.extend(f"manifest: {message}" for message in manifest_summary["issues"])
    status = "block" if issues else "ok"
    return {
        "passed": not issues,
        "status": status,
        "severity": status,
        "issue_codes": ["partner-delivery"] if issues else [],
        "issues": issues,
        "contract": contract,
        "manifest": manifest_summary,
    }

