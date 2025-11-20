from __future__ import annotations

import unittest

from pixelforge_ops.reporting_surfaces import legend


class ReportingLegendTests(unittest.TestCase):
    def test_legend_rows_exist(self) -> None:
        self.assertTrue(legend.legend())

    def test_description_returns_text(self) -> None:
        self.assertTrue(legend.description("ready"))

    def test_label_returns_text(self) -> None:
        self.assertEqual(legend.label("blocked"), "Blocked")


