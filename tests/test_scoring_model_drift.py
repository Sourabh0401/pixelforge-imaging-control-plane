from __future__ import annotations

import unittest

from engineering_challenge.execution import evaluate_attempt
from engineering_challenge.scoring import score_run
from engineering_challenge.scoring_model import drift
from tests.ext_helpers import attempt, bundle


class DriftTests(unittest.TestCase):
    def test_percent_drift_positive_for_strong_over_weak(self) -> None:
        item = bundle("warehouse-routing")
        previous = [score_run(evaluate_attempt(item, attempt("warehouse-routing", "weak")), item)]
        current = [score_run(evaluate_attempt(item, attempt("warehouse-routing", "strong")), item)]
        values = drift.percent_drift(previous, current)
        self.assertGreater(values["warehouse-routing"], 0)

    def test_hidden_drift_uses_hidden_percent(self) -> None:
        item = bundle("warehouse-routing")
        previous = [score_run(evaluate_attempt(item, attempt("warehouse-routing", "weak")), item)]
        current = [score_run(evaluate_attempt(item, attempt("warehouse-routing", "strong")), item)]
        values = drift.hidden_drift(previous, current)
        self.assertIn("warehouse-routing", values)

    def test_drift_alerts_only_raise_large_moves(self) -> None:
        item = bundle("warehouse-routing")
        previous = [score_run(evaluate_attempt(item, attempt("warehouse-routing", "weak")), item)]
        current = [score_run(evaluate_attempt(item, attempt("warehouse-routing", "strong")), item)]
        self.assertTrue(drift.drift_alerts(previous, current))

    def test_by_bundle_maps_scorecards(self) -> None:
        item = bundle("merchant-closeout")
        cards = [score_run(evaluate_attempt(item, attempt("merchant-closeout", "mixed")), item)]
        self.assertIn("merchant-closeout", drift.by_bundle(cards))
