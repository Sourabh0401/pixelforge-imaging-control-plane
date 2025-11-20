from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data
from pixelforge_ops.utils import json_digest


PLAYBOOKS = load_json_data("cataloging", "bundle_playbooks.json")


def playbook(bundle_id: str) -> dict[str, object]:
    return clone_data(PLAYBOOKS[bundle_id])


def watch_sections(bundle_id: str) -> list[str]:
    return list(PLAYBOOKS[bundle_id]["watch_sections"])


def release_questions(bundle_id: str) -> list[str]:
    return list(PLAYBOOKS[bundle_id]["release_questions"])


def failure_patterns(bundle_id: str) -> list[str]:
    return list(PLAYBOOKS[bundle_id]["failure_patterns"])


def operator_steps(bundle_id: str) -> list[str]:
    return list(PLAYBOOKS[bundle_id]["operator_steps"])


def escalation_chain(bundle_id: str) -> list[str]:
    return list(PLAYBOOKS[bundle_id]["escalation_order"])


def playbook_digest(bundle_id: str) -> str:
    return json_digest(PLAYBOOKS[bundle_id])


def render_markdown(bundle_id: str) -> str:
    item = PLAYBOOKS[bundle_id]
    lines = [f"# {bundle_id} release playbook", "", item["audit_focus"], "", "## Watch sections"]
    lines.extend(f"- {section}" for section in item["watch_sections"])
    lines.extend(["", "## Release questions"])
    lines.extend(f"- {question}" for question in item["release_questions"])
    lines.extend(["", "## Failure patterns"])
    lines.extend(f"- {pattern}" for pattern in item["failure_patterns"])
    lines.extend(["", "## Operator steps"])
    lines.extend(f"- {step}" for step in item["operator_steps"])
    lines.extend(["", "## Escalation order"])
    lines.extend(f"- {owner}" for owner in item["escalation_order"])
    return "\n".join(lines) + "\n"
