from __future__ import annotations

import unittest

from engineering_challenge.scoring_model import band_matrix


class BandMatrixTests(unittest.TestCase):
    def test_band_for_percent_ready(self) -> None:
        self.assertEqual(band_matrix.band_for_percent(95.0), "ready")

    def test_band_for_percent_watch(self) -> None:
        self.assertEqual(band_matrix.band_for_percent(75.0), "watch")

    def test_band_for_percent_risk(self) -> None:
        self.assertEqual(band_matrix.band_for_percent(58.0), "risk")

    def test_band_for_percent_blocked(self) -> None:
        self.assertEqual(band_matrix.band_for_percent(40.0), "blocked")

    def test_band_route_returns_queue(self) -> None:
        self.assertEqual(band_matrix.band_route("watch"), "ops-review")

    def test_section_weights_for_owner_returns_catalog_entry(self) -> None:
        weights = band_matrix.section_weights_for_owner("finance_ops")
        self.assertIn("catalog", weights)

    def test_difficulty_target_returns_floor(self) -> None:
        target = band_matrix.difficulty_target("advanced")
        self.assertIn("floor", target)

    def test_flag_definition_returns_route(self) -> None:
        flag = band_matrix.flag_definition("hidden-case-regression")
        self.assertEqual(flag["route"], "authoring")
