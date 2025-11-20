from __future__ import annotations

import unittest

from pixelforge_ops.imaging import golden_image_diff, output_comparator, perceptual_hash, pixel_tolerance


class ImagingPixelAndHashingTests(unittest.TestCase):
    def test_diff_summary_counts_mismatched_pixels(self) -> None:
        actual = [[(10, 10, 10), (20, 20, 20)], [(30, 30, 30), (40, 40, 40)]]
        expected = [[(10, 10, 10), (20, 20, 20)], [(31, 30, 30), (40, 40, 40)]]
        summary = pixel_tolerance.diff_summary(actual, expected, tolerance=0)
        self.assertEqual(summary["mismatched_pixels"], 1)
        self.assertFalse(summary["passed"])

    def test_within_tolerance_accepts_small_channel_delta(self) -> None:
        actual = [[(12, 10, 10)]]
        expected = [[(10, 10, 10)]]
        self.assertTrue(pixel_tolerance.within_tolerance(actual, expected, tolerance=2))

    def test_matrix_dimensions_rejects_ragged_rows(self) -> None:
        with self.assertRaises(ValueError):
            pixel_tolerance.matrix_dimensions([[(1,)], [(1,), (2,)]])

    def test_golden_diff_reports_difference_bounds(self) -> None:
        actual = [[0, 1], [2, 3]]
        expected = [[0, 1], [2, 4]]
        summary = golden_image_diff.golden_diff(actual, expected)
        self.assertEqual(summary["min_x"], 1)
        self.assertEqual(summary["min_y"], 1)
        self.assertEqual(summary["max_x"], 1)
        self.assertEqual(summary["max_y"], 1)

    def test_average_hash_is_stable_for_same_matrix(self) -> None:
        matrix = [[0, 10], [240, 255]]
        self.assertEqual(perceptual_hash.average_hash(matrix, hash_size=2), perceptual_hash.average_hash(matrix, hash_size=2))

    def test_hash_summary_obeys_max_distance(self) -> None:
        reference = perceptual_hash.average_hash([[0, 0], [255, 255]], hash_size=2)
        summary = perceptual_hash.hash_summary([[0, 10], [250, 255]], reference, max_distance=1)
        self.assertTrue(summary["passed"])
        self.assertLessEqual(summary["distance"], 1)

    def test_compare_imaging_output_pixel_matrix_accepts_small_difference(self) -> None:
        actual = [[(12, 10, 10)]]
        expected = {"matrix": [[(10, 10, 10)]], "tolerance": 2}
        self.assertTrue(output_comparator.compare_imaging_output("pixel_matrix", actual, expected))

    def test_compare_imaging_output_perceptual_hash_uses_expected_matrix(self) -> None:
        source = [[0, 0], [255, 255]]
        expected = {"matrix": source, "max_distance": 0}
        self.assertTrue(output_comparator.compare_imaging_output("perceptual_hash", source, expected))

    def test_compare_imaging_output_codec_summary_tracks_best_codec(self) -> None:
        rows = [
            {"codec": "jpeg", "status": "pass", "psnr": 41.5, "runtime_ms": 30},
            {"codec": "webp", "status": "fail", "psnr": 37.2, "runtime_ms": 28, "regressed": True},
            {"codec": "jpeg", "status": "pass", "psnr": 42.1, "runtime_ms": 29},
        ]
        self.assertTrue(output_comparator.compare_imaging_output("codec_summary", rows, {"best_codec": "jpeg"}))
