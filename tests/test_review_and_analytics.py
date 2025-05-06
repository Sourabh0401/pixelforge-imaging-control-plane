from __future__ import annotations

import unittest

from engineering_challenge.analytics import difficulty_drift, release_readiness
from engineering_challenge.execution import evaluate_attempt
from engineering_challenge.review import owner_hotspots, remediation_queue
from engineering_challenge.scoring import score_run
from tests.helpers import attempt, bundle


class ReviewAnalyticsTests(unittest.TestCase):
    def test_remediation_queue_sorts_low_scores_first(self) -> None:
        cards = []
        for name in ["claims-intake", "reserve-rollforward"]:
            item = bundle(name)
            run = evaluate_attempt(item, attempt(name, "weak"))
            cards.append(score_run(run, item))
        queue = remediation_queue(cards)
        self.assertGreaterEqual(len(queue), 1)

    def test_owner_hotspots_groups_runs(self) -> None:
        item = bundle("merchant-closeout")
        cards = [score_run(evaluate_attempt(item, attempt("merchant-closeout", mode)), item) for mode in ("mixed", "strong")]
        hotspots = owner_hotspots(cards)
        self.assertIn("finance_ops", hotspots)

    def test_difficulty_drift_compares_old_and_new_scorecards(self) -> None:
        item = bundle("warehouse-routing")
        previous = [score_run(evaluate_attempt(item, attempt("warehouse-routing", "weak")), item)]
        current = [score_run(evaluate_attempt(item, attempt("warehouse-routing", "strong")), item)]
        drift = difficulty_drift(previous, current)
        self.assertGreater(drift["warehouse-routing"], 0)

    def test_release_readiness_requires_average_and_no_blocked(self) -> None:
        item = bundle("merchant-closeout")
        cards = [score_run(evaluate_attempt(item, attempt("merchant-closeout", "strong")), item)]
        readiness = release_readiness(cards)
        self.assertTrue(readiness["ready"])
