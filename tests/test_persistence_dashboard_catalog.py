from __future__ import annotations

import unittest

from pixelforge_ops.persistence import dashboard_catalog


class DashboardCatalogTests(unittest.TestCase):
    def test_widgets_return_rows(self) -> None:
        self.assertTrue(dashboard_catalog.widgets())

    def test_widget_for_owner_returns_headline(self) -> None:
        widget = dashboard_catalog.widget_for_owner("codec_ops")
        self.assertIn("table_columns", widget)


