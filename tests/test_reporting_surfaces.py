from __future__ import annotations

import unittest

from engineering_challenge.reporting_surfaces import owner_dashboard, portfolio_rollup, release_notes, risk_report, template_catalog
from engineering_challenge.release import build_release_manifest
from tests.ext_helpers import bundle, scorecard


class ReportingSurfaceTests(unittest.TestCase):
    def test_owner_panel_returns_row(self) -> None:
        panel = template_catalog.owner_panel("finance_ops")
        self.assertIn("headline", panel)

    def test_content_blocks_return_rows(self) -> None:
        self.assertTrue(template_catalog.content_blocks())

    def test_block_for_section_matches_section(self) -> None:
        block = template_catalog.block_for_section("catalog")
        self.assertEqual(block["block_id"], "block-catalog")

    def test_owner_dashboard_contains_metrics(self) -> None:
        payload = owner_dashboard.owner_dashboard("finance_ops", {"average_percent": 82.0})
        self.assertIn("metrics", payload)

    def test_owner_dashboard_markdown_renders_callouts(self) -> None:
        text = owner_dashboard.owner_dashboard_markdown("finance_ops", {"average_percent": 82.0})
        self.assertIn("Callouts", text)

    def test_rollup_groups_scorecards(self) -> None:
        cards = [scorecard("merchant-closeout", "mixed"), scorecard("warehouse-routing", "mixed")]
        payload = portfolio_rollup.rollup(cards)
        self.assertEqual(payload["count"], 2)

    def test_csv_rows_emit_simple_rows(self) -> None:
        rows = portfolio_rollup.csv_rows([scorecard("merchant-closeout", "mixed")])
        self.assertEqual(rows[0]["bundle_id"], "merchant-closeout")

    def test_risk_rows_include_problem_cards(self) -> None:
        rows = risk_report.risk_rows([scorecard("claims-intake", "weak")])
        self.assertTrue(rows)

    def test_release_notes_render_bundle_rows(self) -> None:
        manifest = build_release_manifest("release-report", [bundle("merchant-closeout")], created_at="2026-06-03T10:00:00Z")
        text = release_notes.release_notes(manifest, [scorecard("merchant-closeout", "mixed")])
        self.assertIn("Release notes", text)
