from __future__ import annotations

from typing import Mapping


def archive_readiness_summary(
    gate: Mapping[str, object],
    manifest: Mapping[str, object],
    packet_status: Mapping[str, object],
) -> dict[str, object]:
    issues = []
    if str(gate.get("status", "ok")) == "block":
        issues.append("release gate still blocked")
    if not bool(manifest.get("passed", True)):
        issues.append("render manifest still failing validation")
    if str(packet_status.get("status", "green")) == "red":
        issues.append("audit packet status still red")
    status = "block" if issues else "ok"
    return {
        "passed": not issues,
        "status": status,
        "severity": status,
        "issue_codes": ["archive-readiness"] if issues else [],
        "issues": issues,
    }

