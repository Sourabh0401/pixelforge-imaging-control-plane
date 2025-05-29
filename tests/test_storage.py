from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from engineering_challenge import catalog, storage
from engineering_challenge.execution import evaluate_attempt
from engineering_challenge.scoring import score_run
from tests.helpers import attempt, bundle


class StorageTests(unittest.TestCase):
    def test_record_bundle_and_run_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "workbench.sqlite3"
            item = bundle("merchant-closeout")
            storage.record_bundle(db_path, item, catalog.bundle_summary(item))
            run = evaluate_attempt(item, attempt("merchant-closeout", "mixed"))
            card = score_run(run, item)
            storage.record_run(db_path, run, card)
            self.assertTrue(storage.recent_runs(db_path))

    def test_owner_rollup_counts_inserted_bundles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "workbench.sqlite3"
            first = bundle("merchant-closeout")
            second = bundle("warehouse-routing")
            storage.record_bundle(db_path, first, catalog.bundle_summary(first))
            storage.record_bundle(db_path, second, catalog.bundle_summary(second))
            owners = storage.owner_rollup(db_path)
            self.assertIn("finance_ops", owners)
