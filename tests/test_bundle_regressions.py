from __future__ import annotations

import unittest

from pixelforge_ops.execution import evaluate_attempt
from pixelforge_ops.scoring import score_run
from tests.ext_helpers import attempt, bundle


BUNDLES = {
    "jpeg-codec-fidelity": {"owner": "codec_ops", "tag": "codec", "phrase": "JPEG codec"},
    "raster-transform-tiling": {"owner": "raster_ops", "tag": "raster", "phrase": "Raster transform"},
    "metadata-exif-ingest": {"owner": "partner_ops", "tag": "metadata", "phrase": "Metadata EXIF"},
    "alpha-channel-recovery": {"owner": "archive_ops", "tag": "alpha", "phrase": "Alpha channel"},
    "sprite-identity-refresh": {"owner": "image_quality_ops", "tag": "sprite", "phrase": "Sprite identity"},
    "batch-render-telemetry": {"owner": "release_program_ops", "tag": "telemetry", "phrase": "Batch render"},
    "color-profile-parity": {"owner": "color_ops", "tag": "color", "phrase": "Color profile"},
    "export-pipeline-integrity": {"owner": "pipeline_ops", "tag": "export", "phrase": "Export pipeline"},
    "thumbnail-generation-stability": {"owner": "metadata_ops", "tag": "thumbnail", "phrase": "Thumbnail generation"},
    "partner-format-compatibility": {"owner": "export_ops", "tag": "partner", "phrase": "Partner format"},
    "compression-preset-handoff": {"owner": "launch_ops", "tag": "compression", "phrase": "Compression preset"},
    "decoder-recovery-replay": {"owner": "qa_ops", "tag": "decoder", "phrase": "Decoder recovery"},
}


class BundleRegressionTests(unittest.TestCase):
    def test_bundles_load_expected_metadata(self) -> None:
        for name, expected in BUNDLES.items():
            with self.subTest(bundle=name):
                item = bundle(name)
                self.assertEqual(item.bundle_id, name)
                self.assertEqual(item.owner, expected["owner"])
                self.assertIn(expected["tag"], item.tags)
                self.assertIn("release", item.tags)
                self.assertEqual(item.metadata["release_channel"], "internal")
                self.assertIn(expected["phrase"].lower(), item.title.lower())

    def test_bundles_have_hidden_and_public_cases(self) -> None:
        for name in BUNDLES:
            with self.subTest(bundle=name):
                item = bundle(name)
                self.assertTrue(item.hidden_cases())
                self.assertTrue(item.public_cases())
                self.assertGreaterEqual(len(item.sections()), 4)

    def test_strong_profiles_outperform_weak_profiles(self) -> None:
        for name in BUNDLES:
            with self.subTest(bundle=name):
                item = bundle(name)
                strong = score_run(evaluate_attempt(item, attempt(name, "strong")), item)
                weak = score_run(evaluate_attempt(item, attempt(name, "weak")), item)
                self.assertGreater(strong.percent, weak.percent)
                self.assertGreater(strong.hidden_percent, weak.hidden_percent)
                self.assertGreaterEqual(strong.percent, 88.0)

    def test_mixed_profiles_stay_blocked_for_operator_review(self) -> None:
        for name in BUNDLES:
            with self.subTest(bundle=name):
                item = bundle(name)
                mixed = score_run(evaluate_attempt(item, attempt(name, "mixed")), item)
                self.assertEqual(mixed.band, "blocked")
                self.assertIn("requires-review", mixed.policy_flags)
                self.assertGreater(mixed.public_percent, mixed.hidden_percent)

    def test_jpeg_codec_bundle_keeps_audit_section_visible(self) -> None:
        item = bundle("jpeg-codec-fidelity")
        self.assertIn("audit", item.sections())
        self.assertIn("quantization", item.metadata["notes"].lower())

    def test_raster_transform_bundle_mentions_crop_in_operator_notes(self) -> None:
        item = bundle("raster-transform-tiling")
        self.assertIn("crop", item.metadata["notes"].lower())
        self.assertEqual(item.domain, "raster_ops")

    def test_metadata_exif_bundle_preserves_ingest_language(self) -> None:
        item = bundle("metadata-exif-ingest")
        self.assertIn("exif", item.metadata["notes"].lower())
        self.assertEqual(item.domain, "partner_ops")

    def test_decoder_recovery_scorecard_keeps_decoder_owner(self) -> None:
        item = bundle("decoder-recovery-replay")
        card = score_run(evaluate_attempt(item, attempt("decoder-recovery-replay", "mixed")), item)
        self.assertEqual(card.owner, "qa_ops")
        self.assertGreater(card.percent, 40.0)

