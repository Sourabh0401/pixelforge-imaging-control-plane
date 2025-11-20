from __future__ import annotations

import unittest

from pixelforge_ops.scoring_model import threshold_catalog


class ThresholdCatalogTests(unittest.TestCase):
    def test_thresholds_for_owner_return_sections(self) -> None:
        rows = threshold_catalog.thresholds_for_owner("codec_ops")
        self.assertIn("catalog", rows)

    def test_section_threshold_returns_floor(self) -> None:
        row = threshold_catalog.section_threshold("codec_ops", "catalog")
        self.assertIn("floor", row)

    def test_section_threshold_values_are_ordered(self) -> None:
        row = threshold_catalog.section_threshold("codec_ops", "catalog")
        self.assertLessEqual(row["floor"], row["target"])


