from __future__ import annotations

import unittest

from engineering_challenge.reporting_surfaces import dashboard_blueprints


class DashboardBlueprintTests(unittest.TestCase):
    def test_blueprint_has_primary_panels(self) -> None:
        item = dashboard_blueprints.blueprint("finance_ops")
        self.assertIn("primary_panels", item)

    def test_primary_panels_return_rows(self) -> None:
        self.assertTrue(dashboard_blueprints.primary_panels("risk_ops"))

    def test_render_markdown_has_heading(self) -> None:
        text = dashboard_blueprints.render_markdown("support_ops")
        self.assertIn("# ", text)

    def test_digest_is_stable(self) -> None:
        self.assertEqual(
            dashboard_blueprints.digest("treasury_ops"),
            dashboard_blueprints.digest("treasury_ops"),
        )
