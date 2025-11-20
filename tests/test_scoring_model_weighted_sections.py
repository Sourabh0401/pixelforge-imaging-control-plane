from __future__ import annotations

import unittest

from pixelforge_ops.execution import evaluate_attempt
from pixelforge_ops.scoring_model import weighted_sections
from tests.ext_helpers import attempt, bundle


class WeightedSectionsTests(unittest.TestCase):
    def test_weighted_section_totals_include_percent(self) -> None:
        item = bundle("jpeg-codec-fidelity")
        run = evaluate_attempt(item, attempt("jpeg-codec-fidelity", "mixed"))
        totals = weighted_sections.weighted_section_totals(run, item.owner)
        self.assertIn("percent", next(iter(totals.values())))

    def test_weighted_percent_is_positive(self) -> None:
        item = bundle("jpeg-codec-fidelity")
        run = evaluate_attempt(item, attempt("jpeg-codec-fidelity", "strong"))
        totals = weighted_sections.weighted_section_totals(run, item.owner)
        self.assertGreater(weighted_sections.weighted_percent(totals), 0)

    def test_weighted_section_totals_cover_known_sections(self) -> None:
        item = bundle("jpeg-codec-fidelity")
        run = evaluate_attempt(item, attempt("jpeg-codec-fidelity", "mixed"))
        totals = weighted_sections.weighted_section_totals(run, item.owner)
        self.assertIn("catalog", totals)

    def test_weighted_percent_for_strong_run_is_high(self) -> None:
        item = bundle("jpeg-codec-fidelity")
        run = evaluate_attempt(item, attempt("jpeg-codec-fidelity", "strong"))
        totals = weighted_sections.weighted_section_totals(run, item.owner)
        self.assertGreaterEqual(weighted_sections.weighted_percent(totals), 88.0)

    def test_weighted_percent_for_weak_run_is_lower(self) -> None:
        item = bundle("jpeg-codec-fidelity")
        strong = evaluate_attempt(item, attempt("jpeg-codec-fidelity", "strong"))
        weak = evaluate_attempt(item, attempt("jpeg-codec-fidelity", "weak"))
        strong_percent = weighted_sections.weighted_percent(weighted_sections.weighted_section_totals(strong, item.owner))
        weak_percent = weighted_sections.weighted_percent(weighted_sections.weighted_section_totals(weak, item.owner))
        self.assertGreater(strong_percent, weak_percent)


