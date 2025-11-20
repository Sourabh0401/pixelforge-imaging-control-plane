from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data


OWNER_CAPACITY = load_json_data("release_ops", "owner_capacity.json")


def week_rows() -> list[dict[str, object]]:
    return [clone_data(row) for row in OWNER_CAPACITY["weeks"]]


def capacity_for_week(owner: str, week_start: str) -> int:
    for row in OWNER_CAPACITY["weeks"]:
        if row["week_start"] == week_start:
            return int(row["capacity"][owner])
    raise KeyError(week_start)


def blackout_owners(week_start: str) -> list[str]:
    for row in OWNER_CAPACITY["weeks"]:
        if row["week_start"] == week_start:
            return list(row["blackout"])
    raise KeyError(week_start)
