from __future__ import annotations

import unittest

from pixelforge_ops.reporting_surfaces import narrative_catalog


class NarrativeCatalogTests(unittest.TestCase):
    def test_band_narrative_returns_text(self) -> None:
        self.assertTrue(narrative_catalog.band_narrative("ready"))

    def test_flag_narrative_returns_text(self) -> None:
        self.assertTrue(narrative_catalog.flag_narrative("requires-review"))

    def test_section_narrative_returns_text(self) -> None:
        self.assertTrue(narrative_catalog.section_narrative("catalog"))


