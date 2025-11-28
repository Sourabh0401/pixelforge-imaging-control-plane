from __future__ import annotations

from typing import Mapping, Sequence

from .color_profile_validator import profile_summary
from .exif_contract import exif_summary
from .lane_contracts import required_metadata_fields_for_lane


def normalize_metadata(metadata: Mapping[str, object]) -> dict[str, object]:
    payload = dict(metadata)
    payload["width"] = int(payload.get("width", 0) or 0)
    payload["height"] = int(payload.get("height", 0) or 0)
    payload["orientation"] = str(payload.get("orientation", "unknown") or "unknown")
    payload["alpha_mode"] = str(payload.get("alpha_mode", "opaque") or "opaque")
    payload["color_profile"] = str(payload.get("color_profile", payload.get("icc_profile", "")) or "")
    payload["delivery_profile"] = str(payload.get("delivery_profile", "") or "")
    payload["icc_profile"] = str(payload.get("icc_profile", "") or "")
    return payload


def missing_metadata_fields(metadata: Mapping[str, object], required_fields: Sequence[str]) -> list[str]:
    payload = normalize_metadata(metadata)
    missing = []
    for field in required_fields:
        value = payload.get(field)
        if value in (None, "", 0):
            missing.append(field)
    return sorted(missing)


def dimension_issues(metadata: Mapping[str, object], min_width: int = 1, min_height: int = 1) -> list[str]:
    payload = normalize_metadata(metadata)
    issues = []
    if int(payload["width"]) < min_width:
        issues.append("width below minimum")
    if int(payload["height"]) < min_height:
        issues.append("height below minimum")
    return issues


def metadata_policy_summary(
    metadata: Mapping[str, object],
    lane: str,
    required_exif: Sequence[str] = (),
    forbidden_exif: Sequence[str] = (),
    allowed_profiles: Sequence[str] = (),
) -> dict[str, object]:
    payload = normalize_metadata(metadata)
    required_fields = required_metadata_fields_for_lane(lane)
    missing = missing_metadata_fields(payload, required_fields)
    profile = profile_summary(
        {
            "profile": payload.get("color_profile"),
            "embedded": bool(payload.get("color_profile")),
            "transfer_function": payload.get("transfer_function"),
            "gamut": payload.get("gamut"),
        },
        required_profile=allowed_profiles[0] if allowed_profiles else None,
        allowed_transfer_functions=tuple(str(item) for item in payload.get("allowed_transfer_functions", ())),
        require_embedded_profile="partner" in lane,
        allowed_gamuts=tuple(str(item) for item in payload.get("allowed_gamuts", ())),
    )
    exif = exif_summary(
        payload,
        required_fields=tuple(required_exif),
        forbidden_fields=tuple(forbidden_exif),
        numeric_ranges=payload.get("numeric_ranges"),
    )
    issues = []
    issues.extend(f"missing metadata field: {field}" for field in missing)
    issues.extend(dimension_issues(payload))
    if payload["alpha_mode"] not in {"opaque", "premultiplied", "straight"}:
        issues.append(f"unsupported alpha mode: {payload['alpha_mode']}")
    if not profile["passed"]:
        issues.extend(f"color profile issue: {entry}" for entry in profile["issues"])
    if not exif["passed"]:
        issues.extend(f"exif issue: {entry}" for entry in exif["issues"])
    status = "block" if missing or any(text.startswith("exif issue: missing") for text in issues) else "warn" if issues else "ok"
    return {
        "passed": status != "block",
        "status": status,
        "severity": status,
        "issue_codes": ["metadata-policy"] if issues else [],
        "issues": issues,
        "required_fields": list(required_fields),
        "missing_fields": missing,
        "profile": profile,
        "exif": exif,
    }

