from __future__ import annotations

from collections import defaultdict

from pixelforge_ops.models import SubmissionRun
from pixelforge_ops.scoring_model.band_matrix import section_weights_for_owner


def weighted_section_totals(run: SubmissionRun, owner: str) -> dict[str, dict[str, float]]:
    weights = section_weights_for_owner(owner)
    totals: dict[str, dict[str, float]] = defaultdict(lambda: {"earned": 0.0, "possible": 0.0, "weight": 1.0})
    for result in run.case_results:
        bucket = totals[result.section]
        weight = weights.get(result.section, 1.0)
        bucket["weight"] = weight
        bucket["earned"] += result.points * weight
        bucket["possible"] += result.max_points * weight
    for section, bucket in totals.items():
        bucket["percent"] = round((bucket["earned"] / bucket["possible"] * 100.0) if bucket["possible"] else 0.0, 2)
    return dict(sorted(totals.items()))


def weighted_percent(section_totals: dict[str, dict[str, float]]) -> float:
    earned = sum(bucket["earned"] for bucket in section_totals.values())
    possible = sum(bucket["possible"] for bucket in section_totals.values())
    return round((earned / possible * 100.0) if possible else 0.0, 2)


