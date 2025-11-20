from __future__ import annotations

from typing import Any

from .alpha_channel_audit import audit_alpha_matrix
from .codec_matrix import best_codec, regression_codecs, summarize_codec_rows
from .color_profile_validator import profile_summary
from .exif_contract import exif_summary
from .golden_image_diff import golden_diff
from .perceptual_hash import average_hash, hash_summary
from .tile_manifest import manifest_summary
from .transform_pipeline import pipeline_summary


def evaluate_mode(mode: str, answer: Any, expected: Any) -> dict[str, object]:
    if mode == "pixel_matrix":
        contract = dict(expected or {})
        matrix = contract.pop("matrix", expected)
        return golden_diff(
            answer,
            matrix,
            tolerance=int(contract.get("tolerance", 0)),
            max_mismatched_pixels=int(contract.get("max_mismatched_pixels", 0)),
            mean_delta_limit=contract.get("mean_delta_limit"),
        )
    if mode == "perceptual_hash":
        contract = dict(expected or {})
        reference_hash = str(contract.get("hash") or average_hash(contract["matrix"]))
        return hash_summary(answer, reference_hash, max_distance=int(contract.get("max_distance", 0)))
    if mode == "tile_manifest":
        contract = dict(expected or {})
        summary = manifest_summary(answer)
        expected_digest = contract.get("digest")
        if expected_digest is not None and summary["digest"] != expected_digest:
            summary["issues"] = list(summary["issues"]) + ["manifest digest mismatch"]
        if "expected_tile_count" in contract:
            expected_count = int(contract["expected_tile_count"])
            if summary["tile_count"] != expected_count:
                summary["issues"] = list(summary["issues"]) + [f"tile_count expected {expected_count} but got {summary['tile_count']}"]
        summary["passed"] = not summary["issues"]
        return summary
    if mode == "image_audit":
        contract = dict(expected or {})
        color = profile_summary(
            dict(answer.get("color_profile", {})),
            required_profile=contract.get("required_profile"),
            allowed_transfer_functions=contract.get("allowed_transfer_functions"),
            require_embedded_profile=bool(contract.get("require_embedded_profile", False)),
            allowed_gamuts=contract.get("allowed_gamuts"),
        )
        exif = exif_summary(
            dict(answer.get("exif", {})),
            required_fields=tuple(contract.get("required_exif", [])),
            forbidden_fields=tuple(contract.get("forbidden_exif", [])),
            numeric_ranges=contract.get("numeric_ranges"),
        )
        alpha = audit_alpha_matrix(
            answer.get("alpha_matrix", []),
            max_color_leak=int(contract.get("max_color_leak", 0)),
            max_unpremultiplied=int(contract.get("max_unpremultiplied", 0)),
            max_edge_noise=int(contract.get("max_edge_noise", 0)),
        )
        return {
            "passed": bool(color["passed"] and exif["passed"] and alpha["passed"]),
            "color_profile": color,
            "exif": exif,
            "alpha": alpha,
        }
    if mode == "codec_summary":
        summary = summarize_codec_rows(answer)
        reference_best = expected.get("best_codec") if isinstance(expected, dict) else None
        regressions = regression_codecs(summary)
        passed = True
        if reference_best is not None:
            passed = best_codec(summary) == reference_best
        if isinstance(expected, dict) and expected.get("regression_free"):
            passed = passed and not regressions
        return {
            "passed": passed,
            "summary": summary,
            "best_codec": best_codec(summary),
            "regressions": regressions,
        }
    if mode == "transform_pipeline":
        return pipeline_summary(answer)
    raise KeyError(mode)


def compare_imaging_output(mode: str, answer: Any, expected: Any) -> bool:
    return bool(evaluate_mode(mode, answer, expected)["passed"])
