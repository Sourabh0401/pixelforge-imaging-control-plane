from __future__ import annotations

from engineering_challenge.models import Scorecard
from engineering_challenge.scoring_model.fairness import fairness_flags, hidden_gap


def remediation_reason(scorecard: Scorecard) -> str:
    if scorecard.percent < 60:
        return "score below release floor"
    if hidden_gap(scorecard) >= 20:
        return "public-hidden gap requires review"
    if "requires-review" in scorecard.policy_flags:
        return "policy requested review"
    return "manual spot check"


def remediation_item(scorecard: Scorecard) -> dict[str, object]:
    return {
        "bundle_id": scorecard.bundle_id,
        "owner": scorecard.owner,
        "percent": scorecard.percent,
        "reason": remediation_reason(scorecard),
        "flags": list(dict.fromkeys(list(scorecard.policy_flags) + list(fairness_flags(scorecard)))),
    }


def remediation_queue(scorecards: list[Scorecard]) -> list[dict[str, object]]:
    queue = [
        remediation_item(scorecard)
        for scorecard in scorecards
        if scorecard.percent < 70 or hidden_gap(scorecard) >= 20 or scorecard.policy_flags
    ]
    return sorted(queue, key=lambda item: (item["percent"], item["bundle_id"]))
