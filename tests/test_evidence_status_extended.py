from __future__ import annotations

import unittest

from engineering_challenge.auditpack import evidence_status
from engineering_challenge.auditpack.evidence_validator import ValidationIssue


def _issue(code: str, severity: str, path: str) -> ValidationIssue:
    return ValidationIssue(code, severity, f"{code} on {path}", path)


class EvidenceStatusExtendedTests(unittest.TestCase):
    def test_status_for_issues_is_green_when_empty(self) -> None:
        self.assertEqual(evidence_status.status_for_issues([]), "green")

    def test_status_for_issues_is_yellow_for_warning_only(self) -> None:
        self.assertEqual(evidence_status.status_for_issues([_issue("unexpected-path", "warn", "artifact_paths.extra")]), "yellow")

    def test_status_for_issues_is_red_when_error_present(self) -> None:
        self.assertEqual(evidence_status.status_for_issues([_issue("missing-field", "error", "bundle.owner")]), "red")

    def test_description_returns_green_text(self) -> None:
        self.assertIn("structurally complete", evidence_status.description("green"))

    def test_description_returns_yellow_text(self) -> None:
        self.assertIn("warnings", evidence_status.description("yellow"))

    def test_description_returns_red_text(self) -> None:
        self.assertIn("missing required information", evidence_status.description("red"))

    def test_severity_guidance_for_error(self) -> None:
        self.assertIn("Blocking issue", evidence_status.severity_guidance("error"))

    def test_severity_guidance_for_warn(self) -> None:
        self.assertIn("Non-blocking issue", evidence_status.severity_guidance("warn"))

    def test_severity_guidance_for_info(self) -> None:
        self.assertIn("worth recording", evidence_status.severity_guidance("info"))

    def test_route_for_bundle_issue(self) -> None:
        self.assertEqual(evidence_status.route_for_issue(_issue("missing-field", "error", "bundle.owner")), "content_ops")

    def test_route_for_run_issue(self) -> None:
        self.assertEqual(evidence_status.route_for_issue(_issue("missing-field", "error", "run.started_at")), "platform_ops")

    def test_route_for_scorecard_issue(self) -> None:
        self.assertEqual(evidence_status.route_for_issue(_issue("missing-field", "error", "scorecard.percent")), "finance_ops")

    def test_route_for_release_manifest_issue(self) -> None:
        self.assertEqual(
            evidence_status.route_for_issue(_issue("missing-field", "error", "release_manifest.digest")),
            "release_ops",
        )

    def test_route_for_trace_rows_issue(self) -> None:
        self.assertEqual(evidence_status.route_for_issue(_issue("missing-trace-row", "error", "trace_rows")), "platform_ops")

    def test_route_for_artifact_paths_issue(self) -> None:
        self.assertEqual(evidence_status.route_for_issue(_issue("missing-path", "error", "artifact_paths.bundle")), "risk_ops")

    def test_route_for_packet_digest_issue(self) -> None:
        self.assertEqual(evidence_status.route_for_issue(_issue("packet-drift", "error", "packet_digest")), "audit_ops")

    def test_route_for_retention_link_issue(self) -> None:
        self.assertEqual(evidence_status.route_for_issue(_issue("retention-gap", "warn", "retention_link")), "treasury_ops")

    def test_route_for_history_import_issue(self) -> None:
        self.assertEqual(evidence_status.route_for_issue(_issue("stale-history", "warn", "history_import.started_at")), "reporting_ops")

    def test_route_for_owner_dashboard_issue(self) -> None:
        self.assertEqual(evidence_status.route_for_issue(_issue("dashboard-gap", "warn", "owner_dashboard.blocked")), "support_ops")

    def test_route_for_unknown_prefix_defaults_to_support_ops(self) -> None:
        self.assertEqual(evidence_status.route_for_issue(_issue("oddity", "warn", "mystery.path")), "support_ops")

    def test_owner_summary_counts_routed_owners(self) -> None:
        summary = evidence_status.owner_summary(
            [_issue("missing-field", "error", "bundle.owner"), _issue("missing-path", "error", "artifact_paths.bundle")]
        )
        self.assertEqual(summary, {"content_ops": 1, "risk_ops": 1})

    def test_owner_summary_sorts_keys(self) -> None:
        summary = evidence_status.owner_summary(
            [_issue("dashboard-gap", "warn", "owner_dashboard.blocked"), _issue("missing-field", "error", "bundle.owner")]
        )
        self.assertEqual(list(summary), ["content_ops", "support_ops"])

    def test_severity_summary_counts_all_levels(self) -> None:
        summary = evidence_status.severity_summary(
            [_issue("one", "warn", "bundle.owner"), _issue("two", "error", "run.started_at"), _issue("three", "warn", "scorecard.percent")]
        )
        self.assertEqual(summary, {"error": 1, "warn": 2})

    def test_owner_digest_counts_issues_per_owner(self) -> None:
        digest = evidence_status.owner_digest(
            [_issue("missing-field", "error", "bundle.owner"), _issue("missing-other", "warn", "bundle.title")]
        )
        self.assertEqual(digest["content_ops"]["count"], 2)

    def test_owner_digest_sorts_codes(self) -> None:
        digest = evidence_status.owner_digest(
            [_issue("zeta", "warn", "bundle.owner"), _issue("alpha", "warn", "bundle.title")]
        )
        self.assertEqual(digest["content_ops"]["codes"], ["alpha", "zeta"])

    def test_owner_digest_sorts_paths(self) -> None:
        digest = evidence_status.owner_digest(
            [_issue("a", "warn", "bundle.title"), _issue("b", "warn", "bundle.owner")]
        )
        self.assertEqual(digest["content_ops"]["paths"], ["bundle.owner", "bundle.title"])

    def test_owner_digest_ignores_empty_paths(self) -> None:
        digest = evidence_status.owner_digest([ValidationIssue("missing", "warn", "msg", "")])
        self.assertEqual(digest["support_ops"]["paths"], [])

    def test_status_payload_contains_severity_summary(self) -> None:
        payload = evidence_status.status_payload([_issue("missing-field", "error", "bundle.owner")])
        self.assertEqual(payload["severity_summary"], {"error": 1})

    def test_status_payload_contains_owner_digest(self) -> None:
        payload = evidence_status.status_payload([_issue("missing-field", "error", "bundle.owner")])
        self.assertIn("content_ops", payload["owner_digest"])

    def test_notification_lines_include_owner_counts(self) -> None:
        lines = evidence_status.notification_lines([_issue("missing-field", "error", "bundle.owner")])
        self.assertIn("content_ops: 1 issue(s)", lines)

    def test_notification_lines_include_severity_guidance(self) -> None:
        lines = evidence_status.notification_lines([_issue("missing-field", "error", "bundle.owner")])
        self.assertTrue(any(line.startswith("error: ") for line in lines))

    def test_notification_lines_skip_severity_lines_when_empty(self) -> None:
        lines = evidence_status.notification_lines([])
        self.assertEqual(len(lines), 2)

    def test_owner_action_cards_include_known_owner_actions(self) -> None:
        cards = evidence_status.owner_action_cards([_issue("missing-field", "error", "bundle.owner")])
        self.assertIn("primary_action", cards["content_ops"])

    def test_owner_action_cards_include_support_route_for_unknown_issue(self) -> None:
        cards = evidence_status.owner_action_cards([_issue("oddity", "warn", "mystery.path")])
        self.assertIn("primary_action", cards["support_ops"])

    def test_remediation_summary_contains_primary_and_escalation_text(self) -> None:
        summary = evidence_status.remediation_summary([_issue("missing-field", "error", "bundle.owner")])
        self.assertIn("primary action", summary["content_ops"].lower())

    def test_remediation_summary_is_empty_without_issues(self) -> None:
        self.assertEqual(evidence_status.remediation_summary([]), {})

    def test_render_status_brief_has_header(self) -> None:
        text = evidence_status.render_status_brief([])
        self.assertTrue(text.startswith("# Audit packet status brief"))

    def test_render_status_brief_includes_severity_summary_when_present(self) -> None:
        text = evidence_status.render_status_brief([_issue("missing-field", "error", "bundle.owner")])
        self.assertIn("severity summary", text)

    def test_render_status_brief_includes_owner_codes(self) -> None:
        text = evidence_status.render_status_brief([_issue("missing-field", "error", "bundle.owner")])
        self.assertIn("codes: missing-field", text)

    def test_render_status_brief_includes_owner_paths(self) -> None:
        text = evidence_status.render_status_brief([_issue("missing-field", "error", "bundle.owner")])
        self.assertIn("paths: bundle.owner", text)

    def test_render_status_brief_includes_primary_action(self) -> None:
        text = evidence_status.render_status_brief([_issue("missing-field", "error", "bundle.owner")])
        self.assertIn("primary action", text)

    def test_render_status_brief_lists_multiple_owners(self) -> None:
        text = evidence_status.render_status_brief(
            [_issue("missing-field", "error", "bundle.owner"), _issue("missing-path", "error", "artifact_paths.bundle")]
        )
        self.assertIn("- content_ops: 1 issue(s)", text)
        self.assertIn("- risk_ops: 1 issue(s)", text)
