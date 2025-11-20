from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data


RELEASE_PROFILES = load_json_data("cataloging", "release_profiles.json")


def profile_for_bundle(bundle_id: str) -> dict[str, object]:
    for row in RELEASE_PROFILES:
        if row["bundle_id"] == bundle_id:
            return clone_data(row)
    raise KeyError(bundle_id)


def channels_for_bundle(bundle_id: str) -> list[str]:
    return list(profile_for_bundle(bundle_id)["channels"])


def score_floor(bundle_id: str) -> float:
    return float(profile_for_bundle(bundle_id)["score_floor"])
