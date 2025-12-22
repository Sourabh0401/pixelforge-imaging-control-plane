from __future__ import annotations

"""
Final partner/export readiness scoring.

The release gate answers “can the lane move?”  Export readiness answers “if it
does move, how safe is the packet for the next downstream consumer?”  That
question matters for partner, archive, and support-replay flows where a lane
may technically pass but still need extra follow-up before the packet is useful
to someone else.
"""

from typing import Mapping


def readiness_score(
    gate: Mapping[str, object],
    partner_delivery: Mapping[str, object],
    partner_export: Mapping[str, object],
    manifest_consistency: Mapping[str, object] | None = None,
    artifact_reconciliation: Mapping[str, object] | None = None,
) -> int:
    score = 100
    if str(gate.get("status")) == "block":
        score -= 50
    elif str(gate.get("status")) == "warn":
        score -= 20
    if str(partner_delivery.get("status")) == "block":
        score -= 25
    if str(partner_export.get("status")) == "block":
        score -= 20
    if manifest_consistency is not None and str(manifest_consistency.get("status")) == "block":
        score -= 15
    if artifact_reconciliation is not None and str(artifact_reconciliation.get("status")) == "block":
        score -= 20
    return max(score, 0)


def readiness_band(score: int) -> str:
    if score >= 90:
        return "release-ready"
    if score >= 70:
        return "watch"
    if score >= 45:
        return "stabilize"
    return "blocked"


def readiness_actions(
    gate: Mapping[str, object],
    partner_delivery: Mapping[str, object],
    partner_export: Mapping[str, object],
    manifest_consistency: Mapping[str, object] | None = None,
    artifact_reconciliation: Mapping[str, object] | None = None,
) -> list[str]:
    actions = []
    if str(gate.get("status")) == "block":
        actions.append("resolve imaging release blockers before export handoff")
    if str(partner_delivery.get("status")) == "block":
        actions.append("repair required delivery files or metadata before partner export")
    if str(partner_export.get("status")) == "block":
        actions.append("rebuild partner packet and verify export contract")
    if manifest_consistency is not None and str(manifest_consistency.get("status")) != "ok":
        actions.append("compare current manifest against the last accepted packet")
    if artifact_reconciliation is not None and str(artifact_reconciliation.get("status")) != "ok":
        actions.append("reconcile missing or renamed artifacts before packaging")
    if not actions:
        actions.append("packet is ready for the next release or partner checkpoint")
    return actions


def export_readiness_summary(
    gate: Mapping[str, object],
    partner_delivery: Mapping[str, object],
    partner_export: Mapping[str, object],
    manifest_consistency: Mapping[str, object] | None = None,
    artifact_reconciliation: Mapping[str, object] | None = None,
) -> dict[str, object]:
    score = readiness_score(
        gate,
        partner_delivery,
        partner_export,
        manifest_consistency=manifest_consistency,
        artifact_reconciliation=artifact_reconciliation,
    )
    band = readiness_band(score)
    actions = readiness_actions(
        gate,
        partner_delivery,
        partner_export,
        manifest_consistency=manifest_consistency,
        artifact_reconciliation=artifact_reconciliation,
    )
    hard_block = any(
        str(summary.get("status")) == "block"
        for summary in (
            dict(partner_delivery),
            dict(partner_export),
            dict(manifest_consistency or {}),
            dict(artifact_reconciliation or {}),
        )
    )
    status = "block" if hard_block or band == "blocked" else "warn" if band in {"watch", "stabilize"} else "ok"
    return {
        "status": status,
        "severity": status,
        "passed": status != "block",
        "issue_codes": ["export-readiness"] if status != "ok" else [],
        "issues": actions if status != "ok" else [],
        "score": score,
        "band": band,
        "actions": actions,
    }
