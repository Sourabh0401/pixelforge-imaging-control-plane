from __future__ import annotations

from typing import Any, Mapping

from .alpha_channel_audit import audit_alpha_matrix
from .channel_histogram import histogram_summary
from .codec_matrix import best_codec, regression_codecs, summarize_codec_rows
from .codec_profile import codec_profile_summary
from .color_profile_validator import profile_summary
from .color_delta import color_delta_summary
from .exif_contract import exif_summary
from .golden_image_diff import golden_diff
from .image_release_gate import gate_imaging_release
from .metadata_policy import metadata_policy_summary
from .partner_export_gate import partner_export_summary
from .perceptual_hash import average_hash, hash_summary
from .region_diff import region_diff_summary
from .render_manifest import build_render_manifest, compare_render_manifests, render_manifest_summary
from .tile_coverage import tile_coverage_summary
from .tile_manifest import manifest_summary
from .transform_pipeline import pipeline_summary


def _contract(expected: Any) -> dict[str, object]:
    return dict(expected or {}) if isinstance(expected, Mapping) else {}


def evaluate_mode(mode: str, answer: Any, expected: Any) -> dict[str, object]:
    contract = _contract(expected)
    if mode == "pixel_matrix":
        matrix = contract.pop("matrix", expected)
        return golden_diff(
            answer,
            matrix,
            tolerance=int(contract.get("tolerance", 0)),
            max_mismatched_pixels=int(contract.get("max_mismatched_pixels", 0)),
            mean_delta_limit=contract.get("mean_delta_limit"),
        )
    if mode == "perceptual_hash":
        reference_hash = str(contract.get("hash") or average_hash(contract["matrix"]))
        return hash_summary(answer, reference_hash, max_distance=int(contract.get("max_distance", 0)))
    if mode == "channel_histogram":
        matrix = contract.pop("matrix", expected)
        return histogram_summary(
            answer,
            matrix,
            bins=int(contract.get("bins", 16)),
            warn_threshold=float(contract.get("warn_threshold", 0.03)),
            block_threshold=float(contract.get("block_threshold", 0.08)),
            dominant_shift_limit=int(contract.get("dominant_shift_limit", 2)),
        )
    if mode == "color_delta":
        matrix = contract.pop("matrix", expected)
        return color_delta_summary(
            answer,
            matrix,
            weights=contract.get("weights"),
            warn_threshold=float(contract.get("warn_threshold", 6.0)),
            block_threshold=float(contract.get("block_threshold", 18.0)),
            percentile_threshold=float(contract.get("percentile_threshold", 12.0)),
            alpha_weight=float(contract.get("alpha_weight", 2.0)),
        )
    if mode == "region_diff":
        matrix = contract.pop("matrix", expected)
        return region_diff_summary(
            answer,
            matrix,
            required_regions=tuple(contract.get("required_regions", ())),
            ignore_regions=tuple(contract.get("ignore_regions", ())),
            tolerance=int(contract.get("tolerance", 0)),
            max_mismatched_pixels=int(contract.get("max_mismatched_pixels", 0)),
            mean_delta_limit=contract.get("mean_delta_limit"),
        )
    if mode == "tile_manifest":
        summary = manifest_summary(answer)
        expected_digest = contract.get("digest")
        if expected_digest is not None and summary["digest"] != expected_digest:
            summary["issues"] = list(summary["issues"]) + ["manifest digest mismatch"]
        if "expected_tile_count" in contract:
            expected_count = int(contract["expected_tile_count"])
            if summary["tile_count"] != expected_count:
                summary["issues"] = list(summary["issues"]) + [f"tile_count expected {expected_count} but got {summary['tile_count']}"]
        summary["passed"] = not summary["issues"]
        summary["status"] = "block" if summary["issues"] else "ok"
        return summary
    if mode == "tile_coverage":
        return tile_coverage_summary(
            answer,
            expected_columns=contract.get("expected_columns"),
            expected_rows=contract.get("expected_rows"),
            tile_width=contract.get("tile_width"),
            tile_height=contract.get("tile_height"),
        )
    if mode == "render_manifest":
        if isinstance(answer, Mapping) and "artifacts" in answer:
            summary = render_manifest_summary(answer)
        else:
            manifest = build_render_manifest(
                bundle_id=str(contract.get("bundle_id", "bundle")),
                lane=str(contract.get("lane", "lane")),
                artifacts=answer,
                metadata=contract.get("metadata"),
                release_channel=contract.get("release_channel"),
            )
            summary = render_manifest_summary(manifest)
        if "digest" in contract and summary["digest"] != contract["digest"]:
            summary["issues"] = list(summary["issues"]) + ["render manifest digest mismatch"]
            summary["passed"] = False
        elif not contract.get("strict"):
            summary["passed"] = True
            summary["status"] = "ok"
        return summary
    if mode == "image_audit":
        profile = profile_summary(
            dict(answer.get("color_profile", {})),
            required_profile=contract.get("required_profile"),
            allowed_transfer_functions=tuple(contract.get("allowed_transfer_functions", ())),
            require_embedded_profile=bool(contract.get("require_embedded_profile", False)),
            allowed_gamuts=tuple(contract.get("allowed_gamuts", ())),
        )
        exif = exif_summary(
            dict(answer.get("exif", {})),
            required_fields=tuple(contract.get("required_exif", ())),
            forbidden_fields=tuple(contract.get("forbidden_exif", ())),
            numeric_ranges=contract.get("numeric_ranges"),
        )
        metadata = metadata_policy_summary(
            dict(answer.get("metadata", answer.get("exif", {}))),
            lane=str(contract.get("lane", "metadata-exif-ingest")),
            required_exif=tuple(contract.get("required_exif", ())),
            forbidden_exif=tuple(contract.get("forbidden_exif", ())),
            allowed_profiles=tuple(contract.get("allowed_profiles", ())),
        )
        alpha = audit_alpha_matrix(
            answer.get("alpha_matrix", []),
            max_color_leak=int(contract.get("max_color_leak", 0)),
            max_unpremultiplied=int(contract.get("max_unpremultiplied", 0)),
            max_edge_noise=int(contract.get("max_edge_noise", 0)),
        )
        passed = bool(profile["passed"] and exif["passed"] and alpha["passed"])
        if contract.get("metadata") or contract.get("lane"):
            passed = passed and bool(metadata["passed"])
        issues = list(profile["issues"]) + list(exif["issues"]) + list(alpha["issues"])
        if (contract.get("metadata") or contract.get("lane")) and not metadata["passed"]:
            issues.extend(metadata["issues"])
        return {
            "passed": passed,
            "status": "block" if not passed else "ok",
            "profile": profile,
            "exif": exif,
            "metadata": metadata,
            "alpha": alpha,
            "issues": issues,
        }
    if mode == "codec_summary":
        summary = summarize_codec_rows(answer)
        profile = codec_profile_summary(answer)
        reference_best = contract.get("best_codec")
        regressions = regression_codecs(summary)
        passed = True
        strict_profile = bool(contract.get("strict_profile")) or any("lane" in row for row in answer)
        if strict_profile:
            passed = profile["passed"]
        if reference_best is not None:
            passed = passed and best_codec(summary) == reference_best
        if contract.get("regression_free"):
            passed = passed and not regressions
        return {
            "passed": passed,
            "status": "block" if not passed else "ok",
            "summary": summary,
            "profile": profile,
            "best_codec": best_codec(summary),
            "regressions": regressions,
            "issues": list(profile["issues"]),
        }
    if mode == "transform_pipeline":
        return pipeline_summary(answer)
    if mode == "image_release_gate":
        metadata = metadata_policy_summary(
            dict(answer.get("metadata", {})),
            lane=str(contract.get("lane", answer.get("lane", "lane"))),
            required_exif=tuple(contract.get("required_exif", ())),
            forbidden_exif=tuple(contract.get("forbidden_exif", ())),
            allowed_profiles=tuple(contract.get("allowed_profiles", ())),
        )
        histogram = histogram_summary(answer.get("actual_matrix", []), answer.get("expected_matrix", []))
        color = color_delta_summary(answer.get("actual_matrix", []), answer.get("expected_matrix", []))
        regions = region_diff_summary(
            answer.get("actual_matrix", []),
            answer.get("expected_matrix", []),
            required_regions=tuple(contract.get("required_regions", ())),
            ignore_regions=tuple(contract.get("ignore_regions", ())),
        )
        coverage = tile_coverage_summary(answer.get("tiles", []))
        manifest = render_manifest_summary(
            build_render_manifest(
                bundle_id=str(contract.get("bundle_id", answer.get("bundle_id", "bundle"))),
                lane=str(contract.get("lane", answer.get("lane", "lane"))),
                artifacts=answer.get("artifacts", []),
                metadata=answer.get("metadata", {}),
                release_channel=contract.get("release_channel"),
            )
        )
        codecs = codec_profile_summary(answer.get("codec_rows", []))
        partner = partner_export_summary(str(contract.get("lane", answer.get("lane", "lane"))), answer.get("metadata", {}), answer.get("codec_rows", []), build_render_manifest(str(contract.get("bundle_id", answer.get("bundle_id", "bundle"))), str(contract.get("lane", answer.get("lane", "lane"))), answer.get("artifacts", []), metadata=answer.get("metadata", {}), release_channel=contract.get("release_channel")))
        return gate_imaging_release(
            str(contract.get("bundle_id", answer.get("bundle_id", "bundle"))),
            str(contract.get("lane", answer.get("lane", "lane"))),
            histogram=histogram,
            color_delta=color,
            region_diff=regions,
            tile_coverage=coverage,
            metadata_policy=metadata,
            codec_profile=codecs,
            render_manifest=manifest,
            partner_export=partner,
        )
    raise KeyError(mode)


def compare_imaging_output(mode: str, answer: Any, expected: Any) -> bool:
    return bool(evaluate_mode(mode, answer, expected)["passed"])
