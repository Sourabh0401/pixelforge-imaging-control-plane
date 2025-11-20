from __future__ import annotations

import unittest

from pixelforge_ops.execution import evaluate_attempt
from pixelforge_ops.reporting import remediation_markdown, scorecard_markdown, scorecards_csv
from pixelforge_ops.review import remediation_queue
from pixelforge_ops.scoring import score_run
from tests.helpers import attempt, bundle


class ReportingTests(unittest.TestCase):
    def test_scorecard_markdown_contains_section_table(self) -> None:
        item = bundle("jpeg-codec-fidelity")
        run = evaluate_attempt(item, attempt("jpeg-codec-fidelity", "mixed"))
        card = score_run(run, item)
        text = scorecard_markdown(card)
        self.assertIn("| Section | Earned | Possible | Percent |", text)

    def test_scorecards_csv_emits_header(self) -> None:
        item = bundle("raster-transform-tiling")
        run = evaluate_attempt(item, attempt("raster-transform-tiling", "mixed"))
        card = score_run(run, item)
        csv_text = scorecards_csv([card])
        self.assertTrue(csv_text.startswith("run_id,bundle_id"))

    def test_remediation_markdown_handles_non_empty_queue(self) -> None:
        cards = []
        for name in ["jpeg-codec-fidelity", "raster-transform-tiling"]:
            item = bundle(name)
            run = evaluate_attempt(item, attempt(name, "mixed"))
            cards.append(score_run(run, item))
        text = remediation_markdown(remediation_queue(cards))
        self.assertIn("Remediation queue", text)


