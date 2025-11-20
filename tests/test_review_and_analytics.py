from __future__ import annotations

import unittest

from pixelforge_ops.analytics import difficulty_drift, release_readiness
from pixelforge_ops.execution import evaluate_attempt
from pixelforge_ops.review import owner_hotspots, remediation_queue
from pixelforge_ops.scoring import score_run
from tests.helpers import attempt, bundle


class ReviewAnalyticsTests(unittest.TestCase):
    def test_remediation_queue_sorts_low_scores_first(self) -> None:
        cards = []
        for name in ["metadata-exif-ingest", "alpha-channel-recovery"]:
            item = bundle(name)
            run = evaluate_attempt(item, attempt(name, "weak"))
            cards.append(score_run(run, item))
        queue = remediation_queue(cards)
        self.assertGreaterEqual(len(queue), 1)

    def test_owner_hotspots_groups_runs(self) -> None:
        item = bundle("jpeg-codec-fidelity")
        cards = [score_run(evaluate_attempt(item, attempt("jpeg-codec-fidelity", mode)), item) for mode in ("mixed", "strong")]
        hotspots = owner_hotspots(cards)
        self.assertIn("codec_ops", hotspots)

    def test_difficulty_drift_compares_old_and_new_scorecards(self) -> None:
        item = bundle("raster-transform-tiling")
        previous = [score_run(evaluate_attempt(item, attempt("raster-transform-tiling", "weak")), item)]
        current = [score_run(evaluate_attempt(item, attempt("raster-transform-tiling", "strong")), item)]
        drift = difficulty_drift(previous, current)
        self.assertGreater(drift["raster-transform-tiling"], 0)

    def test_release_readiness_requires_average_and_no_blocked(self) -> None:
        item = bundle("jpeg-codec-fidelity")
        cards = [score_run(evaluate_attempt(item, attempt("jpeg-codec-fidelity", "strong")), item)]
        readiness = release_readiness(cards)
        self.assertTrue(readiness["ready"])


