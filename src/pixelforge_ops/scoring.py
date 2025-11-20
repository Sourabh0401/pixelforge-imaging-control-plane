from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .models import ExerciseBundle, Scorecard, SubmissionRun
from .policy import band_for_percent, remediation_flags


def _section_totals(run: SubmissionRun) -> dict[str, dict[str, float]]:
    buckets: dict[str, dict[str, float]] = defaultdict(lambda: {"earned": 0.0, "possible": 0.0, "count": 0.0})
    for result in run.case_results:
        bucket = buckets[result.section]
        bucket["earned"] += result.points
        bucket["possible"] += result.max_points
        bucket["count"] += 1
    for section, bucket in buckets.items():
        bucket["percent"] = round((bucket["earned"] / bucket["possible"] * 100.0) if bucket["possible"] else 0.0, 2)
    return dict(sorted(buckets.items()))


def score_run(run: SubmissionRun, bundle: ExerciseBundle) -> Scorecard:
    earned = sum(item.points for item in run.case_results)
    possible = sum(item.max_points for item in run.case_results)
    public_earned = sum(item.points for item in run.case_results if not item.hidden)
    public_possible = sum(item.max_points for item in run.case_results if not item.hidden)
    hidden_earned = sum(item.points for item in run.case_results if item.hidden)
    hidden_possible = sum(item.max_points for item in run.case_results if item.hidden)
    percent = round((earned / possible * 100.0) if possible else 0.0, 2)
    public_percent = round((public_earned / public_possible * 100.0) if public_possible else 0.0, 2)
    hidden_percent = round((hidden_earned / hidden_possible * 100.0) if hidden_possible else 0.0, 2)
    return Scorecard(
        run_id=run.run_id,
        bundle_id=run.bundle_id,
        percent=percent,
        band=band_for_percent(percent),
        public_percent=public_percent,
        hidden_percent=hidden_percent,
        section_totals=_section_totals(run),
        policy_flags=remediation_flags(public_percent, hidden_percent, percent),
        owner=bundle.owner,
    )


def scorecard_to_dict(scorecard: Scorecard) -> dict[str, object]:
    return {
        "run_id": scorecard.run_id,
        "bundle_id": scorecard.bundle_id,
        "percent": scorecard.percent,
        "band": scorecard.band,
        "public_percent": scorecard.public_percent,
        "hidden_percent": scorecard.hidden_percent,
        "section_totals": scorecard.section_totals,
        "policy_flags": list(scorecard.policy_flags),
        "owner": scorecard.owner,
    }


def portfolio_rollup(scorecards: Iterable[Scorecard]) -> dict[str, object]:
    cards = list(scorecards)
    by_band: dict[str, int] = {}
    by_owner: dict[str, list[float]] = {}
    for card in cards:
        by_band[card.band] = by_band.get(card.band, 0) + 1
        by_owner.setdefault(card.owner, []).append(card.percent)
    return {
        "count": len(cards),
        "band_counts": dict(sorted(by_band.items())),
        "owner_average_percent": {owner: round(sum(values) / len(values), 2) for owner, values in sorted(by_owner.items())},
    }
