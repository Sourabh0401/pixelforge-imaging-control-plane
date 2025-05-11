from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from engineering_challenge.persistence import schema_diff


class SchemaDiffTests(unittest.TestCase):
    def test_same_snapshot_has_no_breaking_changes(self) -> None:
        path = Path(__file__).resolve().parent / "fixtures" / "sqlite_snapshots" / "ops_history_2026_q1.sqlite3"
        diffs = schema_diff.compare_snapshots(path, path)
        self.assertEqual(schema_diff.breaking_changes(diffs), [])

    def test_required_tables_missing_detects_absent_tables(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "empty.sqlite3"
            sqlite3.connect(db).close()
            self.assertIn("history_import", schema_diff.required_tables_missing(db))

    def test_compare_snapshots_detects_type_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            left = Path(tmp) / "left.sqlite3"
            right = Path(tmp) / "right.sqlite3"
            conn = sqlite3.connect(left)
            conn.execute("create table history_import (history_id text primary key, percent real)")
            conn.close()
            conn = sqlite3.connect(right)
            conn.execute("create table history_import (history_id text primary key, percent text)")
            conn.close()
            diffs = schema_diff.compare_snapshots(left, right)
            self.assertTrue(schema_diff.breaking_changes(diffs))

    def test_render_report_mentions_changed_table(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            left = Path(tmp) / "left.sqlite3"
            right = Path(tmp) / "right.sqlite3"
            conn = sqlite3.connect(left)
            conn.execute("create table history_import (history_id text primary key, percent real)")
            conn.close()
            conn = sqlite3.connect(right)
            conn.execute("create table history_import (history_id text primary key, percent text)")
            conn.close()
            report = schema_diff.render_report(left, right)
            self.assertIn("history_import", report)
