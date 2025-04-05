from __future__ import annotations

import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from engineering_challenge.persistence import dashboard, history_ingest, migrations, query_catalog, query_service, snapshots
from tests.ext_helpers import history_rows


class PersistenceModuleTests(unittest.TestCase):
    def test_migration_sql_contains_history_table(self) -> None:
        sql = migrations.migration_sql()
        self.assertTrue(any("history_import" in item for item in sql))

    def test_latest_version_is_four(self) -> None:
        self.assertEqual(migrations.latest_version(), 4)

    def test_load_rows_reads_fixture_file(self) -> None:
        rows = history_rows(1)
        self.assertEqual(len(rows), 2400)

    def test_monthly_rollup_averages_percent(self) -> None:
        summary = history_ingest.monthly_rollup(history_rows(1))
        self.assertEqual(summary["count"], 2400)

    def test_saved_queries_return_rows(self) -> None:
        self.assertTrue(query_catalog.saved_queries())

    def test_query_by_id_returns_title(self) -> None:
        query = query_catalog.query_by_id("owner-rollup-01")
        self.assertIn("title", query)

    def test_materialized_views_return_rows(self) -> None:
        self.assertTrue(query_catalog.materialized_views())

    def test_history_snapshot_tables_exist(self) -> None:
        path = Path(__file__).resolve().parent / "fixtures" / "sqlite_snapshots" / "ops_history_2026_q1.sqlite3"
        tables = snapshots.snapshot_tables(path)
        self.assertIn("history_import", tables)

    def test_history_row_count_is_positive(self) -> None:
        path = Path(__file__).resolve().parent / "fixtures" / "sqlite_snapshots" / "ops_history_2026_q1.sqlite3"
        self.assertGreater(snapshots.history_row_count(path), 0)

    def test_owner_mix_reports_owners(self) -> None:
        path = Path(__file__).resolve().parent / "fixtures" / "sqlite_snapshots" / "ops_history_2026_q1.sqlite3"
        mix = snapshots.owner_mix(path)
        self.assertIn("finance_ops", mix)

    def test_query_service_recent_history_returns_rows(self) -> None:
        path = Path(__file__).resolve().parent / "fixtures" / "sqlite_snapshots" / "ops_history_2026_q1.sqlite3"
        self.assertTrue(query_service.recent_history(path, 5))

    def test_query_service_band_counts_return_mapping(self) -> None:
        path = Path(__file__).resolve().parent / "fixtures" / "sqlite_snapshots" / "ops_history_2026_q1.sqlite3"
        counts = query_service.band_counts(path)
        self.assertIn("ready", counts)

    def test_query_service_owner_average_returns_mapping(self) -> None:
        path = Path(__file__).resolve().parent / "fixtures" / "sqlite_snapshots" / "ops_history_2026_q1.sqlite3"
        averages = query_service.owner_average(path)
        self.assertIn("finance_ops", averages)

    def test_dashboard_payload_contains_bands(self) -> None:
        path = Path(__file__).resolve().parent / "fixtures" / "sqlite_snapshots" / "ops_history_2026_q1.sqlite3"
        payload = dashboard.dashboard_payload(path)
        self.assertIn("bands", payload)

    def test_at_risk_owners_returns_list(self) -> None:
        path = Path(__file__).resolve().parent / "fixtures" / "sqlite_snapshots" / "ops_history_2026_q1.sqlite3"
        owners = dashboard.at_risk_owners(path, floor=90.0)
        self.assertIsInstance(owners, list)

    def test_insert_rows_can_populate_temp_db(self) -> None:
        rows = history_rows(1)[:20]
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "temp.sqlite3"
            with closing(sqlite3.connect(db)) as conn:
                conn.executescript(
                    "create table history_import (history_id text primary key, bundle_id text not null, owner text not null, percent real not null, hidden_percent real not null, band text not null, started_at text not null, payload_json text not null);"
                )
                history_ingest.insert_rows(conn, rows)
                count = conn.execute("select count(*) from history_import").fetchone()[0]
            self.assertEqual(count, 20)
