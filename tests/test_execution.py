from __future__ import annotations

import unittest

from engineering_challenge.execution import evaluate_attempt, run_to_dict
from tests.helpers import attempt, bundle


class ExecutionTests(unittest.TestCase):
    def test_strong_attempt_passes_every_case(self) -> None:
        run = evaluate_attempt(bundle("merchant-closeout"), attempt("merchant-closeout", "strong"))
        self.assertTrue(all(item.status == "pass" for item in run.case_results))

    def test_mixed_attempt_contains_failures_timeouts_and_errors(self) -> None:
        run = evaluate_attempt(bundle("warehouse-routing"), attempt("warehouse-routing", "mixed"))
        statuses = {item.status for item in run.case_results}
        self.assertIn("timeout", statuses)
        self.assertIn("error", statuses)
        self.assertIn("fail", statuses)

    def test_weak_attempt_produces_missing_results(self) -> None:
        run = evaluate_attempt(bundle("claims-intake"), attempt("claims-intake", "weak"))
        self.assertTrue(any(item.status == "fail" for item in run.case_results))

    def test_run_to_dict_contains_totals(self) -> None:
        run = evaluate_attempt(bundle("reserve-rollforward"), attempt("reserve-rollforward", "mixed"))
        payload = run_to_dict(run)
        self.assertIn("totals", payload)
        self.assertEqual(payload["run_id"], "reserve-rollforward-mixed-run")
