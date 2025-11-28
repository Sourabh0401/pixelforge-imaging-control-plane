from __future__ import annotations

from typing import Mapping

from .codec_profile import codec_profile_summary
from .metadata_policy import metadata_policy_summary
from .render_manifest import render_manifest_summary


def partner_export_summary(
    lane: str,
    metadata: Mapping[str, object],
    codec_rows: list[Mapping[str, object]],
    manifest: Mapping[str, object],
) -> dict[str, object]:
    metadata_result = metadata_policy_summary(
        metadata,
        lane=lane,
        required_exif=("camera_model", "orientation") if "metadata" in lane else (),
        allowed_profiles=("DisplayP3",) if "partner" in lane else (),
    )
    codec_result = codec_profile_summary(codec_rows)
    manifest_result = render_manifest_summary(manifest)
    issues = []
    issues.extend(f"metadata: {message}" for message in metadata_result["issues"])
    issues.extend(f"codec: {message}" for message in codec_result["issues"])
    issues.extend(f"manifest: {message}" for message in manifest_result["issues"])
    status = "block" if not metadata_result["passed"] or not manifest_result["passed"] else "warn" if issues else "ok"
    return {
        "passed": status != "block",
        "status": status,
        "severity": status,
        "issue_codes": ["partner-export"] if issues else [],
        "issues": issues,
        "metadata": metadata_result,
        "codecs": codec_result,
        "manifest": manifest_result,
    }

