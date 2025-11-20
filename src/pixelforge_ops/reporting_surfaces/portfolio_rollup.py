from __future__ import annotations

from statistics import mean
from typing import Iterable

from pixelforge_ops.models import Scorecard


def rollup(scorecards: list[Scorecard]) -> dict[str, object]:
    by_band: dict[str, int] = {}
    by_owner: dict[str, list[float]] = {}
    hidden_gaps: list[float] = []
    for item in scorecards:
        by_band[item.band] = by_band.get(item.band, 0) + 1
        by_owner.setdefault(item.owner, []).append(item.percent)
        hidden_gaps.append(round(item.public_percent - item.hidden_percent, 2))
    return {
        "count": len(scorecards),
        "band_counts": dict(sorted(by_band.items())),
        "owner_average": {owner: round(sum(values) / len(values), 2) for owner, values in sorted(by_owner.items())},
        "average_gap": round(mean(hidden_gaps), 2) if hidden_gaps else 0.0,
    }


def csv_rows(scorecards: list[Scorecard]) -> list[dict[str, object]]:
    return [
        {
            "bundle_id": item.bundle_id,
            "owner": item.owner,
            "percent": item.percent,
            "band": item.band,
            "public_percent": item.public_percent,
            "hidden_percent": item.hidden_percent,
        }
        for item in scorecards
    ]


def watch_owners(scorecards: list[Scorecard], floor: float = 80.0) -> list[str]:
    owner_scores: dict[str, list[float]] = {}
    for item in scorecards:
        owner_scores.setdefault(item.owner, []).append(item.percent)
    return sorted(owner for owner, values in owner_scores.items() if mean(values) < floor)


def public_hidden_gap_summary(scorecards: list[Scorecard]) -> dict[str, float]:
    if not scorecards:
        return {"average": 0.0, "max": 0.0, "min": 0.0}
    gaps = [round(item.public_percent - item.hidden_percent, 2) for item in scorecards]
    return {"average": round(mean(gaps), 2), "max": max(gaps), "min": min(gaps)}


def section_average(scorecards: Iterable[Scorecard]) -> dict[str, float]:
    buckets: dict[str, list[float]] = {}
    for item in scorecards:
        for section, payload in item.section_totals.items():
            buckets.setdefault(section, []).append(float(payload["percent"]))
    return {section: round(mean(values), 2) for section, values in sorted(buckets.items())}


def band_register(scorecards: list[Scorecard]) -> dict[str, list[str]]:
    register: dict[str, list[str]] = {}
    for item in scorecards:
        register.setdefault(item.band, []).append(item.bundle_id)
    return {band: sorted(bundle_ids) for band, bundle_ids in sorted(register.items())}


def owner_risk_register(scorecards: list[Scorecard]) -> list[dict[str, object]]:
    by_owner: dict[str, list[Scorecard]] = {}
    for item in scorecards:
        by_owner.setdefault(item.owner, []).append(item)
    rows: list[dict[str, object]] = []
    for owner, cards in sorted(by_owner.items()):
        averages = [card.percent for card in cards]
        gap = public_hidden_gap_summary(cards)
        flags = sorted({flag for card in cards for flag in card.policy_flags})
        rows.append(
            {
                "owner": owner,
                "bundle_count": len(cards),
                "average_percent": round(mean(averages), 2),
                "average_gap": gap["average"],
                "bands": band_register(cards),
                "flags": flags,
            }
        )
    return rows


def markdown_summary(scorecards: list[Scorecard]) -> str:
    top = rollup(scorecards)
    lines = ["# Portfolio rollup", ""]
    lines.append(f"- bundle count: {top['count']}")
    lines.append(f"- average public-hidden gap: {top['average_gap']}")
    lines.append("")
    lines.append("## Bands")
    for band, count in top["band_counts"].items():
        lines.append(f"- {band}: {count}")
    lines.append("")
    lines.append("## Owner averages")
    for owner, average in top["owner_average"].items():
        lines.append(f"- {owner}: {average}")
    return "\n".join(lines) + "\n"


