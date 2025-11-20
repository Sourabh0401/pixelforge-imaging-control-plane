from __future__ import annotations

COLUMN_CATALOG = [
    {"column": "bundle_id", "surface": "portfolio", "label": "Bundle", "required": True, "width": 18},
    {"column": "owner", "surface": "portfolio", "label": "Owner", "required": True, "width": 16},
    {"column": "percent", "surface": "portfolio", "label": "Percent", "required": True, "width": 10},
    {"column": "band", "surface": "portfolio", "label": "Band", "required": True, "width": 10},
    {"column": "public_percent", "surface": "portfolio", "label": "Public", "required": True, "width": 10},
    {"column": "hidden_percent", "surface": "portfolio", "label": "Hidden", "required": True, "width": 10},
    {"column": "policy_flags", "surface": "portfolio", "label": "Flags", "required": False, "width": 24},
    {"column": "release_channel", "surface": "portfolio", "label": "Channel", "required": False, "width": 14},
    {"column": "review_state", "surface": "portfolio", "label": "Review", "required": False, "width": 14},
    {"column": "average_percent", "surface": "owner_dashboard", "label": "Average %", "required": True, "width": 12},
    {"column": "ready_count", "surface": "owner_dashboard", "label": "Ready", "required": True, "width": 8},
    {"column": "watch_count", "surface": "owner_dashboard", "label": "Watch", "required": True, "width": 8},
    {"column": "risk_count", "surface": "owner_dashboard", "label": "Risk", "required": True, "width": 8},
    {"column": "blocked_count", "surface": "owner_dashboard", "label": "Blocked", "required": True, "width": 9},
    {"column": "hidden_gap", "surface": "owner_dashboard", "label": "Hidden Gap", "required": True, "width": 12},
    {"column": "rerun_rate", "surface": "owner_dashboard", "label": "Rerun %", "required": False, "width": 10},
    {"column": "queue_latency_ms", "surface": "history", "label": "Queue Latency", "required": True, "width": 14},
    {"column": "worker_version", "surface": "history", "label": "Worker", "required": True, "width": 12},
    {"column": "started_at", "surface": "history", "label": "Started", "required": True, "width": 20},
    {"column": "artifact_digest", "surface": "history", "label": "Digest", "required": True, "width": 18},
    {"column": "operator_notes", "surface": "history", "label": "Operator Notes", "required": False, "width": 40},
    {"column": "release_id", "surface": "release_notes", "label": "Release", "required": True, "width": 18},
    {"column": "created_at", "surface": "release_notes", "label": "Created", "required": True, "width": 20},
    {"column": "digest", "surface": "release_notes", "label": "Digest", "required": True, "width": 18},
    {"column": "case_count", "surface": "bundle_summary", "label": "Cases", "required": True, "width": 8},
    {"column": "hidden_case_count", "surface": "bundle_summary", "label": "Hidden Cases", "required": True, "width": 12},
    {"column": "public_case_count", "surface": "bundle_summary", "label": "Public Cases", "required": True, "width": 12},
    {"column": "comparator_mix", "surface": "bundle_summary", "label": "Comparators", "required": False, "width": 24},
    {"column": "section_mix", "surface": "bundle_summary", "label": "Sections", "required": False, "width": 24},
    {"column": "metadata_gap", "surface": "bundle_summary", "label": "Metadata Gap", "required": False, "width": 14},
    {"column": "remediation_reason", "surface": "remediation", "label": "Reason", "required": True, "width": 28},
    {"column": "assigned_owner", "surface": "remediation", "label": "Assigned Owner", "required": True, "width": 18},
    {"column": "next_review_at", "surface": "remediation", "label": "Next Review", "required": False, "width": 18},
    {"column": "evidence_status", "surface": "audit", "label": "Evidence", "required": True, "width": 12},
    {"column": "packet_path", "surface": "audit", "label": "Packet Path", "required": True, "width": 28},
    {"column": "retention_days", "surface": "audit", "label": "Retention", "required": True, "width": 10},
    {"column": "trace_count", "surface": "audit", "label": "Trace Count", "required": False, "width": 12},
    {"column": "history_row_count", "surface": "snapshot", "label": "History Rows", "required": True, "width": 12},
    {"column": "owner_mix", "surface": "snapshot", "label": "Owner Mix", "required": True, "width": 20},
    {"column": "band_counts", "surface": "snapshot", "label": "Bands", "required": True, "width": 18},
]


def columns_for_surface(surface: str) -> list[dict[str, object]]:
    return [dict(row) for row in COLUMN_CATALOG if row["surface"] == surface]


def required_columns(surface: str) -> list[str]:
    return [row["column"] for row in COLUMN_CATALOG if row["surface"] == surface and row["required"]]


def display_labels(surface: str) -> dict[str, str]:
    return {row["column"]: row["label"] for row in COLUMN_CATALOG if row["surface"] == surface}
