from __future__ import annotations

import unittest

from engineering_challenge.execution import evaluate_attempt
from engineering_challenge.scoring import portfolio_rollup, score_run
from tests.helpers import attempt, bundle


class ScoringTests(unittest.TestCase):
    def test_strong_attempt_scores_ready_band(self) -> None:
        run = evaluate_attempt(bundle("merchant-closeout"), attempt("merchant-closeout", "strong"))
        card = score_run(run, bundle("merchant-closeout"))
        self.assertEqual(card.band, "ready")
        self.assertGreaterEqual(card.percent, 95.0)

    def test_mixed_attempt_surfaces_policy_flags(self) -> None:
        run = evaluate_attempt(bundle("warehouse-routing"), attempt("warehouse-routing", "mixed"))
        card = score_run(run, bundle("warehouse-routing"))
        self.assertTrue(card.policy_flags)

    def test_portfolio_rollup_groups_by_owner(self) -> None:
        cards = []
        for name in ["merchant-closeout", "warehouse-routing", "claims-intake"]:
            run = evaluate_attempt(bundle(name), attempt(name, "mixed"))
            cards.append(score_run(run, bundle(name)))
        rollup = portfolio_rollup(cards)
        self.assertEqual(rollup["count"], 3)
        self.assertTrue(rollup["owner_average_percent"])
