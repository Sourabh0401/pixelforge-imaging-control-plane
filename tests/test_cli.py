from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
import os
from pathlib import Path

from pixelforge_ops.cli import main

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


class CliTests(unittest.TestCase):
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

    def test_catalog_summary_command(self) -> None:
        payload = self.run_cli("catalog-summary", str(FIXTURES / "catalog"))
        self.assertEqual(payload["bundle_count"], 12)

    def test_validate_bundle_command(self) -> None:
        payload = self.run_cli("validate-bundle", str(FIXTURES / "catalog" / "jpeg-codec-fidelity"))
        self.assertEqual(payload["bundle_id"], "jpeg-codec-fidelity")

    def test_run_attempt_command(self) -> None:
        payload = self.run_cli(
            "run-attempt",
            str(FIXTURES / "catalog" / "jpeg-codec-fidelity"),
            str(FIXTURES / "attempts" / "jpeg-codec-fidelity_mixed.json"),
        )
        self.assertEqual(payload["bundle_id"], "jpeg-codec-fidelity")

    def test_build_audit_command_writes_zip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "packet.zip"
            payload = self.run_cli(
                "build-audit",
                str(FIXTURES / "catalog" / "jpeg-codec-fidelity"),
                str(FIXTURES / "attempts" / "jpeg-codec-fidelity_mixed.json"),
                "--output",
                str(output),
            )
            self.assertTrue(output.exists())
            self.assertIn("digest", payload)


