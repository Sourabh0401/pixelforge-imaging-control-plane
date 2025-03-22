from __future__ import annotations

import json
import unittest
import zipfile
from pathlib import Path

from tests.ext_helpers import FIXTURES, history_rows


class FixtureCorpusTests(unittest.TestCase):
    def test_history_manifest_lists_twelve_months(self) -> None:
        manifest = json.loads((FIXTURES / "history_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest), 12)

    def test_history_rows_are_present_for_january(self) -> None:
        self.assertEqual(len(history_rows(1)), 2400)

    def test_history_rows_have_expected_keys(self) -> None:
        row = history_rows(1)[0]
        self.assertIn("artifact_digest", row)

    def test_sqlite_snapshots_exist(self) -> None:
        paths = sorted((FIXTURES / "sqlite_snapshots").glob("ops_history_2026_q*.sqlite3"))
        self.assertEqual(len(paths), 4)

    def test_audit_samples_exist(self) -> None:
        paths = sorted((FIXTURES / "audit_samples").glob("*.zip"))
        self.assertEqual(len(paths), 8)

    def test_audit_sample_contains_trace_json(self) -> None:
        path = sorted((FIXTURES / "audit_samples").glob("*.zip"))[0]
        with zipfile.ZipFile(path) as archive:
            self.assertTrue(any(name.endswith(".json") for name in archive.namelist()))

    def test_example_audit_packets_exist(self) -> None:
        paths = sorted((Path(__file__).resolve().parents[1] / "examples" / "audit_packets").glob("*.zip"))
        self.assertEqual(len(paths), 12)

    def test_owner_dashboards_exist(self) -> None:
        paths = sorted((Path(__file__).resolve().parents[1] / "examples" / "owner_dashboards").glob("*.md"))
        self.assertTrue(paths)

    def test_release_notes_exist(self) -> None:
        paths = sorted((Path(__file__).resolve().parents[1] / "examples" / "release_notes").glob("*.md"))
        self.assertEqual(len(paths), 12)

    def test_risk_reports_exist(self) -> None:
        paths = sorted((Path(__file__).resolve().parents[1] / "examples" / "risk_reports").glob("*.json"))
        self.assertEqual(len(paths), 10)
