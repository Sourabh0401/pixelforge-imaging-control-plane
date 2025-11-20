from __future__ import annotations

import io
import json
import os
import sqlite3
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from pixelforge_ops.cli import main
from pixelforge_ops.persistence.history_ingest import HistoryRowError


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
CATALOG = FIXTURES / "catalog"
ATTEMPTS = FIXTURES / "attempts"
SNAPSHOT = FIXTURES / "sqlite_snapshots" / "ops_history_2026_q1.sqlite3"


class CliMatrixTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        buffer = io.StringIO()
        previous = Path.cwd()
        try:
            os.chdir(ROOT)
            with redirect_stdout(buffer):
                code = main(list(args))
        finally:
            os.chdir(previous)
        return code, buffer.getvalue()

    def run_cli_json(self, *args: str) -> dict[str, object]:
        code, output = self.run_cli(*args)
        self.assertEqual(code, 0, msg=output)
        return json.loads(output)

    def assert_parser_exit(self, *args: str) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as ctx:
                self.run_cli(*args)
        self.assertEqual(ctx.exception.code, 2)

    def test_no_args_exits_with_parser_error(self) -> None:
        self.assert_parser_exit()

    def test_unknown_command_exits_with_parser_error(self) -> None:
        self.assert_parser_exit("not-a-command")

    def test_catalog_summary_returns_bundle_count(self) -> None:
        payload = self.run_cli_json("catalog-summary", str(CATALOG))
        self.assertEqual(payload["bundle_count"], 12)

    def test_catalog_summary_includes_domains(self) -> None:
        payload = self.run_cli_json("catalog-summary", str(CATALOG))
        self.assertIn("codec_ops", payload["domains"])

    def test_catalog_summary_missing_root_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.run_cli("catalog-summary", str(CATALOG / "missing"))

    def test_validate_bundle_returns_bundle_id(self) -> None:
        payload = self.run_cli_json("validate-bundle", str(CATALOG / "jpeg-codec-fidelity"))
        self.assertEqual(payload["bundle_id"], "jpeg-codec-fidelity")

    def test_validate_bundle_includes_issues_array(self) -> None:
        payload = self.run_cli_json("validate-bundle", str(CATALOG / "jpeg-codec-fidelity"))
        self.assertIn("issues", payload)

    def test_validate_bundle_missing_bundle_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.run_cli("validate-bundle", str(CATALOG / "missing"))

    def test_run_attempt_returns_bundle_id(self) -> None:
        payload = self.run_cli_json(
            "run-attempt",
            str(CATALOG / "jpeg-codec-fidelity"),
            str(ATTEMPTS / "jpeg-codec-fidelity_mixed.json"),
        )
        self.assertEqual(payload["bundle_id"], "jpeg-codec-fidelity")

    def test_run_attempt_can_write_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "run.json"
            payload = self.run_cli_json(
                "run-attempt",
                str(CATALOG / "jpeg-codec-fidelity"),
                str(ATTEMPTS / "jpeg-codec-fidelity_mixed.json"),
                "--output",
                str(out),
            )
            self.assertTrue(out.exists())
            self.assertEqual(payload["run_id"], "jpeg-codec-fidelity-mixed-run")

    def test_run_attempt_missing_attempt_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.run_cli("run-attempt", str(CATALOG / "jpeg-codec-fidelity"), str(ATTEMPTS / "missing.json"))

    def test_build_scorecard_returns_bundle_id(self) -> None:
        payload = self.run_cli_json(
            "build-scorecard",
            str(CATALOG / "jpeg-codec-fidelity"),
            str(ATTEMPTS / "jpeg-codec-fidelity_mixed.json"),
        )
        self.assertEqual(payload["bundle_id"], "jpeg-codec-fidelity")

    def test_build_scorecard_includes_policy_flags(self) -> None:
        payload = self.run_cli_json(
            "build-scorecard",
            str(CATALOG / "jpeg-codec-fidelity"),
            str(ATTEMPTS / "jpeg-codec-fidelity_mixed.json"),
        )
        self.assertIn("requires-review", payload["policy_flags"])

    def test_build_scorecard_missing_attempt_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.run_cli("build-scorecard", str(CATALOG / "jpeg-codec-fidelity"), str(ATTEMPTS / "missing.json"))

    def test_build_release_returns_release_id(self) -> None:
        payload = self.run_cli_json("build-release", str(CATALOG), "jpeg-codec-fidelity", "raster-transform-tiling", "--release-id", "cli-release")
        self.assertEqual(payload["release_id"], "cli-release")

    def test_build_release_uses_default_release_id(self) -> None:
        payload = self.run_cli_json("build-release", str(CATALOG), "jpeg-codec-fidelity")
        self.assertEqual(payload["release_id"], "release-local")

    def test_build_release_missing_bundle_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.run_cli("build-release", str(CATALOG), "missing-bundle")

    def test_build_audit_returns_digest(self) -> None:
        payload = self.run_cli_json(
            "build-audit",
            str(CATALOG / "jpeg-codec-fidelity"),
            str(ATTEMPTS / "jpeg-codec-fidelity_mixed.json"),
        )
        self.assertIn("digest", payload)

    def test_build_audit_can_write_zip_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "packet.zip"
            self.run_cli_json(
                "build-audit",
                str(CATALOG / "jpeg-codec-fidelity"),
                str(ATTEMPTS / "jpeg-codec-fidelity_mixed.json"),
                "--output",
                str(out),
            )
            self.assertTrue(out.exists())

    def test_build_audit_missing_attempt_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.run_cli("build-audit", str(CATALOG / "jpeg-codec-fidelity"), str(ATTEMPTS / "missing.json"))

    def test_owner_dashboard_returns_owner(self) -> None:
        payload = self.run_cli_json("owner-dashboard", str(SNAPSHOT), "codec_ops")
        self.assertEqual(payload["owner"], "codec_ops")

    def test_owner_dashboard_includes_callouts(self) -> None:
        payload = self.run_cli_json("owner-dashboard", str(SNAPSHOT), "codec_ops")
        self.assertEqual(len(payload["callouts"]), 3)

    def test_owner_dashboard_missing_snapshot_raises_operational_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.sqlite3"
            with self.assertRaises(sqlite3.OperationalError):
                self.run_cli("owner-dashboard", str(missing), "codec_ops")

    def test_history_rollup_returns_count(self) -> None:
        payload = self.run_cli_json("history-rollup", str(FIXTURES / "history" / "ops_history_2026_01.jsonl"))
        self.assertEqual(payload["count"], 2400)

    def test_history_rollup_includes_hidden_average(self) -> None:
        payload = self.run_cli_json("history-rollup", str(FIXTURES / "history" / "ops_history_2026_01.jsonl"))
        self.assertIn("average_hidden_percent", payload)

    def test_history_rollup_malformed_jsonl_raises_history_row_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.jsonl"
            path.write_text("{bad json}\n", encoding="utf-8", newline="\n")
            with self.assertRaises(HistoryRowError):
                self.run_cli("history-rollup", str(path))

    def test_snapshot_summary_returns_row_count(self) -> None:
        payload = self.run_cli_json("snapshot-summary", str(SNAPSHOT))
        self.assertEqual(payload["history_row_count"], 7200)

    def test_snapshot_summary_includes_table_names(self) -> None:
        payload = self.run_cli_json("snapshot-summary", str(SNAPSHOT))
        self.assertEqual(payload["tables"], ["history_import"])

    def test_snapshot_summary_missing_snapshot_raises_operational_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.sqlite3"
            with self.assertRaises(sqlite3.OperationalError):
                self.run_cli("snapshot-summary", str(missing))

    def test_release_readiness_returns_ready_flag(self) -> None:
        payload = self.run_cli_json(
            "release-readiness",
            str(CATALOG / "jpeg-codec-fidelity"),
            str(ATTEMPTS / "jpeg-codec-fidelity_mixed.json"),
        )
        self.assertIn("ready", payload)

    def test_release_readiness_marks_blocked_bundle(self) -> None:
        payload = self.run_cli_json(
            "release-readiness",
            str(CATALOG / "jpeg-codec-fidelity"),
            str(ATTEMPTS / "jpeg-codec-fidelity_mixed.json"),
        )
        self.assertIn("jpeg-codec-fidelity", payload["blocked"])

    def test_release_readiness_missing_attempt_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.run_cli("release-readiness", str(CATALOG / "jpeg-codec-fidelity"), str(ATTEMPTS / "missing.json"))

    def test_sync_sqlite_returns_recent_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "ops.sqlite3"
            payload = self.run_cli_json(
                "sync-sqlite",
                str(db),
                str(CATALOG / "jpeg-codec-fidelity"),
                str(ATTEMPTS / "jpeg-codec-fidelity_mixed.json"),
            )
            self.assertIn("recent_runs", payload)

    def test_sync_sqlite_creates_db_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "ops.sqlite3"
            self.run_cli_json(
                "sync-sqlite",
                str(db),
                str(CATALOG / "jpeg-codec-fidelity"),
                str(ATTEMPTS / "jpeg-codec-fidelity_mixed.json"),
            )
            self.assertTrue(db.exists())

    def test_sync_sqlite_missing_bundle_raises_file_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "ops.sqlite3"
            with self.assertRaises(FileNotFoundError):
                self.run_cli("sync-sqlite", str(db), str(CATALOG / "missing"), str(ATTEMPTS / "jpeg-codec-fidelity_mixed.json"))

    def test_validate_bundle_parser_requires_bundle_argument(self) -> None:
        self.assert_parser_exit("validate-bundle")

    def test_build_release_parser_requires_bundle_names(self) -> None:
        self.assert_parser_exit("build-release", str(CATALOG))

    def test_sync_sqlite_parser_requires_attempt_argument(self) -> None:
        self.assert_parser_exit("sync-sqlite", "ops.sqlite3", str(CATALOG / "jpeg-codec-fidelity"))

    def test_history_rollup_parser_requires_history_path(self) -> None:
        self.assert_parser_exit("history-rollup")

    def test_owner_dashboard_parser_requires_owner_argument(self) -> None:
        self.assert_parser_exit("owner-dashboard", str(SNAPSHOT))


