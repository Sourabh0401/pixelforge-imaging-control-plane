from __future__ import annotations

import unittest

from pixelforge_ops.cataloging import policy_catalog
from pixelforge_ops.execution import evaluate_attempt
from pixelforge_ops.execution_engine import comparator
from pixelforge_ops.models import AssessmentCase, ExerciseBundle
from pixelforge_ops.validator import validate_bundle
from tests.helpers import bundle


class ExecutionEngineImagingTests(unittest.TestCase):
    def test_compare_dispatches_image_audit(self) -> None:
        answer = {
            "color_profile": {"profile_name": "Display P3", "embedded_profile": True, "transfer_function": "srgb", "gamut": "p3"},
            "exif": {"camera_model": "A7C"},
            "alpha_matrix": [[(0, 0, 0, 0)]],
        }
        expected = {"required_profile": "Display P3", "allowed_transfer_functions": ["srgb"], "required_exif": ["camera_model"]}
        self.assertTrue(comparator.compare("image_audit", answer, expected))

    def test_compare_dispatches_transform_pipeline(self) -> None:
        stages = [
            {"operation": "decode", "width": 1200, "height": 800},
            {"operation": "resize", "width": 600, "height": 400},
            {"operation": "encode", "width": 600, "height": 400},
        ]
        self.assertTrue(comparator.compare("transform_pipeline", stages, {}))

    def test_compare_dispatches_channel_histogram(self) -> None:
        matrix = [[(10, 10, 10), (20, 20, 20)]]
        self.assertTrue(comparator.compare("channel_histogram", matrix, {"matrix": matrix}))

    def test_compare_dispatches_color_delta(self) -> None:
        matrix = [[(10, 10, 10)]]
        self.assertTrue(comparator.compare("color_delta", matrix, {"matrix": matrix}))

    def test_compare_dispatches_region_diff(self) -> None:
        matrix = [[0, 1], [2, 3]]
        expected = {"matrix": matrix, "required_regions": [{"name": "all", "x": 0, "y": 0, "width": 2, "height": 2}]}
        self.assertTrue(comparator.compare("region_diff", matrix, expected))

    def test_compare_dispatches_tile_coverage(self) -> None:
        tiles = [{"path": "a.png", "x": 0, "y": 0, "width": 8, "height": 8, "codec": "png"}]
        self.assertTrue(comparator.compare("tile_coverage", tiles, {}))

    def test_compare_dispatches_render_manifest(self) -> None:
        artifacts = [{"path": "a.png", "lane": "jpeg-codec-fidelity", "codec": "jpeg", "artifact_type": "frame"}]
        self.assertTrue(comparator.compare("render_manifest", artifacts, {"bundle_id": "bundle-a", "lane": "jpeg-codec-fidelity"}))

    def test_validator_accepts_new_imaging_comparator(self) -> None:
        item = bundle("jpeg-codec-fidelity")
        case = AssessmentCase(
            case_id="imaging-case-001",
            section="execution",
            comparator="pixel_matrix",
            difficulty="core",
            hidden=False,
            weight=1.0,
            time_limit_ms=900,
            input_payload={"prompt_key": "imaging:1"},
            expected={"matrix": [[0]], "tolerance": 1},
            tags=("codec",),
        )
        candidate = ExerciseBundle(
            bundle_id=item.bundle_id,
            version=item.version,
            domain=item.domain,
            owner=item.owner,
            title=item.title,
            tags=item.tags,
            rubric=item.rubric,
            metadata=item.metadata,
            cases=(case,),
            root=item.root,
        )
        issues = validate_bundle(candidate)
        self.assertFalse(any(issue.code == "unknown-comparator" for issue in issues))

    def test_evaluate_attempt_supports_pixel_matrix_case(self) -> None:
        case = AssessmentCase(
            case_id="pixel-case",
            section="execution",
            comparator="pixel_matrix",
            difficulty="core",
            hidden=False,
            weight=1.0,
            time_limit_ms=900,
            input_payload={"prompt_key": "imaging:pixel"},
            expected={"matrix": [[(10, 10, 10)]], "tolerance": 2},
            tags=("codec",),
        )
        item = ExerciseBundle(
            bundle_id="jpeg-codec-fidelity",
            version="2026.06",
            domain="codec_ops",
            owner="codec_ops",
            title="JPEG codec fidelity and quantization drift",
            tags=("codec", "jpeg"),
            rubric={"public_weight": 1.0, "hidden_weight": 1.25},
            metadata={"release_channel": "internal", "author": "codec_ops", "last_reviewed_at": "2026-05-28T12:00:00Z", "notes": "pixel pass"},
            cases=(case,),
        )
        run = evaluate_attempt(
            item,
            {
                "run_id": "pixel-run",
                "participant_id": "p-1",
                "case_results": [{"case_id": "pixel-case", "runtime_ms": 250, "answer": [[(11, 10, 10)]]}],
            },
        )
        self.assertEqual(run.case_results[0].status, "pass")

    def test_policy_catalog_exposes_pixel_matrix_contract(self) -> None:
        contract = policy_catalog.comparator_policy("pixel_matrix")
        self.assertEqual(contract["input_shape"], "matrix")

    def test_policy_catalog_exposes_image_release_gate_contract(self) -> None:
        contract = policy_catalog.comparator_policy("image_release_gate")
        self.assertEqual(contract["input_shape"], "mapping")

    def test_catalog_manifest_titles_are_imaging_specific(self) -> None:
        item = bundle("thumbnail-generation-stability")
        self.assertIn("thumbnail", item.title.lower())

    def test_bundle_notes_reference_imaging_terms(self) -> None:
        item = bundle("alpha-channel-recovery")
        self.assertIn("transparent", item.root.joinpath("bundle_notes.md").read_text(encoding="utf-8").lower())
