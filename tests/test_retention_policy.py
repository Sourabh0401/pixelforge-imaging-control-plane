from __future__ import annotations

from datetime import date
import unittest

from pixelforge_ops.persistence import retention_policy
from tests.ext_helpers import history_rows


class RetentionPolicyTests(unittest.TestCase):
    def test_rule_for_internal_history_requires_export(self) -> None:
        rule = retention_policy.rule_for("internal", "run-history")
        self.assertTrue(rule.requires_export)

    def test_plan_action_can_mark_row_active(self) -> None:
        row = history_rows(1)[0]
        action = retention_policy.plan_action(row, date(2026, 1, 5), has_export=False)
        self.assertEqual(action.action, "keep")

    def test_plan_action_can_mark_row_prunable(self) -> None:
        row = history_rows(1)[0]
        action = retention_policy.plan_action(row, date(2026, 4, 10), has_export=True)
        self.assertIn(action.action, {"archive", "prune", "review", "keep"})

    def test_channel_matrix_contains_partner_rules(self) -> None:
        matrix = retention_policy.channel_matrix()
        self.assertIn("partner", matrix)

    def test_action_summary_groups_actions(self) -> None:
        rows = history_rows(1)[:5]
        actions = retention_policy.plan_actions(rows, date(2026, 4, 10), {row["history_id"] for row in rows})
        self.assertTrue(retention_policy.action_summary(actions))

    def test_render_summary_returns_markdown(self) -> None:
        rows = history_rows(1)[:5]
        actions = retention_policy.plan_actions(rows, date(2026, 4, 10), {row["history_id"] for row in rows})
        self.assertIn("# Retention summary", retention_policy.render_summary(actions))


