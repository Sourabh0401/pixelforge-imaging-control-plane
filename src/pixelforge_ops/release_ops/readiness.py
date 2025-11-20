from __future__ import annotations

from pixelforge_ops.models import Scorecard
from pixelforge_ops.release_ops.checklist import blocking_items


def readiness_state(scorecards: list[Scorecard]) -> dict[str, object]:
    blocked = [card.bundle_id for card in scorecards if card.band == "blocked"]
    watch = [card.bundle_id for card in scorecards if card.band == "watch"]
    ready = len(blocked) == 0 and len(watch) <= max(1, len(scorecards) // 3)
    return {"ready": ready, "blocked": blocked, "watch": watch}


def readiness_notes(scorecards: list[Scorecard]) -> list[str]:
    state = readiness_state(scorecards)
    notes = []
    if state["blocked"]:
        notes.append("At least one bundle is still blocked.")
    if state["watch"]:
        notes.append("Watch-band bundles need owner sign-off before ship.")
    if not notes:
        notes.append("Release set is ready for handoff.")
    return notes


def blocking_check_codes(channel: str) -> tuple[str, ...]:
    return tuple(item["code"] for item in blocking_items(channel))


