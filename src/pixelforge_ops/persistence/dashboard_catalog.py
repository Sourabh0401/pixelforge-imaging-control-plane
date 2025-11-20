from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data


DASHBOARD_CATALOG = load_json_data("persistence", "dashboard_catalog.json")


def widgets() -> list[dict[str, object]]:
    return [clone_data(row) for row in DASHBOARD_CATALOG["widgets"]]


def widget_for_owner(owner: str) -> dict[str, object]:
    for row in DASHBOARD_CATALOG["widgets"]:
        if row["owner"] == owner:
            return clone_data(row)
    raise KeyError(owner)
