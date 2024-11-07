from __future__ import annotations

from engineering_challenge.utils import json_digest


DASHBOARD_BLUEPRINTS = {
    "content_ops": {
        "headline": "Document routing and extraction overview",
        "primary_panels": [
            "owner_average_percent",
            "hidden_gap_watchlist",
            "field_coverage_warnings",
            "release_digest_changes",
        ],
        "drilldowns": [
            "document-classifier packet coverage",
            "content review queue by bundle",
            "routing prompt note alignment",
        ],
        "alerts": [
            "Raise a release alert when extraction field coverage drops in two consecutive trains.",
            "Escalate when public and hidden routing behavior diverge by more than the standard gap threshold.",
            "Show a warning when a packet digest changes without a title or note change in the catalog summary.",
        ],
        "narrative": "Content dashboards are meant to answer whether wording and extraction shape are still aligned, not just whether the latest score went up or down.",
    },
    "education_ops": {
        "headline": "Seat allocation fairness overview",
        "primary_panels": [
            "hidden_section_movement",
            "partner_release_mix",
            "owner_capacity_pressure",
            "fairness_flag_summary",
        ],
        "drilldowns": [
            "seat-allocation hidden cases",
            "owner blackout weeks",
            "partner-facing release notes",
        ],
        "alerts": [
            "Escalate when fairness-sensitive bundles remain watch band for two consecutive reviews.",
            "Show a scheduling warning when the owner is ready but the target train week is blacked out.",
            "Highlight releases where the note changed but the fairness callouts did not.",
        ],
        "narrative": "Education dashboards prioritize fairness, partner communication, and whether the hidden sections are still doing real review work.",
    },
    "finance_ops": {
        "headline": "Closeout and reserve operations overview",
        "primary_panels": [
            "ready_band_holdouts",
            "retention_action_summary",
            "closeout_hidden_gap",
            "audit_export_age",
        ],
        "drilldowns": [
            "merchant-closeout scorecards",
            "reserve-rollforward release notes",
            "treasury handoff summaries",
        ],
        "alerts": [
            "Escalate when reserve or closeout bundles become blocked without a new audit note.",
            "Surface rows that are technically prunable but still tied to close-sensitive work.",
            "Call out when a digest change coincides with a hidden-score drop.",
        ],
        "narrative": "Finance uses the dashboard to connect score movement with release timing, audit state, and retention pressure instead of reading those streams in isolation.",
    },
    "logistics_ops": {
        "headline": "Warehouse routing operations overview",
        "primary_panels": [
            "queue_latency_spikes",
            "blackout_and_quota_status",
            "route_repair_notes",
            "release_train_pressure",
        ],
        "drilldowns": [
            "warehouse-routing hidden failures",
            "facility-specific review notes",
            "support remediation summaries",
        ],
        "alerts": [
            "Warn when blackouts are the real blocker even though quota remains.",
            "Escalate when queue latency increases while route coverage notes change in the same period.",
            "Highlight repair-note mismatches across support and logistics artifacts.",
        ],
        "narrative": "Routing dashboards distinguish content issues, queue issues, and calendar issues because they demand different fixes.",
    },
    "platform_ops": {
        "headline": "Runtime and fulfillment overview",
        "primary_panels": [
            "worker_version_shift",
            "timeout_retry_clusters",
            "manifest_digest_changes",
            "execution_outlier_cases",
        ],
        "drilldowns": [
            "fulfillment-ledger transcripts",
            "identity-refresh packet coverage",
            "retry-horizon summaries",
        ],
        "alerts": [
            "Show a runtime warning when a worker-version change lines up with a spike in timeouts.",
            "Escalate when manifest digests drift without catalog changes.",
            "Flag execution outliers that are large enough to swamp the release decision surface.",
        ],
        "narrative": "Platform dashboards tell the story of operational shape first, then score impact.",
    },
    "procurement_ops": {
        "headline": "Vendor settlement overview",
        "primary_panels": [
            "vendor_exception_mix",
            "support_review_queue",
            "partner_retention_impact",
            "audit_packet_health",
        ],
        "drilldowns": [
            "vendor-settlement exception rows",
            "support terminology drift",
            "procurement release notes",
        ],
        "alerts": [
            "Warn when support and procurement terminology drift in consecutive releases.",
            "Highlight partner-facing bundles whose retention horizon changed.",
            "Escalate when vendor hidden cases lag behind workflow updates.",
        ],
        "narrative": "Procurement dashboards make dispute-handling and settlement language reviewable without reopening every artifact manually.",
    },
    "returns_ops": {
        "headline": "Returns recovery overview",
        "primary_panels": [
            "retryable_timeout_count",
            "returns_hidden_drift",
            "owner_dashboard_trend",
            "queue_pressure_summary",
        ],
        "drilldowns": [
            "returns-recovery case transcripts",
            "review-state balance",
            "disposition note changes",
        ],
        "alerts": [
            "Warn when runtime noise becomes the main reason a bundle falls into watch.",
            "Highlight disposition-language changes that were not mirrored in release notes.",
            "Escalate when owner capacity looks healthy but queue health keeps degrading.",
        ],
        "narrative": "Returns dashboards are built to separate retriable noise from real workflow drift.",
    },
    "revops": {
        "headline": "Recurring billing overview",
        "primary_panels": [
            "bundle_owner_matrix",
            "digest_drift_trend",
            "hidden_score_decay",
            "audit_latency_summary",
        ],
        "drilldowns": [
            "subscriber-billing scorecards",
            "ledger-adjacent comparisons",
            "release brief history",
        ],
        "alerts": [
            "Show a warning when recurring billing and closeout bundles start sharing failure signatures.",
            "Escalate when digest drift outpaces note updates.",
            "Highlight owners whose averages look calm while hidden variance rises.",
        ],
        "narrative": "Revops dashboards connect release storytelling with historical score behavior so the team does not mistake narrative drift for content drift.",
    },
    "risk_ops": {
        "headline": "Identity and controls overview",
        "primary_panels": [
            "hidden_gap_watchlist",
            "packet_field_coverage",
            "partner_control_changes",
            "audit_review_backlog",
        ],
        "drilldowns": [
            "identity-refresh packet details",
            "control wording changes",
            "partner release mix",
        ],
        "alerts": [
            "Warn when evidence quality becomes the dominant release concern.",
            "Escalate when partner-control wording moves without a risk signoff note.",
            "Highlight bundles where hidden decay is concentrated in one section.",
        ],
        "narrative": "Risk dashboards should make evidence and control concerns visible before they become release surprises.",
    },
    "sales_ops": {
        "headline": "Pricing handoff overview",
        "primary_panels": [
            "pricing_hidden_gap",
            "validation_mismatch_rate",
            "release_note_alignment",
            "finance_overlap_watch",
        ],
        "drilldowns": [
            "pricing-handoff scorecards",
            "policy text deltas",
            "sales-to-finance escalation notes",
        ],
        "alerts": [
            "Warn when hidden pricing cases lag behind policy note changes.",
            "Highlight bundles whose failure pattern overlaps with finance-owned closeout work.",
            "Escalate when narrative drift is the real blocker instead of raw quality.",
        ],
        "narrative": "Sales dashboards are there to show whether pricing language, validation behavior, and release narrative still tell the same story.",
    },
    "support_ops": {
        "headline": "Claims intake overview",
        "primary_panels": [
            "review_state_balance",
            "support_queue_latency",
            "taxonomy_drift_watch",
            "owner_average_percent",
        ],
        "drilldowns": [
            "claims-intake mixed runs",
            "support remediation notes",
            "risk escalation joins",
        ],
        "alerts": [
            "Warn when support review becomes the default path for too many bundles.",
            "Highlight taxonomy changes that moved notes but not hidden cases.",
            "Escalate when queue pressure is distorting apparent score health.",
        ],
        "narrative": "Support dashboards help reviewers tell whether the system is asking for content fixes, queue fixes, or release fixes.",
    },
    "treasury_ops": {
        "headline": "Reserve and payout overview",
        "primary_panels": [
            "retention_action_summary",
            "closeout_adjacency",
            "audit_packet_age",
            "reserve_hidden_drift",
        ],
        "drilldowns": [
            "reserve-rollforward scorecards",
            "treasury handoff notes",
            "archive-versus-prune candidates",
        ],
        "alerts": [
            "Warn when rows approach prune eligibility before audit expectations are satisfied.",
            "Highlight reserve bundles whose hidden score moved without a note change.",
            "Escalate when treasury is asked to approve without retention context.",
        ],
        "narrative": "Treasury dashboards connect score movement with retention and close-window risk instead of leaving those as separate manual checks.",
    },
}


def blueprint(owner: str) -> dict[str, object]:
    return dict(DASHBOARD_BLUEPRINTS[owner])


def primary_panels(owner: str) -> list[str]:
    return list(DASHBOARD_BLUEPRINTS[owner]["primary_panels"])


def drilldowns(owner: str) -> list[str]:
    return list(DASHBOARD_BLUEPRINTS[owner]["drilldowns"])


def alerts(owner: str) -> list[str]:
    return list(DASHBOARD_BLUEPRINTS[owner]["alerts"])


def digest(owner: str) -> str:
    return json_digest(DASHBOARD_BLUEPRINTS[owner])


def render_markdown(owner: str) -> str:
    item = DASHBOARD_BLUEPRINTS[owner]
    lines = [f"# {item['headline']}", "", item["narrative"], "", "## Primary panels"]
    lines.extend(f"- {panel}" for panel in item["primary_panels"])
    lines.extend(["", "## Drilldowns"])
    lines.extend(f"- {entry}" for entry in item["drilldowns"])
    lines.extend(["", "## Alerts"])
    lines.extend(f"- {entry}" for entry in item["alerts"])
    return "\n".join(lines) + "\n"
