from __future__ import annotations

import unittest

from pixelforge_ops.imaging import channel_histogram, color_delta, region_diff


class ImagingHistogramColorAndRegionTests(unittest.TestCase):
    def test_histogram_summary_passes_for_identical_matrix(self) -> None:
        matrix = [[(10, 20, 30), (40, 50, 60)]]
        summary = channel_histogram.histogram_summary(matrix, matrix)
        self.assertEqual(summary["status"], "ok")

    def test_histogram_summary_warns_on_drift(self) -> None:
        actual = [[(10, 10, 10), (10, 10, 10)]]
        expected = [[(240, 240, 240), (240, 240, 240)]]
        summary = channel_histogram.histogram_summary(actual, expected, warn_threshold=0.01, block_threshold=2.0)
        self.assertEqual(summary["status"], "warn")

    def test_histogram_summary_blocks_large_drift(self) -> None:
        actual = [[(0, 0, 0), (0, 0, 0)]]
        expected = [[(255, 255, 255), (255, 255, 255)]]
        summary = channel_histogram.histogram_summary(actual, expected)
        self.assertEqual(summary["status"], "block")

    def test_histogram_overlap_score_is_one_for_same_histogram(self) -> None:
        histogram = channel_histogram.build_histogram([[(10, 10, 10)]])
        self.assertEqual(channel_histogram.histogram_overlap_score(histogram, histogram), 1.0)

    def test_color_delta_summary_passes_small_difference(self) -> None:
        actual = [[(11, 10, 10)]]
        expected = [[(10, 10, 10)]]
        summary = color_delta.color_delta_summary(actual, expected, warn_threshold=10.0, block_threshold=20.0)
        self.assertEqual(summary["status"], "ok")

    def test_color_delta_summary_warns_alpha_only_difference(self) -> None:
        actual = [[(10, 10, 10, 200)]]
        expected = [[(10, 10, 10, 210)]]
        summary = color_delta.color_delta_summary(actual, expected, warn_threshold=1.0, block_threshold=100.0)
        self.assertEqual(summary["status"], "warn")
        self.assertGreater(summary["alpha_only_pixels"], 0)

    def test_color_delta_summary_blocks_dimension_mismatch(self) -> None:
        summary = color_delta.color_delta_summary([[0]], [[0], [1]])
        self.assertEqual(summary["status"], "block")

    def test_percentile_returns_interpolated_value(self) -> None:
        value = color_delta.percentile([1, 2, 3, 4], 50)
        self.assertEqual(value, 2.5)

    def test_region_diff_summary_blocks_missing_required_region(self) -> None:
        actual = [[0, 1], [2, 3]]
        expected = [[0, 1], [2, 3]]
        summary = region_diff.region_diff_summary(actual, expected, required_regions=({"name": "crop", "x": 9, "y": 9, "width": 1, "height": 1},))
        self.assertEqual(summary["status"], "block")

    def test_region_diff_summary_tracks_required_region_mismatch(self) -> None:
        actual = [[0, 1], [2, 8]]
        expected = [[0, 1], [2, 3]]
        summary = region_diff.region_diff_summary(
            actual,
            expected,
            required_regions=({"name": "bottom-right", "x": 1, "y": 1, "width": 1, "height": 1},),
        )
        self.assertEqual(summary["status"], "block")
        self.assertIn("bottom-right", summary["issues"][0])

    def test_region_diff_summary_passes_matching_region(self) -> None:
        actual = [[0, 1], [2, 3]]
        expected = [[0, 1], [2, 3]]
        summary = region_diff.region_diff_summary(
            actual,
            expected,
            required_regions=({"name": "whole", "x": 0, "y": 0, "width": 2, "height": 2},),
        )
        self.assertTrue(summary["passed"])
