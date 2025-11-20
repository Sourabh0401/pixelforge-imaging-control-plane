from __future__ import annotations

from pixelforge_ops.models import Scorecard


def by_bundle(scorecards: list[Scorecard]) -> dict[str, Scorecard]:
    return {scorecard.bundle_id: scorecard for scorecard in scorecards}


def percent_drift(previous: list[Scorecard], current: list[Scorecard]) -> dict[str, float]:
    old = by_bundle(previous)
    new = by_bundle(current)
    shared = sorted(set(old) & set(new))
    return {bundle_id: round(new[bundle_id].percent - old[bundle_id].percent, 2) for bundle_id in shared}


def hidden_drift(previous: list[Scorecard], current: list[Scorecard]) -> dict[str, float]:
    old = by_bundle(previous)
    new = by_bundle(current)
    shared = sorted(set(old) & set(new))
    return {
        bundle_id: round(new[bundle_id].hidden_percent - old[bundle_id].hidden_percent, 2)
        for bundle_id in shared
    }


def drift_alerts(previous: list[Scorecard], current: list[Scorecard]) -> list[dict[str, object]]:
    alerts = []
    for bundle_id, value in percent_drift(previous, current).items():
        if abs(value) >= 10:
            alerts.append({"bundle_id": bundle_id, "percent_drift": value})
    return alerts


