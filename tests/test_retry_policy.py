from __future__ import annotations

import unittest

from pixelforge_ops.execution import evaluate_attempt
from pixelforge_ops.execution_engine import retry_policy
from tests.ext_helpers import attempt, bundle


class RetryPolicyTests(unittest.TestCase):
    def test_timeout_cases_become_retryable(self) -> None:
        run = evaluate_attempt(bundle("jpeg-codec-fidelity"), attempt("jpeg-codec-fidelity", "weak"))
        decisions = retry_policy.run_retry_plan(run)
        self.assertTrue(any(item.action in {"retry", "review"} for item in decisions))

    def test_retry_budget_defaults_for_profile(self) -> None:
        self.assertEqual(retry_policy.retry_budget("default"), 8)

    def test_schedule_summary_has_owner_queue(self) -> None:
        run = evaluate_attempt(bundle("metadata-exif-ingest"), attempt("metadata-exif-ingest", "mixed"))
        summary = retry_policy.schedule_summary(run)
        self.assertIn("owner_queue", summary)

    def test_next_retry_window_returns_tuple(self) -> None:
        run = evaluate_attempt(bundle("raster-transform-tiling"), attempt("raster-transform-tiling", "mixed"))
        window = retry_policy.next_retry_window(run)
        self.assertEqual(len(window), 2)

    def test_retry_horizon_is_text(self) -> None:
        run = evaluate_attempt(bundle("decoder-recovery-replay"), attempt("decoder-recovery-replay", "mixed"))
        self.assertIn(":", retry_policy.retry_horizon(run))

    def test_should_pause_bundle_when_budget_exceeded(self) -> None:
        run = evaluate_attempt(bundle("jpeg-codec-fidelity"), attempt("jpeg-codec-fidelity", "weak"))
        self.assertIsInstance(retry_policy.should_pause_bundle(run), bool)


