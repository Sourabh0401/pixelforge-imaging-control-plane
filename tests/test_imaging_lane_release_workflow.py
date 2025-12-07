from __future__ import annotations

import unittest

from pixelforge_ops.imaging import evaluate_lane_payload


class ImagingLaneReleaseWorkflowTests(unittest.TestCase):
    def test_evaluate_lane_payload_includes_quality_report_and_brief(self) -> None:
        payload = {
            "bundle_id": "bundle-a",
            "lane": "jpeg-codec-fidelity",
            "actual_matrix": [[(10, 10, 10)]],
            "expected_matrix": [[(10, 10, 10)]],
            "artifacts": [{"path": "image.bin", "lane": "jpeg-codec-fidelity", "codec": "jpeg", "artifact_type": "frame"}],
            "codec_rows": [{"codec": "jpeg", "lane": "jpeg-codec-fidelity", "status": "pass", "psnr": 41.0, "runtime_ms": 30, "decode_ok": True, "encode_ok": True}],
            "metadata": {
                "width": 10,
                "height": 10,
                "color_profile": "sRGB",
                "orientation": "landscape",
                "capture_timestamp": "2026-06-01T00:00:00Z",
            },
        }
        summary = evaluate_lane_payload(payload)
        self.assertIn("quality_report", summary)
        self.assertIn("operator_brief", summary["quality_report"])

    def test_evaluate_lane_payload_tracks_partner_delivery(self) -> None:
        payload = {
            "bundle_id": "bundle-b",
            "lane": "partner-format-compatibility",
            "partner": "partner-retail-eu",
            "actual_matrix": [[(10, 10, 10)]],
            "expected_matrix": [[(10, 10, 10)]],
            "artifacts": [{"path": "image.bin", "lane": "partner-format-compatibility", "codec": "png", "artifact_type": "frame"}],
            "codec_rows": [{"codec": "png", "lane": "partner-format-compatibility", "status": "pass", "psnr": 41.0, "runtime_ms": 30, "decode_ok": True, "encode_ok": True}],
            "metadata": {
                "width": 10,
                "height": 10,
                "color_profile": "sRGB",
                "delivery_profile": "retail",
                "icc_profile": "srgb",
                "partner_contract": "retail-eu",
            },
        }
        summary = evaluate_lane_payload(payload)
        self.assertIn("partner_delivery", summary)
        self.assertIn(summary["partner_delivery"]["status"], {"ok", "block"})

    def test_evaluate_lane_payload_tracks_rollout_and_exceptions(self) -> None:
        payload = {
            "bundle_id": "bundle-c",
            "lane": "thumbnail-generation-stability",
            "release_channel": "pilot",
            "actual_matrix": [[(10, 10, 10)]],
            "expected_matrix": [[(10, 10, 10)]],
            "artifacts": [{"path": "image.bin", "lane": "thumbnail-generation-stability", "codec": "jpeg", "artifact_type": "frame"}],
            "codec_rows": [{"codec": "jpeg", "lane": "thumbnail-generation-stability", "status": "pass", "psnr": 39.0, "runtime_ms": 300, "decode_ok": True, "encode_ok": True}],
            "metadata": {
                "width": 10,
                "height": 10,
                "color_profile": "sRGB",
                "crop_mode": "fit",
                "target_aspect_ratio": "1:1",
            },
        }
        summary = evaluate_lane_payload(payload)
        self.assertIn("rollout", summary)
        self.assertIn("exceptions", summary)
        self.assertIn("lineage", summary)
