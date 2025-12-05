from __future__ import annotations

"""
Lane threshold profiles bridge comparator code and release operations.

The imaging package now carries richer comparator summaries than the older
PixelForge control-plane surface did. These helpers keep the lane-specific
rules in one place so region diff, histogram drift, color delta, render
budget, and release gating all read the same contract.
"""

from typing import Any, Mapping

from .reference_data import load_reference_data


def _profiles() -> list[dict[str, object]]:
    payload = load_reference_data("lane_threshold_profiles.json")
    return [dict(row) for row in payload["profiles"]]


def lane_threshold_profile(lane: str) -> dict[str, object]:
    for row in _profiles():
        if str(row.get("lane")) == lane:
            return row
    raise KeyError(lane)


def comparator_thresholds(lane: str, comparator: str) -> dict[str, object]:
    profile = lane_threshold_profile(lane)
    comparators = dict(profile.get("comparators", {}))
    if comparator not in comparators:
        raise KeyError(f"{lane}:{comparator}")
    return dict(comparators[comparator])


def sampling_policy(lane: str) -> dict[str, object]:
    return dict(lane_threshold_profile(lane).get("sampling", {}))


def render_budget_policy(lane: str) -> dict[str, object]:
    return dict(lane_threshold_profile(lane).get("render_budget", {}))


def metadata_policy_contract(lane: str) -> dict[str, object]:
    return dict(lane_threshold_profile(lane).get("metadata", {}))


def release_blockers(lane: str) -> list[str]:
    return sorted(str(value) for value in lane_threshold_profile(lane).get("release_blockers", []))


def threshold_profile_summary(lane: str) -> dict[str, object]:
    profile = lane_threshold_profile(lane)
    comparators = dict(profile.get("comparators", {}))
    return {
        "lane": lane,
        "owner_group": profile.get("owner_group"),
        "release_channel": profile.get("release_channel"),
        "comparator_count": len(comparators),
        "comparator_names": sorted(str(name) for name in comparators),
        "required_fields": sorted(str(value) for value in profile.get("metadata", {}).get("required_fields", [])),
        "required_regions": sorted(str(value) for value in profile.get("sampling", {}).get("required_regions", [])),
        "release_blockers": release_blockers(lane),
    }


def merge_threshold_overrides(lane: str, comparator: str, overrides: Mapping[str, object] | None = None) -> dict[str, object]:
    base = comparator_thresholds(lane, comparator)
    for key, value in dict(overrides or {}).items():
        base[str(key)] = value
    return base


def validate_threshold_override(lane: str, comparator: str, overrides: Mapping[str, object]) -> list[str]:
    merged = merge_threshold_overrides(lane, comparator, overrides)
    issues: list[str] = []
    for key in ("warn_threshold", "block_threshold", "mean_delta_limit"):
        if key in merged and float(merged[key]) < 0:
            issues.append(f"{comparator} override {key} must be non-negative")
    if "tolerance" in merged and int(merged["tolerance"]) < 0:
        issues.append(f"{comparator} override tolerance must be non-negative")
    if "max_mismatched_pixels" in merged and int(merged["max_mismatched_pixels"]) < 0:
        issues.append(f"{comparator} override max_mismatched_pixels must be non-negative")
    return issues


def release_matrix() -> list[dict[str, object]]:
    rows = []
    for profile in _profiles():
        rows.append(
            {
                "lane": profile.get("lane"),
                "release_channel": profile.get("release_channel"),
                "owner_group": profile.get("owner_group"),
                "watch_signals": sorted(str(value) for value in profile.get("watch_signals", [])),
                "release_blockers": sorted(str(value) for value in profile.get("release_blockers", [])),
            }
        )
    rows.sort(key=lambda row: (str(row["release_channel"]), str(row["lane"])))
    return rows
