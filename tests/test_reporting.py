from __future__ import annotations

import unittest

from engineering_challenge.execution import evaluate_attempt
from engineering_challenge.reporting import remediation_markdown, scorecard_markdown, scorecards_csv
from engineering_challenge.review import remediation_queue
from engineering_challenge.scoring import score_run
from tests.helpers import attempt, bundle


class ReportingTests(unittest.TestCase):
    def test_scorecard_markdown_contains_section_table(self) -> None:
        item = bundle("merchant-closeout")
        run = evaluate_attempt(item, attempt("merchant-closeout", "mixed"))
        card = score_run(run, item)
        text = scorecard_markdown(card)
        self.assertIn("| Section | Earned | Possible | Percent |", text)

    def test_scorecards_csv_emits_header(self) -> None:
        item = bundle("warehouse-routing")
        run = evaluate_attempt(item, attempt("warehouse-routing", "mixed"))
        card = score_run(run, item)
        csv_text = scorecards_csv([card])
        self.assertTrue(csv_text.startswith("run_id,bundle_id"))

    def test_remediation_markdown_handles_non_empty_queue(self) -> None:
        cards = []
        for name in ["merchant-closeout", "warehouse-routing"]:
            item = bundle(name)
            run = evaluate_attempt(item, attempt(name, "mixed"))
            cards.append(score_run(run, item))
        text = remediation_markdown(remediation_queue(cards))
        self.assertIn("Remediation queue", text)
