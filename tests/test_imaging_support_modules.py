from __future__ import annotations

import unittest

from pixelforge_ops.imaging import frame_sampling, issue_digest, jpeg_quantization, lane_contracts, perceptual_hash
from pixelforge_ops.imaging import render_budget, tile_seam_audit, transparency_halo


class ImagingSupportModuleTests(unittest.TestCase):
    def test_lane_contract_has_required_codecs(self) -> None:
        contract = lane_contracts.lane_contract("thumbnail-generation-stability")
        self.assertTrue(contract["required_codecs"])

    def test_validate_lane_contract_accepts_generated_contract(self) -> None:
        issues = lane_contracts.validate_lane_contract(lane_contracts.lane_contract("jpeg-codec-fidelity"))
        self.assertEqual(issues, [])

    def test_sample_points_returns_center(self) -> None:
        self.assertIn((2, 2), frame_sampling.sample_points(5, 5))

    def test_edge_band_points_covers_corners(self) -> None:
        points = frame_sampling.edge_band_points(3, 3, band=1)
        self.assertIn((0, 0), points)
        self.assertIn((2, 2), points)

    def test_distance_bucket_classifies_warn(self) -> None:
        self.assertEqual(perceptual_hash.distance_bucket(3, 25), "warn")

    def test_issue_digest_is_stable(self) -> None:
        digest = issue_digest.digest_issues([{"severity": "warn", "lane": "lane-a", "kind": "metadata", "message": "x"}])
        self.assertEqual(digest, issue_digest.digest_issues([{"severity": "warn", "lane": "lane-a", "kind": "metadata", "message": "x"}]))

    def test_jpeg_quantization_blocks_high_average(self) -> None:
        summary = jpeg_quantization.quantization_summary([200] * 64)
        self.assertEqual(summary["status"], "block")

    def test_transparency_halo_counts_halo_pixels(self) -> None:
        summary = transparency_halo.transparency_halo_summary([[(20, 20, 20, 10)]], max_halo_pixels=0)
        self.assertEqual(summary["status"], "block")

    def test_render_budget_lane_budget_is_positive(self) -> None:
        budget = render_budget.budget_for_lane("jpeg-codec-fidelity")
        self.assertGreater(budget["max_runtime_ms"], 0)

    def test_seam_difference_compares_edges(self) -> None:
        value = tile_seam_audit.seam_difference([[(0, 0, 0), (2, 2, 2)]], [[(3, 3, 3), (5, 5, 5)]], "right", "left")
        self.assertGreater(value, 0)

