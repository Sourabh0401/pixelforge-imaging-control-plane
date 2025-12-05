from __future__ import annotations

"""
Partner delivery rules for imaging packets.

Visual parity is only part of a partner-ready packet. Export lanes also need
required files, required codecs, metadata contracts, and stable routing. These
helpers keep that validation close to the imaging package instead of treating
partner delivery as an afterthought after render-time checks have passed.
"""

from collections import Counter, defaultdict
from typing import Iterable, Mapping

from .reference_data import load_reference_data


def _profiles() -> list[dict[str, object]]:
    payload = load_reference_data("partner_delivery_profiles.json")
    return [dict(row) for row in payload["profiles"]]


def partner_profile(partner: str, lane: str) -> dict[str, object]:
    for row in _profiles():
        if str(row.get("partner")) == partner and str(row.get("lane")) == lane:
            return row
    raise KeyError(f"{partner}:{lane}")


def partner_requirements(partner: str, lane: str) -> dict[str, object]:
    profile = partner_profile(partner, lane)
    return {
        "required_files": sorted(str(value) for value in profile.get("required_files", [])),
        "required_codecs": sorted(str(value) for value in profile.get("required_codecs", [])),
        "required_metadata": sorted(str(value) for value in profile.get("required_metadata", [])),
        "strict_manifest_digest": bool(profile.get("strict_manifest_digest", False)),
        "allow_alpha": bool(profile.get("allow_alpha", False)),
    }


def validate_partner_delivery(
    partner: str,
    lane: str,
    files: Iterable[str],
    codecs: Iterable[str],
    metadata: Mapping[str, object],
) -> dict[str, object]:
    requirements = partner_requirements(partner, lane)
    file_set = {str(value) for value in files}
    codec_set = {str(value).lower() for value in codecs}
    metadata_map = dict(metadata)
    issues = []
    for file_name in requirements["required_files"]:
        if file_name not in file_set:
            issues.append(f"missing required file: {file_name}")
    for codec_name in requirements["required_codecs"]:
        if codec_name not in codec_set:
            issues.append(f"missing required codec: {codec_name}")
    for field_name in requirements["required_metadata"]:
        if metadata_map.get(field_name) in (None, "", []):
            issues.append(f"missing required metadata: {field_name}")
    return {
        "passed": not issues,
        "status": "block" if issues else "ok",
        "issues": issues,
        "partner": partner,
        "lane": lane,
        "requirements": requirements,
    }


def partner_matrix(rows: Iterable[Mapping[str, object]]) -> dict[str, object]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("partner"))].append(dict(row))
    partner_status = {}
    issue_counts = Counter()
    for partner, items in sorted(grouped.items()):
        blocked = any(str(item.get("status")) == "block" for item in items)
        warned = any(str(item.get("status")) == "warn" for item in items)
        status = "block" if blocked else "warn" if warned else "ok"
        partner_status[partner] = {
            "status": status,
            "lanes": sorted(str(item.get("lane")) for item in items),
            "issue_count": sum(len(item.get("issues", [])) for item in items),
        }
        issue_counts[status] += 1
    return {"partners": partner_status, "status_counts": dict(sorted(issue_counts.items()))}
