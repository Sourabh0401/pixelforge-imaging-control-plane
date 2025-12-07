from __future__ import annotations

import unittest

from pixelforge_ops.imaging import image_release_gate, lane_dashboard, lane_workflows, partner_delivery, quality_report
from pixelforge_ops.imaging import archive_readiness, partner_export_gate, metadata_policy, render_manifest


class ImagingReleaseGateAndWorkflowTests(unittest.TestCase):
    def test_partner_delivery_blocks_missing_delivery_file(self) -> None:
        manifest = render_manifest.build_render_manifest("bundle-a", "partner-format-compatibility", [])
        summary = partner_delivery.partner_delivery_summary(
            "partner-format-compatibility",
            {"files": ["manifest.json"], "codecs": ["png"]},
            manifest,
        )
        self.assertEqual(summary["status"], "block")

    def test_partner_export_summary_blocks_missing_metadata(self) -> None:
        manifest = render_manifest.build_render_manifest("bundle-a", "metadata-exif-ingest", [])
        summary = partner_export_gate.partner_export_summary("metadata-exif-ingest", {"width": 10}, [], manifest)
        self.assertEqual(summary["status"], "block")

    def test_gate_imaging_release_merges_issue_counts(self) -> None:
        gate = image_release_gate.gate_imaging_release(
            "bundle-a",
            "jpeg-codec-fidelity",
            histogram={"status": "warn", "issues": ["histogram drift exceeded warning threshold"]},
            color_delta={"status": "block", "issues": ["color delta exceeded blocking threshold"]},
        )
        self.assertEqual(gate["status"], "block")
        self.assertGreater(gate["issue_count"], 0)

    def test_merge_lane_gates_blocks_when_one_lane_blocks(self) -> None:
        merged = image_release_gate.merge_lane_gates(
            [
                {"lane": "jpeg-codec-fidelity", "status": "ok", "issues": []},
                {"lane": "color-profile-parity", "status": "block", "issues": [{"severity": "block", "lane": "color-profile-parity", "kind": "metadata", "code": "x", "message": "bad"}]},
            ]
        )
        self.assertEqual(merged["status"], "block")

    def test_render_gate_markdown_mentions_lane(self) -> None:
        text = image_release_gate.render_gate_markdown(
            {"bundle_id": "bundle-a", "lane": "jpeg-codec-fidelity", "status": "ok", "brief_lines": []}
        )
        self.assertIn("jpeg-codec-fidelity", text)

    def test_quality_report_contains_digest(self) -> None:
        report = quality_report.build_quality_report("bundle-a", "jpeg-codec-fidelity", {"status": "ok"})
        self.assertIn("digest", report)

    def test_lane_dashboard_summarizes_by_owner(self) -> None:
        summary = lane_dashboard.lane_dashboard_summary(
            [
                {"lane": "jpeg-codec-fidelity", "owner": "codec_ops", "status": "ok"},
                {"lane": "jpeg-codec-fidelity", "owner": "codec_ops", "status": "warn"},
            ]
        )
        self.assertIn("codec_ops", summary["owner_summary"])

    def test_archive_readiness_blocks_when_packet_is_red(self) -> None:
        summary = archive_readiness.archive_readiness_summary({"status": "ok"}, {"passed": True}, {"status": "red"})
        self.assertEqual(summary["status"], "block")

    def test_lane_workflow_builds_gate(self) -> None:
        payload = {
            "bundle_id": "bundle-a",
            "lane": "jpeg-codec-fidelity",
            "actual_matrix": [[(10, 10, 10)]],
            "expected_matrix": [[(10, 10, 10)]],
            "metadata": {"width": 1, "height": 1, "color_profile": "DisplayP3"},
            "artifacts": [{"path": "lane/a.png", "lane": "jpeg-codec-fidelity", "codec": "jpeg", "artifact_type": "frame"}],
            "codec_rows": [{"lane": "jpeg-codec-fidelity", "codec": "jpeg", "status": "pass", "psnr": 40, "ssim": 0.98, "runtime_ms": 12}],
        }
        summary = lane_workflows.evaluate_lane_payload(payload)
        self.assertIn("gate", summary)

    def test_metadata_policy_warns_for_bad_alpha_mode(self) -> None:
        summary = metadata_policy.metadata_policy_summary(
            {"width": 10, "height": 10, "color_profile": "DisplayP3", "alpha_mode": "mystery"},
            lane="alpha-channel-recovery",
        )
        self.assertEqual(summary["status"], "warn")

