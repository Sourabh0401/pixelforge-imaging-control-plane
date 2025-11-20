from __future__ import annotations

import unittest

from pixelforge_ops.release import build_release_manifest, manifest_to_dict, release_delta
from tests.helpers import bundle


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


