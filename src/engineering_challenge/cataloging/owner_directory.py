from __future__ import annotations

OWNER_DIRECTORY = {
    "finance_ops": {
        "team_name": "Finance Operations",
        "region": "amer",
        "contacts": {
            "lead": "finance-ops-lead@internal.example",
            "backup": "finance-ops-backup@internal.example",
            "slack": "#finance-ops",
            "pager": "finance-ops-primary",
        },
        "queues": {
            "release": "queue-finance-release",
            "audit": "queue-finance-audit",
            "support": "queue-finance-support",
        },
        "escalation_chain": ["finance_ops", "release_ops", "support_quality", "audit_program"],
    },
    "support_ops": {
        "team_name": "Support Operations",
        "region": "amer",
        "contacts": {
            "lead": "support-ops-lead@internal.example",
            "backup": "support-ops-backup@internal.example",
            "slack": "#support-ops",
            "pager": "support-ops-primary",
        },
        "queues": {
            "release": "queue-support-release",
            "audit": "queue-support-audit",
            "support": "queue-support-support",
        },
        "escalation_chain": ["support_ops", "release_ops", "support_quality", "audit_program"],
    },
    "treasury_ops": {
        "team_name": "Treasury Operations",
        "region": "amer",
        "contacts": {
            "lead": "treasury-ops-lead@internal.example",
            "backup": "treasury-ops-backup@internal.example",
            "slack": "#treasury-ops",
            "pager": "treasury-ops-primary",
        },
        "queues": {
            "release": "queue-treasury-release",
            "audit": "queue-treasury-audit",
            "support": "queue-treasury-support",
        },
        "escalation_chain": ["treasury_ops", "release_ops", "support_quality", "audit_program"],
    },
    "logistics_ops": {
        "team_name": "Logistics Operations",
        "region": "emea",
        "contacts": {
            "lead": "logistics-ops-lead@internal.example",
            "backup": "logistics-ops-backup@internal.example",
            "slack": "#logistics-ops",
            "pager": "logistics-ops-primary",
        },
        "queues": {
            "release": "queue-logistics-release",
            "audit": "queue-logistics-audit",
            "support": "queue-logistics-support",
        },
        "escalation_chain": ["logistics_ops", "release_ops", "support_quality", "audit_program"],
    },
    "risk_ops": {
        "team_name": "Risk Operations",
        "region": "amer",
        "contacts": {
            "lead": "risk-ops-lead@internal.example",
            "backup": "risk-ops-backup@internal.example",
            "slack": "#risk-ops",
            "pager": "risk-ops-primary",
        },
        "queues": {
            "release": "queue-risk-release",
            "audit": "queue-risk-audit",
            "support": "queue-risk-support",
        },
        "escalation_chain": ["risk_ops", "release_ops", "support_quality", "audit_program"],
    },
    "revops": {
        "team_name": "Revenue Operations",
        "region": "amer",
        "contacts": {
            "lead": "revops-lead@internal.example",
            "backup": "revops-backup@internal.example",
            "slack": "#revops",
            "pager": "revops-primary",
        },
        "queues": {
            "release": "queue-revops-release",
            "audit": "queue-revops-audit",
            "support": "queue-revops-support",
        },
        "escalation_chain": ["revops", "release_ops", "support_quality", "audit_program"],
    },
    "education_ops": {
        "team_name": "Education Operations",
        "region": "amer",
        "contacts": {
            "lead": "education-ops-lead@internal.example",
            "backup": "education-ops-backup@internal.example",
            "slack": "#education-ops",
            "pager": "education-ops-primary",
        },
        "queues": {
            "release": "queue-education-release",
            "audit": "queue-education-audit",
            "support": "queue-education-support",
        },
        "escalation_chain": ["education_ops", "release_ops", "support_quality", "audit_program"],
    },
    "platform_ops": {
        "team_name": "Platform Operations",
        "region": "apac",
        "contacts": {
            "lead": "platform-ops-lead@internal.example",
            "backup": "platform-ops-backup@internal.example",
            "slack": "#platform-ops",
            "pager": "platform-ops-primary",
        },
        "queues": {
            "release": "queue-platform-release",
            "audit": "queue-platform-audit",
            "support": "queue-platform-support",
        },
        "escalation_chain": ["platform_ops", "release_ops", "support_quality", "audit_program"],
    },
    "content_ops": {
        "team_name": "Content Operations",
        "region": "emea",
        "contacts": {
            "lead": "content-ops-lead@internal.example",
            "backup": "content-ops-backup@internal.example",
            "slack": "#content-ops",
            "pager": "content-ops-primary",
        },
        "queues": {
            "release": "queue-content-release",
            "audit": "queue-content-audit",
            "support": "queue-content-support",
        },
        "escalation_chain": ["content_ops", "release_ops", "support_quality", "audit_program"],
    },
    "procurement_ops": {
        "team_name": "Procurement Operations",
        "region": "emea",
        "contacts": {
            "lead": "procurement-ops-lead@internal.example",
            "backup": "procurement-ops-backup@internal.example",
            "slack": "#procurement-ops",
            "pager": "procurement-ops-primary",
        },
        "queues": {
            "release": "queue-procurement-release",
            "audit": "queue-procurement-audit",
            "support": "queue-procurement-support",
        },
        "escalation_chain": ["procurement_ops", "release_ops", "support_quality", "audit_program"],
    },
    "sales_ops": {
        "team_name": "Sales Operations",
        "region": "amer",
        "contacts": {
            "lead": "sales-ops-lead@internal.example",
            "backup": "sales-ops-backup@internal.example",
            "slack": "#sales-ops",
            "pager": "sales-ops-primary",
        },
        "queues": {
            "release": "queue-sales-release",
            "audit": "queue-sales-audit",
            "support": "queue-sales-support",
        },
        "escalation_chain": ["sales_ops", "release_ops", "support_quality", "audit_program"],
    },
    "returns_ops": {
        "team_name": "Returns Operations",
        "region": "apac",
        "contacts": {
            "lead": "returns-ops-lead@internal.example",
            "backup": "returns-ops-backup@internal.example",
            "slack": "#returns-ops",
            "pager": "returns-ops-primary",
        },
        "queues": {
            "release": "queue-returns-release",
            "audit": "queue-returns-audit",
            "support": "queue-returns-support",
        },
        "escalation_chain": ["returns_ops", "release_ops", "support_quality", "audit_program"],
    },
}

ROLE_DIRECTORY = [
    {"role": "release_manager", "team": "release_ops", "region": "amer", "requires_weekly_digest": True},
    {"role": "support_quality", "team": "support_quality", "region": "amer", "requires_weekly_digest": True},
    {"role": "audit_program", "team": "audit_program", "region": "emea", "requires_weekly_digest": False},
    {"role": "difficulty_owner", "team": "curriculum_quality", "region": "amer", "requires_weekly_digest": True},
    {"role": "hidden_owner", "team": "assessment_security", "region": "apac", "requires_weekly_digest": True},
    {"role": "history_analyst", "team": "ops_analytics", "region": "amer", "requires_weekly_digest": False},
    {"role": "dashboard_editor", "team": "ops_analytics", "region": "emea", "requires_weekly_digest": False},
    {"role": "remediation_owner", "team": "bundle_remediation", "region": "amer", "requires_weekly_digest": True},
]

QUEUE_SERVICE_LEVELS = {
    "queue-finance-release": {"target_hours": 8, "escalate_after_hours": 16},
    "queue-support-release": {"target_hours": 8, "escalate_after_hours": 16},
    "queue-treasury-release": {"target_hours": 10, "escalate_after_hours": 20},
    "queue-logistics-release": {"target_hours": 12, "escalate_after_hours": 24},
    "queue-risk-release": {"target_hours": 6, "escalate_after_hours": 12},
    "queue-revops-release": {"target_hours": 10, "escalate_after_hours": 18},
    "queue-education-release": {"target_hours": 12, "escalate_after_hours": 24},
    "queue-platform-release": {"target_hours": 8, "escalate_after_hours": 14},
    "queue-content-release": {"target_hours": 10, "escalate_after_hours": 18},
    "queue-procurement-release": {"target_hours": 14, "escalate_after_hours": 28},
    "queue-sales-release": {"target_hours": 10, "escalate_after_hours": 18},
    "queue-returns-release": {"target_hours": 12, "escalate_after_hours": 22},
}


def owner_row(owner: str) -> dict[str, object]:
    return dict(OWNER_DIRECTORY[owner])


def primary_contact(owner: str) -> str:
    return str(OWNER_DIRECTORY[owner]["contacts"]["lead"])


def escalation_chain(owner: str) -> tuple[str, ...]:
    return tuple(OWNER_DIRECTORY[owner]["escalation_chain"])


def owners_by_region(region: str) -> list[str]:
    return sorted(owner for owner, payload in OWNER_DIRECTORY.items() if payload["region"] == region)


def queue_service_level(queue_name: str) -> dict[str, int]:
    return dict(QUEUE_SERVICE_LEVELS[queue_name])


def weekly_digest_roles() -> list[str]:
    return [row["role"] for row in ROLE_DIRECTORY if row["requires_weekly_digest"]]
