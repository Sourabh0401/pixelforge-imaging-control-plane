from __future__ import annotations

import unittest
from pathlib import Path

from engineering_challenge import jobs
from tests.helpers import FIXTURES, attempt


class JobTests(unittest.TestCase):
    def test_batch_validate_returns_all_bundles(self) -> None:
        result = jobs.batch_validate(FIXTURES / "catalog")
        self.assertEqual(len(result), 12)

    def test_batch_score_returns_named_entries(self) -> None:
        root = FIXTURES / "catalog"
        payloads = {
            root / "merchant-closeout": attempt("merchant-closeout", "mixed"),
            root / "warehouse-routing": attempt("warehouse-routing", "strong"),
        }
        result = jobs.batch_score(payloads)
        self.assertEqual(len(result), 2)

    def test_build_release_returns_manifest_and_validation(self) -> None:
        root = FIXTURES / "catalog"
        result = jobs.build_release(root, [root / "merchant-closeout", root / "warehouse-routing"], "release-jobs")
        self.assertIn("manifest", result)
        self.assertIn("validation", result)
