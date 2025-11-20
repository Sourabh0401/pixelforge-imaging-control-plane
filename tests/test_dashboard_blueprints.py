from __future__ import annotations

import unittest

from pixelforge_ops.reporting_surfaces import dashboard_blueprints


class DashboardBlueprintTests(unittest.TestCase):
    def test_blueprint_has_primary_panels(self) -> None:
        item = dashboard_blueprints.blueprint("codec_ops")
        self.assertIn("primary_panels", item)

    def test_primary_panels_return_rows(self) -> None:
        self.assertTrue(dashboard_blueprints.primary_panels("image_quality_ops"))

    def test_render_markdown_has_heading(self) -> None:
        text = dashboard_blueprints.render_markdown("partner_ops")
        self.assertIn("# ", text)

    def test_digest_is_stable(self) -> None:
        self.assertEqual(
            dashboard_blueprints.digest("archive_ops"),
            dashboard_blueprints.digest("archive_ops"),
        )


