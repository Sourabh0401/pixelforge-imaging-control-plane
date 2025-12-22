from __future__ import annotations

import unittest

from pixelforge_ops.imaging import (
    artifact_reconciliation_summary,
    certification_queue,
    codec_blocker_summary,
    export_readiness_summary,
    manifest_consistency_summary,
    quality_envelope_summary,
    region_cluster_summary,
    release_story,
    render_release_story,
)


class ImagingReconciliationAndStoryTests(unittest.TestCase):
    def test_artifact_reconciliation_detects_missing_and_renamed_artifacts(self) -> None:
        expected = [
            {"path": "frame.jpeg", "lane": "jpeg-codec-fidelity", "codec": "jpeg", "artifact_type": "frame", "required": True},
            {"path": "packet.json", "lane": "jpeg-codec-fidelity", "codec": "jpeg", "artifact_type": "metadata", "required": True, "delivery_only": True},
        ]
        actual = [
            {"path": "frame-final.jpeg", "lane": "jpeg-codec-fidelity", "codec": "jpeg", "artifact_type": "frame"},
        ]
        summary = artifact_reconciliation_summary(expected, actual, blocked_lanes=["jpeg-codec-fidelity"])
        self.assertEqual(summary["status"], "block")
        self.assertGreater(len(summary["renamed_candidates"]), 0)

    def test_region_cluster_summary_groups_connected_mismatches(self) -> None:
        actual = [[0, 0, 0], [0, 8, 8], [0, 8, 8]]
        expected = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        summary = region_cluster_summary(actual, expected, tolerance=0)
        self.assertEqual(summary["cluster_count"], 1)
        self.assertEqual(summary["clusters"][0]["shape"], "filled-block")

    def test_manifest_consistency_detects_artifact_and_metadata_changes(self) -> None:
        previous = {
            "bundle_id": "bundle-a",
            "lane": "jpeg-codec-fidelity",
            "digest": "old",
            "release_channel": "internal",
            "artifacts": [{"path": "a.jpeg", "codec": "jpeg", "artifact_type": "frame"}],
            "metadata": {"profile": "srgb"},
            "lane_contract": {"required_codecs": ["jpeg"]},
        }
        current = {
            "bundle_id": "bundle-a",
            "lane": "jpeg-codec-fidelity",
            "digest": "new",
            "release_channel": "partner",
            "artifacts": [{"path": "a.webp", "codec": "webp", "artifact_type": "frame"}],
            "metadata": {"profile": "p3"},
            "lane_contract": {"required_codecs": ["jpeg", "webp"]},
        }
        summary = manifest_consistency_summary(current, previous)
        self.assertEqual(summary["status"], "block")
        self.assertIn("artifact-set-changed", summary["categories"])
        self.assertIn("release-channel-changed", summary["categories"])

    def test_codec_blocker_summary_keeps_partial_rollout_candidates(self) -> None:
        rows = [
            {"lane": "jpeg-codec-fidelity", "codec": "jpeg", "family": "jpeg", "status": "pass", "psnr": 41.0, "runtime_ms": 20},
            {"lane": "jpeg-codec-fidelity", "codec": "avif", "family": "avif", "status": "fail", "psnr": 30.0, "runtime_ms": 200, "partner_visible": True},
        ]
        summary = codec_blocker_summary(rows)
        self.assertIn("avif", summary["blocked_families"])
        self.assertIn("jpeg", summary["partial_rollout_candidates"])

    def test_quality_envelope_summary_warns_on_histogram_drift(self) -> None:
        summary = quality_envelope_summary(
            "jpeg-codec-fidelity",
            histogram={"max_delta": 0.03},
            color_delta={"mean_delta": 0.0, "p95_delta": 0.0},
            region_summary={"issues": []},
            manifest_summary={"issues": []},
        )
        self.assertIn(summary["status"], {"warn", "block"})

    def test_export_readiness_summary_scores_partner_failures(self) -> None:
        summary = export_readiness_summary(
            gate={"status": "warn"},
            partner_delivery={"status": "block"},
            partner_export={"status": "ok"},
            manifest_consistency={"status": "warn"},
            artifact_reconciliation={"status": "warn"},
        )
        self.assertEqual(summary["status"], "block")
        self.assertLess(summary["score"], 70)

    def test_release_story_renders_lane_headline_and_sections(self) -> None:
        story = release_story(
            {
                "lane": "partner-format-compatibility",
                "gate": {"status": "block", "issues": ["missing partner metadata"]},
                "export_readiness": {"band": "blocked", "actions": ["repair packet"]},
                "manifest_consistency": {"issues": ["manifest changed"]},
                "artifact_reconciliation": {"issues": ["missing artifact"]},
            }
        )
        self.assertIn("blocked", story["headline"])
        markdown = render_release_story(
            {
                "lane": "partner-format-compatibility",
                "gate": {"status": "block", "issues": ["missing partner metadata"]},
                "export_readiness": {"band": "blocked", "actions": ["repair packet"]},
                "manifest_consistency": {"issues": ["manifest changed"]},
                "artifact_reconciliation": {"issues": ["missing artifact"]},
            }
        )
        self.assertIn("repair packet", markdown)

    def test_certification_queue_prioritizes_partner_blockers(self) -> None:
        queue = certification_queue(
            [
                {"lane": "color-profile-parity", "status": "warn", "release_channel": "internal", "owner_group": "color-ops"},
                {"lane": "partner-format-compatibility", "status": "block", "release_channel": "partner", "owner_group": "partner-ops", "partner_visible": True},
            ]
        )
        self.assertEqual(queue[0]["lane"], "partner-format-compatibility")
