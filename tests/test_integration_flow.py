from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from engineering_challenge import audit, catalog, reporting, storage
from engineering_challenge.execution import evaluate_attempt
from engineering_challenge.release import build_release_manifest
from engineering_challenge.scoring import score_run
from tests.helpers import FIXTURES, attempt


class IntegrationFlowTests(unittest.TestCase):
    def test_end_to_end_release_run_score_and_storage_flow(self) -> None:
        bundle_root = FIXTURES / "catalog" / "merchant-closeout"
        item = catalog.load_bundle(bundle_root)
        run = evaluate_attempt(item, attempt("merchant-closeout", "mixed"))
        card = score_run(run, item)
        manifest = build_release_manifest("integration-release", [item], created_at="2026-06-03T10:00:00Z")
        packet = audit.build_audit_packet(item, run, card, manifest)
        markdown = reporting.scorecard_markdown(card)
        self.assertIn("Scorecard", markdown)
        self.assertIn("release_manifest", packet)
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "workbench.sqlite3"
            storage.record_bundle(db_path, item, catalog.bundle_summary(item))
            storage.record_run(db_path, run, card)
            self.assertTrue(storage.recent_runs(db_path))
