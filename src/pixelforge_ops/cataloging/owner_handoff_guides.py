from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data
from pixelforge_ops.utils import json_digest


OWNER_HANDOFF_GUIDES = load_json_data("cataloging", "owner_handoff_guides.json")


def guide(owner: str) -> dict[str, object]:
    return clone_data(OWNER_HANDOFF_GUIDES[owner])


def signals(owner: str) -> list[str]:
    return list(OWNER_HANDOFF_GUIDES[owner]["signals"])


def questions(owner: str) -> list[str]:
    return list(OWNER_HANDOFF_GUIDES[owner]["questions"])


def handoff_notes(owner: str) -> list[str]:
    return list(OWNER_HANDOFF_GUIDES[owner]["handoff_notes"])


def guide_digest(owner: str) -> str:
    return json_digest(OWNER_HANDOFF_GUIDES[owner])


def render_markdown(owner: str) -> str:
    item = OWNER_HANDOFF_GUIDES[owner]
    lines = [f"# {owner} handoff guide", "", item["purpose"], "", "## Signals to watch"]
    lines.extend(f"- {signal}" for signal in item["signals"])
    lines.extend(["", "## Questions to answer"])
    lines.extend(f"- {question}" for question in item["questions"])
    lines.extend(["", "## Handoff notes"])
    lines.extend(f"- {note}" for note in item["handoff_notes"])
    return "\n".join(lines) + "\n"
