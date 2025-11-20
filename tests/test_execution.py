from __future__ import annotations

import unittest

from pixelforge_ops.execution import evaluate_attempt, run_to_dict
from tests.helpers import attempt, bundle


class ExecutionTests(unittest.TestCase):
    def test_strong_attempt_passes_every_case(self) -> None:
        run = evaluate_attempt(bundle("jpeg-codec-fidelity"), attempt("jpeg-codec-fidelity", "strong"))
        self.assertTrue(all(item.status == "pass" for item in run.case_results))

    def test_mixed_attempt_contains_failures_timeouts_and_errors(self) -> None:
        run = evaluate_attempt(bundle("raster-transform-tiling"), attempt("raster-transform-tiling", "mixed"))
        statuses = {item.status for item in run.case_results}
        self.assertIn("timeout", statuses)
        self.assertIn("error", statuses)
        self.assertIn("fail", statuses)

    def test_weak_attempt_produces_missing_results(self) -> None:
        run = evaluate_attempt(bundle("metadata-exif-ingest"), attempt("metadata-exif-ingest", "weak"))
        self.assertTrue(any(item.status == "fail" for item in run.case_results))

    def test_run_to_dict_contains_totals(self) -> None:
        run = evaluate_attempt(bundle("alpha-channel-recovery"), attempt("alpha-channel-recovery", "mixed"))
        payload = run_to_dict(run)
        self.assertIn("totals", payload)
        self.assertEqual(payload["run_id"], "alpha-channel-recovery-mixed-run")


