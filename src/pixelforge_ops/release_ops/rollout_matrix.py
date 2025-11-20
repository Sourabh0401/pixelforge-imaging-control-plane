from __future__ import annotations

from datetime import date

from pixelforge_ops.datafiles import clone_data, load_json_data


ROLLOUT_MATRIX = load_json_data("release_ops", "rollout_matrix.json")


def owner_quota(owner: str, channel: str) -> int:
    return int(ROLLOUT_MATRIX["owner_quotas"][owner].get(channel, 0))


def release_trains() -> list[dict[str, object]]:
    return [clone_data(item) for item in ROLLOUT_MATRIX["release_trains"]]


def release_train_for_date(day: date) -> dict[str, object]:
    iso = day.isoformat()
    for train in ROLLOUT_MATRIX["release_trains"]:
        if iso <= train["ship_date"]:
            return clone_data(train)
    return clone_data(ROLLOUT_MATRIX["release_trains"][-1])


def train_ids() -> tuple[str, ...]:
    return tuple(item["train_id"] for item in ROLLOUT_MATRIX["release_trains"])
