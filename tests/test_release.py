from __future__ import annotations

import unittest

from pixelforge_ops.release import build_release_manifest, manifest_to_dict, release_delta
from pixelforge_ops.reporting_surfaces.release_notes import release_notes
from pixelforge_ops.scoring import score_run
from pixelforge_ops.execution import evaluate_attempt
from tests.helpers import bundle
from tests.helpers import attempt


class ReleaseTests(unittest.TestCase):
    def test_release_manifest_is_deterministic_for_same_inputs(self) -> None:
        bundles = [bundle("jpeg-codec-fidelity"), bundle("raster-transform-tiling")]
        first = build_release_manifest("release-a", bundles, created_at="2026-06-03T10:00:00Z")
        second = build_release_manifest("release-a", bundles, created_at="2026-06-03T10:00:00Z")
        self.assertEqual(first.digest, second.digest)

    def test_release_delta_detects_added_bundle(self) -> None:
        first = build_release_manifest("release-a", [bundle("jpeg-codec-fidelity")], created_at="2026-06-03T10:00:00Z")
        second = build_release_manifest(
            "release-b",
            [bundle("jpeg-codec-fidelity"), bundle("raster-transform-tiling")],
            created_at="2026-06-03T10:00:00Z",
        )
        delta = release_delta(first, second)
        self.assertEqual(delta["added"], ["raster-transform-tiling"])

    def test_manifest_to_dict_exposes_bundle_stats(self) -> None:
        manifest = build_release_manifest("release-c", [bundle("metadata-exif-ingest")], created_at="2026-06-03T10:00:00Z")
        payload = manifest_to_dict(manifest)
        self.assertIn("bundle_stats", payload)

    def test_release_notes_include_imaging_review_when_present(self) -> None:
        item = bundle("jpeg-codec-fidelity")
        run = evaluate_attempt(item, attempt("jpeg-codec-fidelity", "mixed"))
        card = score_run(run, item)
        manifest = build_release_manifest("release-c", [item], created_at="2026-06-03T10:00:00Z")
        text = release_notes(manifest, [card], {"jpeg-codec-fidelity": {"status": "warn", "issue_count": 2}})
        self.assertIn("imaging gate", text)

