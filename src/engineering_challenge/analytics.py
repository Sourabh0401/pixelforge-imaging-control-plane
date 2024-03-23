from __future__ import annotations

from typing import Iterable

from .models import Scorecard


def difficulty_drift(previous: Iterable[Scorecard], current: Iterable[Scorecard]) -> dict[str, float]:
    before = {card.bundle_id: card.percent for card in previous}
    after = {card.bundle_id: card.percent for card in current}
    shared = sorted(set(before) & set(after))
    return {bundle_id: round(after[bundle_id] - before[bundle_id], 2) for bundle_id in shared}


def release_readiness(scorecards: Iterable[Scorecard]) -> dict[str, object]:
    cards = list(scorecards)
    if not cards:
        return {"ready": False, "average_percent": 0.0, "blocked_count": 0}
    average = round(sum(card.percent for card in cards) / len(cards), 2)
    blocked = sum(1 for card in cards if card.band == "blocked")
    return {"ready": blocked == 0 and average >= 78.0, "average_percent": average, "blocked_count": blocked}
