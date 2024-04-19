from __future__ import annotations

from typing import Iterable

from .models import Scorecard


def remediation_queue(scorecards: Iterable[Scorecard]) -> list[dict[str, object]]:
    queue: list[dict[str, object]] = []
    for scorecard in scorecards:
        if scorecard.percent < 60:
            queue.append(
                {
                    "bundle_id": scorecard.bundle_id,
                    "owner": scorecard.owner,
                    "percent": scorecard.percent,
                    "reason": "score below release floor",
                }
            )
        elif "hidden-case-regression" in scorecard.policy_flags:
            queue.append(
                {
                    "bundle_id": scorecard.bundle_id,
                    "owner": scorecard.owner,
                    "percent": scorecard.percent,
                    "reason": "hidden cases regressed",
                }
            )
    return sorted(queue, key=lambda item: (item["percent"], item["bundle_id"]))


def owner_hotspots(scorecards: Iterable[Scorecard]) -> dict[str, dict[str, float]]:
    buckets: dict[str, list[float]] = {}
    for scorecard in scorecards:
        buckets.setdefault(scorecard.owner, []).append(scorecard.percent)
    return {
        owner: {"average_percent": round(sum(values) / len(values), 2), "run_count": float(len(values))}
        for owner, values in sorted(buckets.items())
    }
