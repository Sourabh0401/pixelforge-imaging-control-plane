from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from engineering_challenge.cli import main

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


class ExtendedCliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> dict[str, object]:
        buffer = io.StringIO()
        previous = Path.cwd()
        try:
            os.chdir(ROOT)
            with redirect_stdout(buffer):
                code = main(list(args))
        finally:
            os.chdir(previous)
        self.assertEqual(code, 0, msg=buffer.getvalue())
        return json.loads(buffer.getvalue())

    def test_build_scorecard_command(self) -> None:
        payload = self.run_cli(
            "build-scorecard",
            str(FIXTURES / "catalog" / "merchant-closeout"),
            str(FIXTURES / "attempts" / "merchant-closeout_mixed.json"),
        )
        self.assertEqual(payload["bundle_id"], "merchant-closeout")

    def test_build_release_command(self) -> None:
        payload = self.run_cli(
            "build-release",
            str(FIXTURES / "catalog"),
            "merchant-closeout",
            "warehouse-routing",
            "--release-id",
            "cli-release",
        )
        self.assertEqual(payload["release_id"], "cli-release")

    def test_sync_sqlite_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "ops.sqlite3"
            payload = self.run_cli(
                "sync-sqlite",
                str(db),
                str(FIXTURES / "catalog" / "merchant-closeout"),
                str(FIXTURES / "attempts" / "merchant-closeout_mixed.json"),
            )
            self.assertIn("recent_runs", payload)

    def test_build_audit_command_can_write_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "packet.zip"
            payload = self.run_cli(
                "build-audit",
                str(FIXTURES / "catalog" / "merchant-closeout"),
                str(FIXTURES / "attempts" / "merchant-closeout_mixed.json"),
                "--output",
                str(output),
            )
            self.assertTrue(output.exists())
            self.assertIn("digest", payload)
