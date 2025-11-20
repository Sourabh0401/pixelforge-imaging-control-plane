from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data


THRESHOLD_CATALOG = load_json_data("scoring_model", "threshold_catalog.json")


def thresholds_for_owner(owner: str) -> dict[str, dict[str, float]]:
    return clone_data(THRESHOLD_CATALOG["owner_thresholds"][owner])


def section_threshold(owner: str, section: str) -> dict[str, float]:
    return clone_data(THRESHOLD_CATALOG["owner_thresholds"][owner][section])
