from __future__ import annotations

"""
Render human-facing operator guidance from lane-aware imaging evidence.

The point of the control plane is not just to compute a packet. It is also to
leave enough structured prose behind that another operator can continue the
same investigation later without reverse engineering the lane from raw JSON.
"""

from importlib import resources
from typing import Iterable

from .issue_taxonomy import issue_rollup, taxonomy_entry
from .reference_data import load_reference_data


TEMPLATE_PACKAGE = "pixelforge_ops.imaging.templates"


def available_templates() -> list[str]:
    root = resources.files(TEMPLATE_PACKAGE)
    return sorted(item.name for item in root.iterdir() if item.name.endswith(".md"))


def template_name_for_lane(lane: str) -> str:
    return f"{str(lane).replace('-', '_')}.md"


def template_text(lane: str) -> str:
    return resources.files(TEMPLATE_PACKAGE).joinpath(template_name_for_lane(lane)).read_text(encoding="utf-8")


def release_questionnaire(lane: str) -> dict[str, object]:
    payload = load_reference_data("release_questionnaires.json")
    for questionnaire in payload["questionnaires"]:
        if str(questionnaire.get("lane")) == lane:
            return dict(questionnaire)
    raise KeyError(lane)


def build_operator_brief(lane: str, issue_codes: Iterable[str], status: str) -> dict[str, object]:
    codes = sorted({str(code) for code in issue_codes})
    rollup = issue_rollup(codes)
    entries = [taxonomy_entry(code) for code in codes]
    questionnaire = release_questionnaire(lane)
    return {
        "lane": lane,
        "status": status,
        "issue_codes": codes,
        "issue_rollup": rollup,
        "owners": sorted({str(entry["owner_group"]) for entry in entries}),
        "families": sorted({str(entry["family"]) for entry in entries}),
        "questions": list(questionnaire["questions"]),
        "handoff_template": list(questionnaire["handoff_template"]),
        "template_name": template_name_for_lane(lane),
    }


def render_operator_brief(lane: str, issue_codes: Iterable[str], status: str) -> str:
    brief = build_operator_brief(lane, issue_codes, status)
    lines = [
        f"# {lane} operator brief",
        "",
        f"Status: {brief['status']}",
        f"Issue codes: {', '.join(brief['issue_codes']) or 'none'}",
        f"Owner groups: {', '.join(brief['owners']) or 'none'}",
        "",
        "## Release questions",
    ]
    for question in brief["questions"]:
        lines.append(f"- {question}")
    lines.extend(["", "## Handoff template"])
    for item in brief["handoff_template"]:
        lines.append(f"- {item}")
    return "\n".join(lines)
