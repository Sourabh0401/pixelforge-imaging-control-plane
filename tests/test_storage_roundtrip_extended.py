from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from engineering_challenge import catalog, release, storage
from engineering_challenge.execution import evaluate_attempt
from engineering_challenge.scoring import score_run
from tests.ext_helpers import attempt, bundle


class StorageRoundTripExtendedTests(unittest.TestCase):
    def _db_path(self, tmp: str) -> Path:
        return Path(tmp) / "runtime" / "engineering_challenge.sqlite3"

    def _run_and_score(self, bundle_name: str, mode: str = "mixed"):
        item = bundle(bundle_name)
        run = evaluate_attempt(item, attempt(bundle_name, mode))
        card = score_run(run, item)
        return item, run, card

    def test_initialize_creates_bundle_summary_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            storage.initialize(path)
            with closing(storage.connect(path)) as conn:
                tables = {row[0] for row in conn.execute("select name from sqlite_master where type='table'")}
        self.assertIn("bundle_summary", tables)

    def test_initialize_creates_submission_run_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            storage.initialize(path)
            with closing(storage.connect(path)) as conn:
                tables = {row[0] for row in conn.execute("select name from sqlite_master where type='table'")}
        self.assertIn("submission_run", tables)

    def test_initialize_creates_release_manifest_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            storage.initialize(path)
            with closing(storage.connect(path)) as conn:
                tables = {row[0] for row in conn.execute("select name from sqlite_master where type='table'")}
        self.assertIn("release_manifest", tables)

    def test_initialize_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            storage.initialize(path)
            storage.initialize(path)
            with closing(storage.connect(path)) as conn:
                count = conn.execute("select count(*) from sqlite_master where type='table' and name='bundle_summary'").fetchone()[0]
        self.assertEqual(count, 1)

    def test_connect_creates_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            with closing(storage.connect(path)):
                pass
            self.assertTrue(path.parent.exists())

    def test_recent_runs_is_empty_for_new_db(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            self.assertEqual(storage.recent_runs(path), [])

    def test_owner_rollup_is_empty_for_new_db(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            self.assertEqual(storage.owner_rollup(path), {})

    def test_record_bundle_persists_owner_rollup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            item = bundle("merchant-closeout")
            storage.record_bundle(path, item, catalog.bundle_summary(item))
            self.assertEqual(storage.owner_rollup(path), {"finance_ops": 1})

    def test_record_bundle_replaces_existing_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            item = bundle("merchant-closeout")
            storage.record_bundle(path, item, {"status": "old"})
            storage.record_bundle(path, item, {"status": "new"})
            with closing(storage.connect(path)) as conn:
                stored = conn.execute("select summary_json from bundle_summary where bundle_id=?", (item.bundle_id,)).fetchone()[0]
        self.assertEqual(json.loads(stored)["status"], "new")

    def test_record_bundle_can_store_multiple_owners(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            first = bundle("merchant-closeout")
            second = bundle("warehouse-routing")
            storage.record_bundle(path, first, catalog.bundle_summary(first))
            storage.record_bundle(path, second, catalog.bundle_summary(second))
            rollup = storage.owner_rollup(path)
        self.assertEqual(rollup["finance_ops"], 1)
        self.assertEqual(rollup["logistics_ops"], 1)

    def test_record_run_persists_recent_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            _, run, card = self._run_and_score("merchant-closeout")
            storage.record_run(path, run, card)
            rows = storage.recent_runs(path)
        self.assertEqual(rows[0]["run_id"], run.run_id)

    def test_record_run_replaces_existing_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            _, run, card = self._run_and_score("merchant-closeout")
            storage.record_run(path, run, card)
            storage.record_run(path, run, card)
            with closing(storage.connect(path)) as conn:
                count = conn.execute("select count(*) from submission_run").fetchone()[0]
        self.assertEqual(count, 1)

    def test_record_run_stores_scorecard_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            _, run, card = self._run_and_score("merchant-closeout")
            storage.record_run(path, run, card)
            with closing(storage.connect(path)) as conn:
                scorecard_json = conn.execute("select scorecard_json from submission_run where run_id=?", (run.run_id,)).fetchone()[0]
        self.assertEqual(json.loads(scorecard_json)["bundle_id"], "merchant-closeout")

    def test_record_run_stores_notes_in_run_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            _, run, card = self._run_and_score("merchant-closeout")
            storage.record_run(path, run, card)
            with closing(storage.connect(path)) as conn:
                run_json = conn.execute("select run_json from submission_run where run_id=?", (run.run_id,)).fetchone()[0]
        self.assertIn("notes", json.loads(run_json))

    def test_recent_runs_honors_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            for bundle_name in ("merchant-closeout", "warehouse-routing"):
                _, run, card = self._run_and_score(bundle_name)
                storage.record_run(path, run, card)
            self.assertEqual(len(storage.recent_runs(path, limit=1)), 1)

    def test_recent_runs_orders_newest_first(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            for bundle_name in ("merchant-closeout", "warehouse-routing"):
                _, run, card = self._run_and_score(bundle_name)
                storage.record_run(path, run, card)
            rows = storage.recent_runs(path, limit=2)
        self.assertEqual(rows[0]["bundle_id"], "warehouse-routing")

    def test_record_run_keeps_participant_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            _, run, card = self._run_and_score("merchant-closeout")
            storage.record_run(path, run, card)
            rows = storage.recent_runs(path)
        self.assertEqual(rows[0]["participant_id"], run.participant_id)

    def test_record_release_persists_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            manifest = release.build_release_manifest("release-1", [bundle("merchant-closeout")], notes=("ops-ready",))
            storage.record_release(path, manifest)
            with closing(storage.connect(path)) as conn:
                stored = conn.execute("select manifest_json from release_manifest where release_id='release-1'").fetchone()[0]
        self.assertEqual(json.loads(stored)["release_id"], "release-1")

    def test_record_release_replaces_existing_release(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._db_path(tmp)
            first = release.build_release_manifest("release-1", [bundle("merchant-closeout")], notes=("old",))
            second = release.build_release_manifest("release-1", [bundle("merchant-closeout")], notes=("new",))
            storage.record_release(path, first)
            storage.record_release(path, second)
            with closing(storage.connect(path)) as conn:
                stored = conn.execute("select manifest_json from release_manifest where release_id='release-1'").fetchone()[0]
        self.assertEqual(json.loads(stored)["notes"], ["new"])
