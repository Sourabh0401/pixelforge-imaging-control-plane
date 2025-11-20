from __future__ import annotations

import unittest

from pixelforge_ops.execution import evaluate_attempt
from pixelforge_ops.scoring import score_run
from pixelforge_ops.scoring_model import drift
from tests.ext_helpers import attempt, bundle


class DriftTests(unittest.TestCase):
    def test_percent_drift_positive_for_strong_over_weak(self) -> None:
        item = bundle("raster-transform-tiling")
        previous = [score_run(evaluate_attempt(item, attempt("raster-transform-tiling", "weak")), item)]
        current = [score_run(evaluate_attempt(item, attempt("raster-transform-tiling", "strong")), item)]
        values = drift.percent_drift(previous, current)
        self.assertGreater(values["raster-transform-tiling"], 0)

    def test_hidden_drift_uses_hidden_percent(self) -> None:
        item = bundle("raster-transform-tiling")
        previous = [score_run(evaluate_attempt(item, attempt("raster-transform-tiling", "weak")), item)]
        current = [score_run(evaluate_attempt(item, attempt("raster-transform-tiling", "strong")), item)]
        values = drift.hidden_drift(previous, current)
        self.assertIn("raster-transform-tiling", values)

    def test_drift_alerts_only_raise_large_moves(self) -> None:
        item = bundle("raster-transform-tiling")
        previous = [score_run(evaluate_attempt(item, attempt("raster-transform-tiling", "weak")), item)]
        current = [score_run(evaluate_attempt(item, attempt("raster-transform-tiling", "strong")), item)]
        self.assertTrue(drift.drift_alerts(previous, current))

    def test_by_bundle_maps_scorecards(self) -> None:
        item = bundle("jpeg-codec-fidelity")
        cards = [score_run(evaluate_attempt(item, attempt("jpeg-codec-fidelity", "mixed")), item)]
        self.assertIn("jpeg-codec-fidelity", drift.by_bundle(cards))


