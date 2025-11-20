from __future__ import annotations

import unittest
from pathlib import Path

from pixelforge_ops import jobs
from tests.helpers import FIXTURES, attempt


class JobTests(unittest.TestCase):
    def test_batch_validate_returns_all_bundles(self) -> None:
        result = jobs.batch_validate(FIXTURES / "catalog")
        self.assertEqual(len(result), 12)

    def test_batch_score_returns_named_entries(self) -> None:
        root = FIXTURES / "catalog"
        payloads = {
            root / "jpeg-codec-fidelity": attempt("jpeg-codec-fidelity", "mixed"),
            root / "raster-transform-tiling": attempt("raster-transform-tiling", "strong"),
        }
        result = jobs.batch_score(payloads)
        self.assertEqual(len(result), 2)

    def test_build_release_returns_manifest_and_validation(self) -> None:
        root = FIXTURES / "catalog"
        result = jobs.build_release(root, [root / "jpeg-codec-fidelity", root / "raster-transform-tiling"], "release-jobs")
        self.assertIn("manifest", result)
        self.assertIn("validation", result)


