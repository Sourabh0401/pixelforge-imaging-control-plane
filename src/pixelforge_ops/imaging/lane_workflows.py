from __future__ import annotations

from typing import Mapping

from .artifact_lineage import lineage_summary
from .channel_histogram import histogram_summary
from .codec_profile import codec_profile_summary
from .color_delta import color_delta_summary
from .image_release_gate import gate_imaging_release
from .manifest_exceptions import exception_summary
from .metadata_policy import metadata_policy_summary
from .partner_profiles import validate_partner_delivery
from .partner_export_gate import partner_export_summary
from .quality_report import build_quality_report
from .region_diff import region_diff_summary
from .render_manifest import build_render_manifest, render_manifest_summary
from .rollout_policy import rollout_summary
from .threshold_profiles import comparator_thresholds, render_budget_policy, threshold_profile_summary
from .tile_coverage import tile_coverage_summary


def evaluate_lane_payload(payload: Mapping[str, object]) -> dict[str, object]:
    lane = str(payload.get("lane", "lane"))
    bundle_id = str(payload.get("bundle_id", "bundle"))
    actual_matrix = payload.get("actual_matrix", [])
    expected_matrix = payload.get("expected_matrix", [])
    histogram_contract = comparator_thresholds(lane, "channel_histogram")
    histogram = histogram_summary(
        actual_matrix,
        expected_matrix,
        bins=int(histogram_contract.get("bins", 16)),
        warn_threshold=float(histogram_contract.get("warn_threshold", 0.03)),
        block_threshold=float(histogram_contract.get("block_threshold", 0.08)),
        dominant_shift_limit=int(histogram_contract.get("dominant_shift_limit", 2)),
    )
    delta_contract = comparator_thresholds(lane, "color_delta")
    color = color_delta_summary(
        actual_matrix,
        expected_matrix,
        weights=delta_contract.get("weights"),
        warn_threshold=float(delta_contract.get("warn_threshold", 6.0)),
        block_threshold=float(delta_contract.get("block_threshold", 18.0)),
        percentile_threshold=float(delta_contract.get("percentile_threshold", 12.0)),
        alpha_weight=float(delta_contract.get("alpha_weight", 2.0)),
    )
    regions = region_diff_summary(
        actual_matrix,
        expected_matrix,
        required_regions=tuple(payload.get("required_regions", ())),
        ignore_regions=tuple(payload.get("ignore_regions", ())),
    )
    tiles = tile_coverage_summary(
        payload.get("tiles", []),
        expected_columns=payload.get("expected_columns"),
        expected_rows=payload.get("expected_rows"),
        tile_width=payload.get("tile_width"),
        tile_height=payload.get("tile_height"),
    )
    metadata = metadata_policy_summary(
        payload.get("metadata", {}),
        lane=lane,
        required_exif=tuple(payload.get("required_exif", ())),
        forbidden_exif=tuple(payload.get("forbidden_exif", ())),
        allowed_profiles=tuple(payload.get("allowed_profiles", ())),
    )
    manifest = build_render_manifest(
        bundle_id=bundle_id,
        lane=lane,
        artifacts=payload.get("artifacts", []),
        metadata=payload.get("metadata", {}),
        release_channel=payload.get("release_channel"),
    )
    manifest_summary = render_manifest_summary(manifest)
    codecs = codec_profile_summary(payload.get("codec_rows", []))
    partner = partner_export_summary(lane, payload.get("metadata", {}), payload.get("codec_rows", []), manifest)
    partner_delivery = validate_partner_delivery(
        str(payload.get("partner", "partner-retail-eu")),
        lane,
        files=[str(row.get("path", "")) for row in payload.get("artifacts", [])] + ["render.json", "quality.md", "issues.json"],
        codecs=[str(row.get("codec", "")) for row in payload.get("codec_rows", [])],
        metadata=payload.get("metadata", {}),
    )
    rollout = rollout_summary(payload.get("codec_rows", []), lane, str(payload.get("release_channel", threshold_profile_summary(lane)["release_channel"])))
    gate = gate_imaging_release(
        bundle_id,
        lane,
        histogram=histogram,
        color_delta=color,
        region_diff=regions,
        tile_coverage=tiles,
        metadata_policy=metadata,
        codec_profile=codecs,
        render_manifest=manifest_summary,
        partner_export=partner,
    )
    exceptions = exception_summary(lane, [{"code": code} for code in gate.get("issue_codes", [])])
    lineage = lineage_summary([manifest])
    quality_report = build_quality_report(
        bundle_id,
        lane,
        gate=gate,
        histogram=histogram,
        color_delta=color,
        region_diff=regions,
        tile_coverage=tiles,
        metadata_policy=metadata,
        codec_profile=codecs,
        render_manifest=manifest_summary,
        partner_export=partner,
    )
    return {
        "bundle_id": bundle_id,
        "lane": lane,
        "threshold_profile": threshold_profile_summary(lane),
        "render_budget": render_budget_policy(lane),
        "histogram": histogram,
        "color_delta": color,
        "region_diff": regions,
        "tile_coverage": tiles,
        "metadata_policy": metadata,
        "render_manifest": manifest_summary,
        "codec_profile": codecs,
        "partner_export": partner,
        "partner_delivery": partner_delivery,
        "rollout": rollout,
        "exceptions": exceptions,
        "lineage": lineage,
        "gate": gate,
        "quality_report": quality_report,
    }
