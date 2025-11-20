from __future__ import annotations

import unittest

from pixelforge_ops.imaging import (
    alpha_channel_audit,
    color_profile_validator,
    exif_contract,
    output_comparator,
    tile_manifest,
    transform_pipeline,
)


class ImagingAuditAndManifestTests(unittest.TestCase):
    def test_validate_profile_requires_embedded_profile(self) -> None:
        issues = color_profile_validator.validate_profile({"profile_name": "Display P3"}, required_profile="Display P3", require_embedded_profile=True)
        self.assertIn("embedded_profile missing", issues)

    def test_profile_summary_passes_matching_profile(self) -> None:
        summary = color_profile_validator.profile_summary(
            {"profile_name": "Display P3", "embedded_profile": True, "transfer_function": "srgb", "gamut": "p3"},
            required_profile="Display P3",
            allowed_transfer_functions=["srgb"],
            require_embedded_profile=True,
            allowed_gamuts=["p3"],
        )
        self.assertTrue(summary["passed"])

    def test_validate_exif_metadata_reports_missing_and_range(self) -> None:
        issues = exif_contract.validate_exif_metadata({"iso": "40"}, required_fields=["camera_model"], numeric_ranges={"iso": {"min": 80, "max": 3200}})
        self.assertTrue(any("camera_model" in issue for issue in issues))
        self.assertTrue(any("iso outside range" in issue for issue in issues))

    def test_exif_summary_lists_present_fields(self) -> None:
        summary = exif_contract.exif_summary({"camera_model": "A7C", "iso": 200}, required_fields=["camera_model"])
        self.assertIn("camera_model", summary["present_fields"])

    def test_transparent_edge_summary_counts_color_leaks(self) -> None:
        matrix = [[(12, 0, 0, 0), (0, 0, 0, 255)], [(0, 0, 0, 128), (0, 0, 0, 255)]]
        summary = alpha_channel_audit.transparent_edge_summary(matrix)
        self.assertEqual(summary["color_leak_pixels"], 1)
        self.assertGreaterEqual(summary["edge_noise_pixels"], 1)

    def test_audit_alpha_matrix_rejects_unpremultiplied_pixels(self) -> None:
        matrix = [[(200, 0, 0, 120)]]
        summary = alpha_channel_audit.audit_alpha_matrix(matrix, max_unpremultiplied=0)
        self.assertFalse(summary["passed"])

    def test_validate_tile_manifest_detects_duplicate_paths(self) -> None:
        issues = tile_manifest.validate_tile_manifest(
            [{"zoom": 1, "x": 0, "y": 0, "path": "a.png"}, {"zoom": 1, "x": 0, "y": 1, "path": "a.png"}]
        )
        self.assertTrue(any("duplicate tile path" in issue for issue in issues))

    def test_manifest_digest_ignores_input_order(self) -> None:
        left = [{"zoom": 2, "x": 1, "y": 0, "path": "b.png"}, {"zoom": 1, "x": 0, "y": 0, "path": "a.png"}]
        right = list(reversed(left))
        self.assertEqual(tile_manifest.manifest_digest(left), tile_manifest.manifest_digest(right))

    def test_compare_imaging_output_tile_manifest_uses_expected_digest(self) -> None:
        manifest = [{"zoom": 1, "x": 0, "y": 0, "path": "tile-0.png"}]
        expected = {"digest": tile_manifest.manifest_digest(manifest), "expected_tile_count": 1}
        self.assertTrue(output_comparator.compare_imaging_output("tile_manifest", manifest, expected))

    def test_validate_transform_chain_rejects_crop_enlarge(self) -> None:
        issues = transform_pipeline.validate_transform_chain(
            [{"operation": "decode", "width": 100, "height": 80}, {"operation": "crop", "width": 120, "height": 80}]
        )
        self.assertTrue(any("crop enlarged" in issue for issue in issues))

    def test_compare_imaging_output_image_audit_checks_color_exif_and_alpha(self) -> None:
        answer = {
            "color_profile": {"profile_name": "Display P3", "embedded_profile": True, "transfer_function": "srgb", "gamut": "p3"},
            "exif": {"camera_model": "A7C", "iso": 400},
            "alpha_matrix": [[(0, 0, 0, 0), (0, 0, 0, 255)]],
        }
        expected = {
            "required_profile": "Display P3",
            "allowed_transfer_functions": ["srgb"],
            "require_embedded_profile": True,
            "allowed_gamuts": ["p3"],
            "required_exif": ["camera_model"],
            "numeric_ranges": {"iso": {"min": 100, "max": 1600}},
            "max_color_leak": 0,
        }
        self.assertTrue(output_comparator.compare_imaging_output("image_audit", answer, expected))

    def test_compare_imaging_output_transform_pipeline_respects_stage_rules(self) -> None:
        stages = [
            {"operation": "decode", "width": 1600, "height": 1200},
            {"operation": "resize", "width": 800, "height": 600},
            {"operation": "encode", "width": 800, "height": 600},
        ]
        self.assertTrue(output_comparator.compare_imaging_output("transform_pipeline", stages, {}))
