from __future__ import annotations

import unittest

from engineering_challenge.execution import evaluate_attempt
from engineering_challenge.scoring_model import weighted_sections
from tests.ext_helpers import attempt, bundle


class WeightedSectionsTests(unittest.TestCase):
    def test_weighted_section_totals_include_percent(self) -> None:
        item = bundle("merchant-closeout")
        run = evaluate_attempt(item, attempt("merchant-closeout", "mixed"))
        totals = weighted_sections.weighted_section_totals(run, item.owner)
        self.assertIn("percent", next(iter(totals.values())))

    def test_weighted_percent_is_positive(self) -> None:
        item = bundle("merchant-closeout")
        run = evaluate_attempt(item, attempt("merchant-closeout", "strong"))
        totals = weighted_sections.weighted_section_totals(run, item.owner)
        self.assertGreater(weighted_sections.weighted_percent(totals), 0)

    def test_weighted_section_totals_cover_known_sections(self) -> None:
        item = bundle("merchant-closeout")
        run = evaluate_attempt(item, attempt("merchant-closeout", "mixed"))
        totals = weighted_sections.weighted_section_totals(run, item.owner)
        self.assertIn("catalog", totals)

    def test_weighted_percent_for_strong_run_is_high(self) -> None:
        item = bundle("merchant-closeout")
        run = evaluate_attempt(item, attempt("merchant-closeout", "strong"))
        totals = weighted_sections.weighted_section_totals(run, item.owner)
        self.assertGreaterEqual(weighted_sections.weighted_percent(totals), 88.0)

    def test_weighted_percent_for_weak_run_is_lower(self) -> None:
        item = bundle("merchant-closeout")
        strong = evaluate_attempt(item, attempt("merchant-closeout", "strong"))
        weak = evaluate_attempt(item, attempt("merchant-closeout", "weak"))
        strong_percent = weighted_sections.weighted_percent(weighted_sections.weighted_section_totals(strong, item.owner))
        weak_percent = weighted_sections.weighted_percent(weighted_sections.weighted_section_totals(weak, item.owner))
        self.assertGreater(strong_percent, weak_percent)
