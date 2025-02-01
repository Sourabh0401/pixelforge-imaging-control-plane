from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from engineering_challenge import audit
from engineering_challenge.execution import evaluate_attempt
from engineering_challenge.release import build_release_manifest
from engineering_challenge.scoring import score_run
from tests.helpers import attempt, bundle


class AuditTests(unittest.TestCase):
    def test_audit_packet_contains_digest(self) -> None:
        item = bundle("merchant-closeout")
        run = evaluate_attempt(item, attempt("merchant-closeout", "mixed"))
        card = score_run(run, item)
        manifest = build_release_manifest("release-a", [item], created_at="2026-06-03T10:00:00Z")
        packet = audit.build_audit_packet(item, run, card, manifest)
        self.assertIn("digest", packet)

    def test_audit_zip_contains_fixed_files(self) -> None:
        item = bundle("warehouse-routing")
        run = evaluate_attempt(item, attempt("warehouse-routing", "mixed"))
        card = score_run(run, item)
        manifest = build_release_manifest("release-a", [item], created_at="2026-06-03T10:00:00Z")
        packet = audit.build_audit_packet(item, run, card, manifest)
        data = audit.audit_zip_bytes(packet)
        with zipfile.ZipFile(Path(tempfile.gettempdir()) / "audit-check.zip", "w") as _:
            pass
        with zipfile.ZipFile(__import__("io").BytesIO(data)) as archive:
            self.assertEqual(sorted(archive.namelist()), ["audit_packet.json", "manifest.json"])
