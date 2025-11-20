from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pixelforge_ops import catalog, storage
from pixelforge_ops.execution import evaluate_attempt
from pixelforge_ops.scoring import score_run
from tests.helpers import attempt, bundle


class StorageTests(unittest.TestCase):
    def test_record_bundle_and_run_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "workbench.sqlite3"
            item = bundle("jpeg-codec-fidelity")
            storage.record_bundle(db_path, item, catalog.bundle_summary(item))
            run = evaluate_attempt(item, attempt("jpeg-codec-fidelity", "mixed"))
            card = score_run(run, item)
            storage.record_run(db_path, run, card)
            self.assertTrue(storage.recent_runs(db_path))

    def test_owner_rollup_counts_inserted_bundles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "workbench.sqlite3"
            first = bundle("jpeg-codec-fidelity")
            second = bundle("raster-transform-tiling")
            storage.record_bundle(db_path, first, catalog.bundle_summary(first))
            storage.record_bundle(db_path, second, catalog.bundle_summary(second))
            owners = storage.owner_rollup(db_path)
            self.assertIn("codec_ops", owners)


