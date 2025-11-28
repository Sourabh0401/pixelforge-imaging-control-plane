from __future__ import annotations

from typing import Mapping, Sequence


def lane_tokens(lane: str) -> tuple[str, ...]:
    parts = [part.strip().lower() for part in str(lane).replace("_", "-").split("-") if part.strip()]
    return tuple(parts)


def required_codecs_for_lane(lane: str) -> tuple[str, ...]:
    tokens = set(lane_tokens(lane))
    if "jpeg" in tokens:
        return ("jpeg", "webp")
    if "thumbnail" in tokens:
        return ("jpeg", "webp", "avif")
    if "partner" in tokens:
        return ("png", "webp")
    if "color" in tokens:
        return ("png", "avif")
    if "metadata" in tokens:
        return ("jpeg",)
    return ("png", "jpeg")


def required_metadata_fields_for_lane(lane: str) -> tuple[str, ...]:
    tokens = set(lane_tokens(lane))
    fields = {"width", "height", "color_profile"}
    if "metadata" in tokens or "exif" in tokens:
        fields.update({"camera_model", "orientation", "capture_timestamp"})
    if "alpha" in tokens:
        fields.add("alpha_mode")
    if "partner" in tokens:
        fields.update({"delivery_profile", "icc_profile"})
    if "thumbnail" in tokens:
        fields.update({"crop_mode", "target_aspect_ratio"})
    return tuple(sorted(fields))


def tolerance_contract_for_lane(lane: str) -> dict[str, object]:
    tokens = set(lane_tokens(lane))
    tolerance = 2 if "jpeg" in tokens else 1
    warn_threshold = 0.02
    block_threshold = 0.06
    if "color" in tokens:
        tolerance = 1
        warn_threshold = 0.01
        block_threshold = 0.03
    if "thumbnail" in tokens:
        tolerance = 3
        warn_threshold = 0.03
        block_threshold = 0.08
    if "alpha" in tokens:
        tolerance = 0
        warn_threshold = 0.005
        block_threshold = 0.02
    return {
        "tolerance": tolerance,
        "warn_threshold": warn_threshold,
        "block_threshold": block_threshold,
        "max_mismatched_pixels": 0 if "alpha" in tokens else 8,
    }


def manifest_contract_for_lane(lane: str) -> dict[str, object]:
    tokens = set(lane_tokens(lane))
    return {
        "required_codecs": list(required_codecs_for_lane(lane)),
        "required_metadata": list(required_metadata_fields_for_lane(lane)),
        "allow_alpha": "alpha" in tokens or "sprite" in tokens,
        "require_tiles": "tiling" in tokens or "raster" in tokens or "thumbnail" in tokens,
        "require_partner_export": "partner" in tokens,
    }


def lane_contract(lane: str) -> dict[str, object]:
    return {
        "lane": lane,
        "tokens": list(lane_tokens(lane)),
        "required_codecs": list(required_codecs_for_lane(lane)),
        "required_metadata": list(required_metadata_fields_for_lane(lane)),
        "tolerance": tolerance_contract_for_lane(lane),
        "manifest": manifest_contract_for_lane(lane),
    }


def validate_lane_contract(contract: Mapping[str, object]) -> list[str]:
    issues: list[str] = []
    lane = str(contract.get("lane", "")).strip()
    if not lane:
        issues.append("lane contract missing lane")
    required_codecs = contract.get("required_codecs", [])
    if not isinstance(required_codecs, Sequence) or not required_codecs:
        issues.append("lane contract missing required codecs")
    required_metadata = contract.get("required_metadata", [])
    if not isinstance(required_metadata, Sequence) or not required_metadata:
        issues.append("lane contract missing required metadata")
    tolerance = contract.get("tolerance", {})
    if not isinstance(tolerance, Mapping):
        issues.append("lane contract tolerance must be a mapping")
    else:
        if int(tolerance.get("tolerance", -1)) < 0:
            issues.append("lane contract tolerance must be non-negative")
        if float(tolerance.get("warn_threshold", -1)) < 0:
            issues.append("lane contract warn threshold must be non-negative")
        if float(tolerance.get("block_threshold", -1)) < 0:
            issues.append("lane contract block threshold must be non-negative")
    return issues


def lane_release_channel(lane: str) -> str:
    tokens = set(lane_tokens(lane))
    if "partner" in tokens:
        return "partner"
    if "telemetry" in tokens or "replay" in tokens:
        return "pilot"
    return "internal"


def lane_priority(lane: str) -> int:
    tokens = set(lane_tokens(lane))
    if "alpha" in tokens or "color" in tokens:
        return 100
    if "partner" in tokens or "metadata" in tokens:
        return 90
    if "codec" in tokens or "jpeg" in tokens:
        return 80
    if "thumbnail" in tokens or "tiling" in tokens:
        return 70
    return 60

