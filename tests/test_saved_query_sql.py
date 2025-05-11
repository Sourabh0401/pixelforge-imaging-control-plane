from __future__ import annotations

import unittest

from engineering_challenge.persistence import saved_query_sql


class SavedQuerySqlTests(unittest.TestCase):
    def test_queries_return_many_specs(self) -> None:
        self.assertGreaterEqual(len(saved_query_sql.queries()), 10)

    def test_query_spec_returns_sql(self) -> None:
        spec = saved_query_sql.query_spec("owner-trend-rollup")
        self.assertIn("select", spec["sql"].lower())

    def test_parameter_names_are_exposed(self) -> None:
        params = saved_query_sql.parameter_names("hidden-gap-watchlist")
        self.assertIn("gap_floor", params)

    def test_queries_for_owner_filters_catalog(self) -> None:
        rows = saved_query_sql.queries_for_owner("risk_ops")
        self.assertTrue(rows)

    def test_markdown_catalog_has_heading(self) -> None:
        self.assertIn("# Saved query catalog", saved_query_sql.markdown_catalog())
