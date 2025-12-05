from __future__ import annotations

import unittest

from pixelforge_ops.imaging import (
    build_operator_brief,
    canary_plan,
    comparator_thresholds,
    exception_summary,
    issue_rollup,
    lineage_summary,
    partner_matrix,
    partner_requirements,
    render_operator_brief,
    threshold_profile_summary,
    validate_partner_delivery,
)
from pixelforge_ops.imaging.frame_sampling import alpha_candidate_points, edge_band_points, region_sample_points, sample_points, seam_points
from pixelforge_ops.imaging.artifact_lineage import changed_paths
from pixelforge_ops.imaging.issue_taxonomy import classify_issue_messages, issue_family, issue_owner, issue_severity
from pixelforge_ops.imaging.quality_report import build_quality_report, render_quality_report_markdown
from pixelforge_ops.imaging.rollout_policy import rollout_summary
from pixelforge_ops.imaging.threshold_profiles import metadata_policy_contract, release_matrix, render_budget_policy, sampling_policy, validate_threshold_override


class ImagingPoliciesAndBriefsTests(unittest.TestCase):
    def test_threshold_profile_summary_includes_release_blockers(self) -> None:
        summary = threshold_profile_summary("jpeg-codec-fidelity")
        self.assertIn("render-manifest", summary["release_blockers"])

    def test_comparator_thresholds_read_color_delta_contract(self) -> None:
        contract = comparator_thresholds("color-profile-parity", "color_delta")
        self.assertLess(contract["warn_threshold"], contract["block_threshold"])

    def test_sampling_policy_and_metadata_contract_are_available(self) -> None:
        self.assertIn("required_regions", sampling_policy("thumbnail-generation-stability"))
        self.assertIn("required_fields", metadata_policy_contract("partner-format-compatibility"))

    def test_render_budget_policy_and_release_matrix_expose_lane_context(self) -> None:
        self.assertIn("max_runtime_ms", render_budget_policy("batch-render-telemetry"))
        self.assertTrue(any(row["lane"] == "jpeg-codec-fidelity" for row in release_matrix()))

    def test_validate_threshold_override_rejects_negative_values(self) -> None:
        issues = validate_threshold_override("jpeg-codec-fidelity", "pixel_matrix", {"tolerance": -1})
        self.assertTrue(any("non-negative" in issue for issue in issues))

    def test_issue_rollup_counts_owner_groups(self) -> None:
        rollup = issue_rollup(["render-manifest", "codec-profile", "codec-profile"])
        self.assertIn("codec-ops", rollup["owner_counts"])

    def test_issue_classification_routes_tile_messages(self) -> None:
        codes = classify_issue_messages(["missing tile at 0,0", "manifest digest mismatch"])
        self.assertEqual(codes[0], "tile-coverage")
        self.assertEqual(codes[1], "render-manifest")

    def test_issue_helpers_return_family_owner_and_severity(self) -> None:
        self.assertEqual(issue_family("partner-export"), "partner-delivery")
        self.assertEqual(issue_owner("partner-export"), "partner-ops")
        self.assertEqual(issue_severity("partner-export"), "block")

    def test_validate_partner_delivery_detects_missing_codec(self) -> None:
        summary = validate_partner_delivery(
            "partner-retail-eu",
            "partner-format-compatibility",
            files=["render.json", "quality.md", "issues.json", "image.bin"],
            codecs=["png"],
            metadata={"width": 10, "height": 10, "color_profile": "sRGB", "delivery_profile": "web", "icc_profile": "srgb", "partner_contract": "retail"},
        )
        self.assertFalse(summary["passed"])

    def test_partner_requirements_include_files_and_codecs(self) -> None:
        requirements = partner_requirements("partner-marketplace-us", "export-pipeline-integrity")
        self.assertIn("issues.json", requirements["required_files"])
        self.assertIn("png", requirements["required_codecs"])

    def test_partner_matrix_groups_status_by_partner(self) -> None:
        matrix = partner_matrix(
            [
                {"partner": "p-a", "lane": "jpeg-codec-fidelity", "status": "ok", "issues": []},
                {"partner": "p-a", "lane": "color-profile-parity", "status": "warn", "issues": ["delta"]},
                {"partner": "p-b", "lane": "partner-format-compatibility", "status": "block", "issues": ["export"]},
            ]
        )
        self.assertEqual(matrix["partners"]["p-b"]["status"], "block")

    def test_rollout_summary_marks_blocking_codec(self) -> None:
        summary = rollout_summary(
            [{"codec": "jpeg", "psnr": 32.0, "runtime_ms": 1000, "status": "pass", "decode_ok": True}],
            "jpeg-codec-fidelity",
            "internal",
        )
        self.assertEqual(summary["status"], "block")

    def test_canary_plan_uses_policy_percent(self) -> None:
        plan = canary_plan("partner-format-compatibility", ["png"], "partner")
        self.assertEqual(plan[0]["canary_percent"], 10)

    def test_exception_summary_downgrades_allowed_issue(self) -> None:
        summary = exception_summary("jpeg-codec-fidelity", [{"code": "manifest-exception"}])
        self.assertEqual(summary["status"], "warn")

    def test_operator_brief_includes_questions_and_owners(self) -> None:
        brief = build_operator_brief("thumbnail-generation-stability", ["render-manifest", "codec-profile"], "block")
        self.assertIn("release-ops", brief["owners"])
        self.assertGreater(len(brief["questions"]), 0)

    def test_render_operator_brief_mentions_lane_and_codes(self) -> None:
        text = render_operator_brief("jpeg-codec-fidelity", ["codec-profile"], "warn")
        self.assertIn("jpeg-codec-fidelity", text)
        self.assertIn("codec-profile", text)

    def test_quality_report_includes_operator_brief_and_threshold_profile(self) -> None:
        report = build_quality_report(
            "bundle-a",
            "jpeg-codec-fidelity",
            gate={"status": "warn", "issues": ["manifest digest mismatch"], "blocked_count": 0, "warn_count": 1},
            render_manifest={"status": "warn", "issues": ["manifest digest mismatch"]},
        )
        self.assertIn("operator_brief", report)
        self.assertIn("threshold_profile", report)

    def test_quality_report_markdown_mentions_profile_and_issues(self) -> None:
        report = build_quality_report(
            "bundle-a",
            "jpeg-codec-fidelity",
            gate={"status": "warn", "issues": ["manifest digest mismatch"], "blocked_count": 0, "warn_count": 1},
            render_manifest={"status": "warn", "issues": ["manifest digest mismatch"]},
        )
        text = render_quality_report_markdown(report)
        self.assertIn("Threshold profile", text)
        self.assertIn("manifest digest mismatch", text)

    def test_frame_sampling_helpers_cover_edges_regions_and_alpha(self) -> None:
        self.assertIn((0, 0), sample_points(9, 9))
        self.assertIn((0, 0), edge_band_points(3, 3))
        self.assertIn((2, 2), region_sample_points({"x": 2, "y": 2, "width": 2, "height": 2}))
        self.assertIn((0, 0), alpha_candidate_points([[(0, 0, 0, 120)]]))

    def test_seam_points_include_neighbor_columns_and_rows(self) -> None:
        points = seam_points(4, 4, 2, 2)
        self.assertIn((3, 0), points)
        self.assertIn((4, 0), points)

    def test_lineage_summary_tracks_changed_paths(self) -> None:
        manifests = [
            {"bundle_id": "b", "lane": "jpeg-codec-fidelity", "digest": "one", "artifacts": [{"path": "a.png", "codec": "png", "artifact_type": "frame"}]},
            {"bundle_id": "b", "lane": "jpeg-codec-fidelity", "digest": "two", "artifacts": [{"path": "a.png", "codec": "webp", "artifact_type": "frame"}]},
        ]
        self.assertIn("a.png", changed_paths(manifests))
        self.assertEqual(lineage_summary(manifests)["path_count"], 1)
