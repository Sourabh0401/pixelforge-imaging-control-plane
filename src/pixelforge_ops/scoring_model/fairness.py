from __future__ import annotations

from pixelforge_ops.models import Scorecard


def hidden_gap(scorecard: Scorecard) -> float:
    return round(scorecard.public_percent - scorecard.hidden_percent, 2)


def section_spread(scorecard: Scorecard) -> float:
    percents = [bucket["percent"] for bucket in scorecard.section_totals.values()]
    return round((max(percents) - min(percents)) if percents else 0.0, 2)


def fairness_flags(scorecard: Scorecard) -> tuple[str, ...]:
    flags = []
    if hidden_gap(scorecard) >= 20:
        flags.append("public-hidden-gap")
    if section_spread(scorecard) >= 30:
        flags.append("section-spread")
    if scorecard.hidden_percent < 60:
        flags.append("hidden-depth-risk")
    return tuple(flags)


def fairness_summary(scorecards: list[Scorecard]) -> dict[str, float]:
    if not scorecards:
        return {"average_hidden_gap": 0.0, "average_spread": 0.0}
    return {
        "average_hidden_gap": round(sum(hidden_gap(card) for card in scorecards) / len(scorecards), 2),
        "average_spread": round(sum(section_spread(card) for card in scorecards) / len(scorecards), 2),
    }


