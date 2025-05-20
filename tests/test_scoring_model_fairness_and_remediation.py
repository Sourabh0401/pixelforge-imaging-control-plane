from __future__ import annotations

import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from engineering_challenge.execution import evaluate_attempt
from engineering_challenge.models import Scorecard
from engineering_challenge.scoring import score_run
from engineering_challenge.scoring_model import fairness, remediation
from tests.ext_helpers import attempt, bundle


class FairnessRemediationTests(unittest.TestCase):
    def _scorecard(
        self,
        *,
        bundle_id: str = "bundle-a",
        owner: str = "finance_ops",
        percent: float = 88.0,
        public_percent: float = 88.0,
        hidden_percent: float = 88.0,
        policy_flags: tuple[str, ...] = (),
    ) -> Scorecard:
        return Scorecard(
            run_id=f"{bundle_id}-run",
            bundle_id=bundle_id,
            percent=percent,
            band="watch",
            public_percent=public_percent,
            hidden_percent=hidden_percent,
            section_totals={"audit": {"percent": percent}},
            policy_flags=policy_flags,
            owner=owner,
        )

    def test_hidden_gap_returns_difference(self) -> None:
        card = score_run(evaluate_attempt(bundle("merchant-closeout"), attempt("merchant-closeout", "mixed")), bundle("merchant-closeout"))
        self.assertIsInstance(fairness.hidden_gap(card), float)

    def test_section_spread_returns_value(self) -> None:
        card = score_run(evaluate_attempt(bundle("merchant-closeout"), attempt("merchant-closeout", "mixed")), bundle("merchant-closeout"))
        self.assertGreaterEqual(fairness.section_spread(card), 0.0)

    def test_fairness_flags_can_return_public_gap(self) -> None:
        card = score_run(evaluate_attempt(bundle("warehouse-routing"), attempt("warehouse-routing", "mixed")), bundle("warehouse-routing"))
        self.assertIsInstance(fairness.fairness_flags(card), tuple)

    def test_fairness_summary_averages_values(self) -> None:
        cards = [
            score_run(evaluate_attempt(bundle("merchant-closeout"), attempt("merchant-closeout", "mixed")), bundle("merchant-closeout")),
            score_run(evaluate_attempt(bundle("warehouse-routing"), attempt("warehouse-routing", "mixed")), bundle("warehouse-routing")),
        ]
        summary = fairness.fairness_summary(cards)
        self.assertIn("average_hidden_gap", summary)

    def test_remediation_reason_handles_low_percent(self) -> None:
        card = score_run(evaluate_attempt(bundle("claims-intake"), attempt("claims-intake", "weak")), bundle("claims-intake"))
        self.assertTrue(remediation.remediation_reason(card))

    def test_remediation_item_contains_flags(self) -> None:
        card = score_run(evaluate_attempt(bundle("warehouse-routing"), attempt("warehouse-routing", "mixed")), bundle("warehouse-routing"))
        item = remediation.remediation_item(card)
        self.assertIn("flags", item)

    def test_remediation_queue_sorts_entries(self) -> None:
        cards = [
            score_run(evaluate_attempt(bundle("merchant-closeout"), attempt("merchant-closeout", "mixed")), bundle("merchant-closeout")),
            score_run(evaluate_attempt(bundle("claims-intake"), attempt("claims-intake", "weak")), bundle("claims-intake")),
        ]
        queue = remediation.remediation_queue(cards)
        self.assertTrue(queue)

    def test_queue_contains_bundle_id(self) -> None:
        card = score_run(evaluate_attempt(bundle("claims-intake"), attempt("claims-intake", "weak")), bundle("claims-intake"))
        item = remediation.remediation_item(card)
        self.assertEqual(item["bundle_id"], "claims-intake")

    def test_remediation_reason_prefers_hidden_gap_branch(self) -> None:
        card = self._scorecard(public_percent=97.0, hidden_percent=70.0, percent=80.0)
        self.assertEqual(remediation.remediation_reason(card), "public-hidden gap requires review")

    def test_remediation_reason_uses_policy_flag_branch(self) -> None:
        card = self._scorecard(percent=80.0, policy_flags=("requires-review",))
        self.assertEqual(remediation.remediation_reason(card), "policy requested review")

    def test_remediation_reason_falls_back_to_manual_spot_check(self) -> None:
        card = self._scorecard(percent=82.0, public_percent=82.0, hidden_percent=81.0)
        self.assertEqual(remediation.remediation_reason(card), "manual spot check")

    def test_remediation_queue_includes_hidden_gap_even_without_policy_flags(self) -> None:
        queue = remediation.remediation_queue([self._scorecard(public_percent=98.0, hidden_percent=70.0, percent=85.0)])
        self.assertEqual(len(queue), 1)

    def test_remediation_queue_includes_policy_flagged_scorecard(self) -> None:
        queue = remediation.remediation_queue([self._scorecard(percent=82.0, policy_flags=("requires-review",))])
        self.assertEqual(len(queue), 1)

    def test_remediation_queue_excludes_healthy_scorecard(self) -> None:
        queue = remediation.remediation_queue([self._scorecard(percent=92.0, public_percent=92.0, hidden_percent=90.0)])
        self.assertEqual(queue, [])

    def test_remediation_item_deduplicates_flags(self) -> None:
        card = self._scorecard(percent=55.0, public_percent=95.0, hidden_percent=60.0, policy_flags=("requires-review",))
        item = remediation.remediation_item(card)
        self.assertEqual(item["flags"].count("requires-review"), 1)

    def test_src_package_init_exports_expected_modules(self) -> None:
        path = Path(__file__).resolve().parents[1] / "src" / "engineering_challenge" / "__init__.py"
        spec = spec_from_file_location("engineering_challenge_src_init", path)
        assert spec and spec.loader
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertIn("catalog", module.__all__)
