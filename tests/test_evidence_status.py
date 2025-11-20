from __future__ import annotations

import unittest

from pixelforge_ops.auditpack.evidence_status import notification_lines, owner_summary, status_payload
from pixelforge_ops.auditpack.evidence_validator import ValidationIssue


class EvidenceStatusTests(unittest.TestCase):
    def test_status_payload_is_green_without_issues(self) -> None:
        payload = status_payload([])
        self.assertEqual(payload["status"], "green")

    def test_owner_summary_groups_issue_routes(self) -> None:
        issues = [ValidationIssue("missing-field", "error", "x", "bundle.field_04")]
        summary = owner_summary(issues)
        self.assertIn("metadata_ops", summary)

    def test_notification_lines_include_status(self) -> None:
        issues = [ValidationIssue("unexpected-path", "warn", "x", "artifact_paths.extra")]
        lines = notification_lines(issues)
        self.assertTrue(lines[0].startswith("audit packet status"))


