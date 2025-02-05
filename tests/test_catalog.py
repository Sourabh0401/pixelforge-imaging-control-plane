from __future__ import annotations

import unittest
from pathlib import Path

from engineering_challenge import catalog
from tests.helpers import FIXTURES, bundle


class CatalogTests(unittest.TestCase):
    def test_load_bundle_reads_manifest_and_cases(self) -> None:
        item = bundle("merchant-closeout")
        self.assertEqual(item.bundle_id, "merchant-closeout")
        self.assertEqual(len(item.cases), 24)
        self.assertGreater(len(item.hidden_cases()), 0)

    def test_corpus_summary_counts_all_fixture_bundles(self) -> None:
        summary = catalog.corpus_summary(FIXTURES / "catalog")
        self.assertEqual(summary["bundle_count"], 12)
        self.assertEqual(len(summary["bundle_ids"]), 12)

    def test_duplicate_case_ids_empty_for_fixture_bundle(self) -> None:
        self.assertEqual(catalog.duplicate_case_ids(bundle("warehouse-routing")), ())

    def test_section_matrix_contains_expected_sections(self) -> None:
        bundles = [bundle("merchant-closeout"), bundle("warehouse-routing"), bundle("claims-intake")]
        matrix = catalog.section_matrix(bundles)
        self.assertIn("execution", matrix)
        self.assertIn("merchant-closeout", matrix["execution"])

    def test_owner_token_normalization(self) -> None:
        token = catalog.normalized_owner_token(bundle("claims-intake"))
        self.assertEqual(token, "support-ops")
