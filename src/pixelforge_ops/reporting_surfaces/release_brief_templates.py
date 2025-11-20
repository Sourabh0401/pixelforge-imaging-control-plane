from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data
from pixelforge_ops.utils import json_digest


BRIEF_TEMPLATES = load_json_data("reporting_surfaces", "release_brief_templates.json")


def owners() -> list[str]:
    return sorted(BRIEF_TEMPLATES)


def brief_for_owner(owner: str) -> dict[str, object]:
    return clone_data(BRIEF_TEMPLATES[owner])


def owner_prompt_cards(owner: str) -> list[str]:
    return list(BRIEF_TEMPLATES[owner]["prompts"])


def metric_callouts(owner: str) -> list[str]:
    return list(BRIEF_TEMPLATES[owner]["metric_callouts"])


def brief_digest(owner: str) -> str:
    return json_digest(BRIEF_TEMPLATES[owner])


def render_brief(owner: str, title: str, summary_lines: list[str]) -> str:
    template = BRIEF_TEMPLATES[owner]
    lines = [f"# {title}", "", template["intro"], "", "## Metric callouts"]
    lines.extend(f"- {item}" for item in template["metric_callouts"])
    lines.extend(["", "## Summary"])
    lines.extend(f"- {line}" for line in summary_lines)
    lines.extend(["", "## Review prompts"])
    lines.extend(f"- {item}" for item in template["prompts"])
    lines.extend(["", template["closing"]])
    return "\n".join(lines) + "\n"
