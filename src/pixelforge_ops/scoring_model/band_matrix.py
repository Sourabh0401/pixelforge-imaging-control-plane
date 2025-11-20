from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data


_DATA = load_json_data("scoring_model", "band_matrix.json")
BAND_MATRIX = _DATA["band_matrix"]
DIFFICULTY_TARGETS = _DATA["difficulty_targets"]
FLAG_LIBRARY = _DATA["flag_library"]
SECTION_WEIGHT_MATRIX = _DATA["section_weight_matrix"]


def band_for_percent(percent: float) -> str:
    for row in BAND_MATRIX:
        if percent >= row["floor"]:
            return str(row["band"])
    return "blocked"


def band_route(band: str) -> str:
    for row in BAND_MATRIX:
        if row["band"] == band:
            return str(row["queue"])
    raise KeyError(band)


def section_weights_for_owner(owner: str) -> dict[str, float]:
    return clone_data(SECTION_WEIGHT_MATRIX[owner])


def difficulty_target(level: str) -> dict[str, float]:
    return clone_data(DIFFICULTY_TARGETS[level])


def flag_definition(code: str) -> dict[str, object]:
    for row in FLAG_LIBRARY:
        if row["code"] == code:
            return clone_data(row)
    raise KeyError(code)
