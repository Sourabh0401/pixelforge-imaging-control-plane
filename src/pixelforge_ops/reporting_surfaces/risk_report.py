from __future__ import annotations

from pixelforge_ops.models import Scorecard
from pixelforge_ops.scoring_model.fairness import fairness_flags


def risk_rows(scorecards: list[Scorecard]) -> list[dict[str, object]]:
    rows = []
    for item in scorecards:
        if item.band in {"risk", "blocked"} or fairness_flags(item):
            rows.append(
                {
                    "bundle_id": item.bundle_id,
                    "owner": item.owner,
                    "band": item.band,
                    "percent": item.percent,
                    "flags": list(fairness_flags(item)),
                }
            )
    return sorted(rows, key=lambda row: (row["percent"], row["bundle_id"]))


