from __future__ import annotations

import unittest

from engineering_challenge.cataloging import case_index, loader, lineage
from tests.ext_helpers import FIXTURES, bundle


class CatalogLoaderIndexTests(unittest.TestCase):
    def test_load_bundle_with_policy_exposes_weights(self) -> None:
        payload = loader.load_bundle_with_policy(FIXTURES / "catalog" / "merchant-closeout")
        self.assertIn("section_weights", payload)

    def test_load_corpus_with_policy_matches_bundle_count(self) -> None:
        payload = loader.load_corpus_with_policy(FIXTURES / "catalog")
        self.assertEqual(len(payload), 12)

    def test_bundles_for_owner_returns_expected_bundle(self) -> None:
        names = loader.bundles_for_owner(FIXTURES / "catalog", "finance_ops")
        self.assertIn("merchant-closeout", names)

    def test_case_budget_covers_fixture_bundle(self) -> None:
        budgets = loader.case_budget(FIXTURES / "catalog")
        self.assertEqual(budgets["merchant-closeout"], 24)

    def test_comparator_mix_contains_exact(self) -> None:
        mix = loader.comparator_mix(FIXTURES / "catalog")
        self.assertIn("exact", mix)

    def test_by_section_indexes_case_ids(self) -> None:
        rows = case_index.by_section(bundle("merchant-closeout"))
        self.assertIn("catalog", rows)

    def test_by_difficulty_indexes_case_ids(self) -> None:
        rows = case_index.by_difficulty(bundle("merchant-closeout"))
        self.assertIn("intro", rows)

    def test_hidden_case_ids_returns_only_hidden_cases(self) -> None:
        rows = case_index.hidden_case_ids(bundle("merchant-closeout"))
        self.assertTrue(rows)

    def test_searchable_rows_match_case_count(self) -> None:
        rows = case_index.searchable_rows(bundle("merchant-closeout"))
        self.assertEqual(len(rows), 24)

    def test_tag_counts_aggregate_fixture_tags(self) -> None:
        counts = case_index.tag_counts(bundle("merchant-closeout"))
        self.assertIn("catalog", counts)

    def test_filter_cases_can_select_public_rows(self) -> None:
        rows = case_index.filter_cases(bundle("merchant-closeout"), hidden=False)
        self.assertTrue(rows)

    def test_lineage_rows_cover_loaded_bundles(self) -> None:
        rows = lineage.lineage_rows([bundle("merchant-closeout"), bundle("warehouse-routing")])
        self.assertEqual(len(rows), 2)

    def test_owner_lineage_groups_bundles(self) -> None:
        rows = lineage.owner_lineage([bundle("merchant-closeout"), bundle("warehouse-routing")])
        self.assertIn("finance_ops", rows)

    def test_version_train_groups_versions(self) -> None:
        rows = lineage.version_train([bundle("merchant-closeout"), bundle("warehouse-routing")])
        self.assertIn("2026.06", rows)

    def test_supersedes_map_handles_sorted_bundles(self) -> None:
        mapping = lineage.supersedes_map([bundle("merchant-closeout"), bundle("warehouse-routing")])
        self.assertIsInstance(mapping, dict)
