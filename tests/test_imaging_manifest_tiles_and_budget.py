from __future__ import annotations

import unittest

from pixelforge_ops.imaging import artifact_inventory, render_manifest, render_manifest_summary, tile_coverage
from pixelforge_ops.imaging import render_budget, tile_seam_audit


class ImagingManifestTilesAndBudgetTests(unittest.TestCase):
    def test_artifact_inventory_detects_missing_required_path(self) -> None:
        summary = artifact_inventory.artifact_inventory_summary(
            [{"path": "lane/a.png", "lane": "jpeg-codec-fidelity", "codec": "jpeg", "required": True, "status": "missing"}]
        )
        self.assertFalse(summary["passed"])

    def test_artifact_inventory_digest_is_stable(self) -> None:
        rows = [{"path": "lane/a.png", "lane": "jpeg-codec-fidelity", "codec": "jpeg"}]
        self.assertEqual(artifact_inventory.inventory_digest(rows), artifact_inventory.inventory_digest(rows))

    def test_tile_coverage_detects_duplicate_tile(self) -> None:
        summary = tile_coverage.tile_coverage_summary(
            [
                {"path": "a.png", "x": 0, "y": 0, "width": 10, "height": 10, "codec": "png"},
                {"path": "b.png", "x": 0, "y": 0, "width": 10, "height": 10, "codec": "png"},
            ]
        )
        self.assertEqual(summary["status"], "block")

    def test_tile_coverage_detects_missing_position(self) -> None:
        summary = tile_coverage.tile_coverage_summary(
            [{"path": "a.png", "x": 0, "y": 0, "width": 10, "height": 10, "codec": "png"}],
            expected_columns=2,
            expected_rows=1,
            tile_width=10,
            tile_height=10,
        )
        self.assertIn("missing tile", " ".join(summary["issues"]))

    def test_render_manifest_builds_digest(self) -> None:
        manifest = render_manifest.build_render_manifest(
            "bundle-a",
            "jpeg-codec-fidelity",
            [{"path": "lane/a.png", "lane": "jpeg-codec-fidelity", "codec": "jpeg", "artifact_type": "frame"}],
        )
        self.assertIn("digest", manifest)

    def test_render_manifest_summary_fails_when_digest_changes(self) -> None:
        manifest = render_manifest.build_render_manifest(
            "bundle-a",
            "jpeg-codec-fidelity",
            [{"path": "lane/a.png", "lane": "jpeg-codec-fidelity", "codec": "jpeg", "artifact_type": "frame"}],
        )
        manifest["digest"] = "bad"
        summary = render_manifest_summary(manifest)
        self.assertFalse(summary["passed"])

    def test_compare_render_manifests_detects_added_artifact(self) -> None:
        left = render_manifest.build_render_manifest("bundle-a", "jpeg-codec-fidelity", [])
        right = render_manifest.build_render_manifest(
            "bundle-a",
            "jpeg-codec-fidelity",
            [{"path": "lane/a.png", "lane": "jpeg-codec-fidelity", "codec": "jpeg", "artifact_type": "frame"}],
        )
        delta = render_manifest.compare_render_manifests(left, right)
        self.assertTrue(delta["added_artifacts"])

    def test_render_budget_blocks_large_artifact_size(self) -> None:
        summary = render_budget.summarize_budget(
            [{"artifact_type": "frame", "bytes": 2_000_000, "runtime_ms": 10}],
            "jpeg-codec-fidelity",
        )
        self.assertEqual(summary["status"], "block")

    def test_tile_seam_summary_warns_on_seam_delta(self) -> None:
        left = [[(0, 0, 0), (0, 0, 0)]]
        right = [[(10, 10, 10), (10, 10, 10)]]
        summary = tile_seam_audit.tile_seam_summary(
            [{"name": "seam-1", "left_matrix": left, "right_matrix": right}],
            warn_threshold=1.0,
            block_threshold=100.0,
        )
        self.assertEqual(summary["status"], "warn")

