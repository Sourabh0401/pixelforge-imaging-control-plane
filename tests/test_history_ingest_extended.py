from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from engineering_challenge.persistence import history_ingest


def _row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "history_id": "hist-001",
        "bundle_id": "merchant-closeout",
        "owner": "finance_ops",
        "percent": 91.5,
        "hidden_percent": 87.2,
        "band": "ready",
        "started_at": "2026-01-05T09:00:00Z",
        "worker_version": "worker-1.2",
    }
    row.update(overrides)
    return row


class HistoryIngestExtendedTests(unittest.TestCase):
    def _history_table_sql(self) -> str:
        return (
            "create table history_import ("
            "history_id text primary key, "
            "bundle_id text not null, "
            "owner text not null, "
            "percent real not null, "
            "hidden_percent real not null, "
            "band text not null, "
            "started_at text not null, "
            "payload_json text not null"
            ");"
        )

    def test_normalize_row_coerces_percent_to_float(self) -> None:
        row = history_ingest.normalize_row(_row(percent="91.50"))
        self.assertEqual(row["percent"], 91.5)

    def test_normalize_row_coerces_hidden_percent_to_float(self) -> None:
        row = history_ingest.normalize_row(_row(hidden_percent="87.20"))
        self.assertEqual(row["hidden_percent"], 87.2)

    def test_normalize_row_strips_history_id(self) -> None:
        row = history_ingest.normalize_row(_row(history_id=" hist-001 "))
        self.assertEqual(row["history_id"], "hist-001")

    def test_normalize_row_strips_owner(self) -> None:
        row = history_ingest.normalize_row(_row(owner=" finance_ops "))
        self.assertEqual(row["owner"], "finance_ops")

    def test_normalize_row_preserves_extra_fields(self) -> None:
        row = history_ingest.normalize_row(_row(release_channel="partner"))
        self.assertEqual(row["release_channel"], "partner")

    def test_normalize_row_rejects_missing_history_id(self) -> None:
        with self.assertRaises(history_ingest.HistoryRowError):
            history_ingest.normalize_row({key: value for key, value in _row().items() if key != "history_id"})

    def test_normalize_row_rejects_missing_bundle_id(self) -> None:
        with self.assertRaises(history_ingest.HistoryRowError):
            history_ingest.normalize_row({key: value for key, value in _row().items() if key != "bundle_id"})

    def test_normalize_row_rejects_missing_owner(self) -> None:
        with self.assertRaises(history_ingest.HistoryRowError):
            history_ingest.normalize_row({key: value for key, value in _row().items() if key != "owner"})

    def test_normalize_row_rejects_missing_percent(self) -> None:
        with self.assertRaises(history_ingest.HistoryRowError):
            history_ingest.normalize_row({key: value for key, value in _row().items() if key != "percent"})

    def test_normalize_row_rejects_missing_hidden_percent(self) -> None:
        with self.assertRaises(history_ingest.HistoryRowError):
            history_ingest.normalize_row({key: value for key, value in _row().items() if key != "hidden_percent"})

    def test_normalize_row_rejects_missing_band(self) -> None:
        with self.assertRaises(history_ingest.HistoryRowError):
            history_ingest.normalize_row({key: value for key, value in _row().items() if key != "band"})

    def test_normalize_row_rejects_missing_started_at(self) -> None:
        with self.assertRaises(history_ingest.HistoryRowError):
            history_ingest.normalize_row({key: value for key, value in _row().items() if key != "started_at"})

    def test_normalize_row_rejects_blank_history_id(self) -> None:
        with self.assertRaises(history_ingest.HistoryRowError):
            history_ingest.normalize_row(_row(history_id="   "))

    def test_normalize_row_rejects_blank_owner(self) -> None:
        with self.assertRaises(history_ingest.HistoryRowError):
            history_ingest.normalize_row(_row(owner="   "))

    def test_normalize_row_rejects_blank_band(self) -> None:
        with self.assertRaises(history_ingest.HistoryRowError):
            history_ingest.normalize_row(_row(band=" "))

    def test_normalize_row_rejects_non_numeric_percent(self) -> None:
        with self.assertRaises(history_ingest.HistoryRowError):
            history_ingest.normalize_row(_row(percent="banana"))

    def test_normalize_row_rejects_non_numeric_hidden_percent(self) -> None:
        with self.assertRaises(history_ingest.HistoryRowError):
            history_ingest.normalize_row(_row(hidden_percent="banana"))

    def test_load_rows_ignores_blank_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.jsonl"
            path.write_text(
                "\n".join(
                    [
                        "",
                        json.dumps(_row(history_id="hist-001")),
                        "   ",
                        json.dumps(_row(history_id="hist-002")),
                    ]
                ),
                encoding="utf-8",
                newline="\n",
            )
            rows = history_ingest.load_rows(path)
        self.assertEqual(len(rows), 2)

    def test_load_rows_rejects_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.jsonl"
            path.write_text("{bad json}\n", encoding="utf-8", newline="\n")
            with self.assertRaises(history_ingest.HistoryRowError) as ctx:
                history_ingest.load_rows(path)
        self.assertIn("line 1", str(ctx.exception))

    def test_load_rows_rejects_array_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.jsonl"
            path.write_text("[1, 2, 3]\n", encoding="utf-8", newline="\n")
            with self.assertRaises(history_ingest.HistoryRowError) as ctx:
                history_ingest.load_rows(path)
        self.assertIn("object", str(ctx.exception))

    def test_load_rows_passes_line_number_to_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.jsonl"
            path.write_text(
                "\n".join([json.dumps(_row()), json.dumps(_row(owner=" ")), ""]),
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaises(history_ingest.HistoryRowError) as ctx:
                history_ingest.load_rows(path)
        self.assertIn("line 2", str(ctx.exception))

    def test_monthly_rollup_handles_empty_rows(self) -> None:
        self.assertEqual(
            history_ingest.monthly_rollup([]),
            {"count": 0, "average_percent": 0.0, "average_hidden_percent": 0.0},
        )

    def test_monthly_rollup_includes_hidden_average(self) -> None:
        summary = history_ingest.monthly_rollup([_row(hidden_percent=80), _row(history_id="hist-002", hidden_percent=88)])
        self.assertEqual(summary["average_hidden_percent"], 84.0)

    def test_monthly_rollup_includes_first_started_at(self) -> None:
        summary = history_ingest.monthly_rollup(
            [
                _row(started_at="2026-02-03T08:00:00Z"),
                _row(history_id="hist-002", started_at="2026-02-05T08:00:00Z"),
            ]
        )
        self.assertEqual(summary["first_started_at"], "2026-02-03T08:00:00Z")

    def test_owner_rollup_groups_counts(self) -> None:
        rollup = history_ingest.owner_rollup(
            [_row(owner="finance_ops"), _row(history_id="hist-002", owner="finance_ops"), _row(history_id="hist-003", owner="support_ops")]
        )
        self.assertEqual(rollup["finance_ops"]["count"], 2)

    def test_owner_rollup_sorts_owner_keys(self) -> None:
        rollup = history_ingest.owner_rollup(
            [_row(owner="support_ops"), _row(history_id="hist-002", owner="finance_ops")]
        )
        self.assertEqual(list(rollup), ["finance_ops", "support_ops"])

    def test_owner_rollup_averages_hidden_percent(self) -> None:
        rollup = history_ingest.owner_rollup(
            [_row(hidden_percent=80), _row(history_id="hist-002", hidden_percent=90)]
        )
        self.assertEqual(rollup["finance_ops"]["average_hidden_percent"], 85.0)

    def test_band_rollup_groups_counts(self) -> None:
        rollup = history_ingest.band_rollup(
            [_row(band="watch"), _row(history_id="hist-002", band="watch"), _row(history_id="hist-003", band="ready")]
        )
        self.assertEqual(rollup["watch"]["count"], 2)

    def test_band_rollup_averages_percent(self) -> None:
        rollup = history_ingest.band_rollup([_row(percent=75), _row(history_id="hist-002", percent=95)])
        self.assertEqual(rollup["ready"]["average_percent"], 85.0)

    def test_month_rollup_groups_by_month(self) -> None:
        rollup = history_ingest.month_rollup(
            [
                _row(started_at="2026-01-01T09:00:00Z"),
                _row(history_id="hist-002", started_at="2026-02-01T09:00:00Z"),
            ]
        )
        self.assertEqual(list(rollup), ["2026-01", "2026-02"])

    def test_month_rollup_includes_owners(self) -> None:
        rollup = history_ingest.month_rollup(
            [
                _row(owner="finance_ops", started_at="2026-01-01T09:00:00Z"),
                _row(history_id="hist-002", owner="support_ops", started_at="2026-01-11T09:00:00Z"),
            ]
        )
        self.assertEqual(rollup["2026-01"]["owners"], ["finance_ops", "support_ops"])

    def test_import_summary_contains_expected_sections(self) -> None:
        summary = history_ingest.import_summary([_row()])
        self.assertEqual(set(summary), {"monthly", "owners", "bands", "months"})

    def test_insert_rows_replaces_duplicate_history_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "history.sqlite3"
            with closing(sqlite3.connect(db)) as conn:
                conn.executescript(self._history_table_sql())
                history_ingest.insert_rows(
                    conn,
                    [
                        _row(percent=75.0),
                        _row(percent=99.0),
                    ],
                )
                row = conn.execute("select count(*), max(percent) from history_import").fetchone()
        self.assertEqual(row[0], 1)
        self.assertEqual(row[1], 99.0)

    def test_insert_rows_rejects_invalid_row_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "history.sqlite3"
            with closing(sqlite3.connect(db)) as conn:
                conn.executescript(self._history_table_sql())
                with self.assertRaises(history_ingest.HistoryRowError):
                    history_ingest.insert_rows(conn, [_row(), _row(history_id="hist-002", percent="bad")])
                count = conn.execute("select count(*) from history_import").fetchone()[0]
        self.assertEqual(count, 0)

    def test_insert_rows_stores_normalized_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "history.sqlite3"
            with closing(sqlite3.connect(db)) as conn:
                conn.executescript(self._history_table_sql())
                history_ingest.insert_rows(conn, [_row(owner=" finance_ops ", percent="91.5")])
                payload = conn.execute("select payload_json from history_import").fetchone()[0]
        stored = json.loads(payload)
        self.assertEqual(stored["owner"], "finance_ops")
        self.assertEqual(stored["percent"], 91.5)

    def test_load_rows_from_temp_file_normalizes_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.jsonl"
            path.write_text(json.dumps(_row(percent="77.5", hidden_percent="66.5")) + "\n", encoding="utf-8", newline="\n")
            rows = history_ingest.load_rows(path)
        self.assertEqual(rows[0]["percent"], 77.5)
        self.assertEqual(rows[0]["hidden_percent"], 66.5)

    def test_import_summary_handles_empty_rows(self) -> None:
        summary = history_ingest.import_summary([])
        self.assertEqual(summary["owners"], {})
        self.assertEqual(summary["bands"], {})
        self.assertEqual(summary["months"], {})
