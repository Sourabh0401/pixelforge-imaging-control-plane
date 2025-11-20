from __future__ import annotations

import unittest

from pixelforge_ops.execution import evaluate_attempt
from pixelforge_ops.reporting_surfaces import portfolio_rollup
from pixelforge_ops.scoring import score_run
from tests.ext_helpers import attempt, bundle


def _cards() -> list:
    cards = []
    for name in ("jpeg-codec-fidelity", "raster-transform-tiling", "metadata-exif-ingest"):
        item = bundle(name)
        cards.append(score_run(evaluate_attempt(item, attempt(name, "mixed")), item))
    return cards


class ReportingPortfolioRollupTests(unittest.TestCase):
    def test_rollup_includes_average_gap(self) -> None:
        payload = portfolio_rollup.rollup(_cards())
        self.assertIn("average_gap", payload)

    def test_watch_owners_returns_list(self) -> None:
        owners = portfolio_rollup.watch_owners(_cards(), floor=90.0)
        self.assertIsInstance(owners, list)

    def test_public_hidden_gap_summary_has_bounds(self) -> None:
        summary = portfolio_rollup.public_hidden_gap_summary(_cards())
        self.assertIn("max", summary)

    def test_section_average_reports_sections(self) -> None:
        summary = portfolio_rollup.section_average(_cards())
        self.assertIn("validation", summary)

    def test_owner_risk_register_groups_by_owner(self) -> None:
        rows = portfolio_rollup.owner_risk_register(_cards())
        self.assertTrue(rows)
        self.assertIn("owner", rows[0])

    def test_markdown_summary_has_heading(self) -> None:
        self.assertIn("# Portfolio rollup", portfolio_rollup.markdown_summary(_cards()))


