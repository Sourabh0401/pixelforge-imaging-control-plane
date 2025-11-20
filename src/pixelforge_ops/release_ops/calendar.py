from __future__ import annotations

from datetime import date

from pixelforge_ops.release_ops.rollout_matrix import release_train_for_date


def freeze_window(day: date) -> tuple[str, str]:
    train = release_train_for_date(day)
    return str(train["freeze_starts"]), str(train["ship_date"])


def in_freeze(day: date) -> bool:
    train = release_train_for_date(day)
    return str(train["freeze_starts"]) <= day.isoformat() <= str(train["ship_date"])


def next_ship_date(day: date) -> str:
    return str(release_train_for_date(day)["ship_date"])


