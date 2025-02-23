from __future__ import annotations

import unittest

from engineering_challenge.reporting_surfaces import column_catalog


class ColumnCatalogTests(unittest.TestCase):
    def test_columns_for_surface_returns_rows(self) -> None:
        rows = column_catalog.columns_for_surface("portfolio")
        self.assertTrue(rows)

    def test_required_columns_include_bundle_id(self) -> None:
        self.assertIn("bundle_id", column_catalog.required_columns("portfolio"))

    def test_display_labels_returns_mapping(self) -> None:
        labels = column_catalog.display_labels("owner_dashboard")
        self.assertIn("average_percent", labels)
