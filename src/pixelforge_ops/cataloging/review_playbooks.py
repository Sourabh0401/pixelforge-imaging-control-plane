from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data


PLAYBOOKS = load_json_data("cataloging", "review_playbooks.json")


def steps_for_section(section: str) -> list[dict[str, object]]:
    return [clone_data(step) for step in PLAYBOOKS.get(section, [])]


def blocking_steps(section: str) -> list[dict[str, object]]:
    return [clone_data(step) for step in PLAYBOOKS.get(section, []) if step["blocking"]]


def steps_for_owner(owner: str) -> list[dict[str, object]]:
    output = []
    for section, steps in PLAYBOOKS.items():
        for step in steps:
            if step["owner"] == owner:
                output.append({"section": section, **clone_data(step)})
    return output


def step_codes(section: str) -> tuple[str, ...]:
    return tuple(step["code"] for step in PLAYBOOKS.get(section, []))


def playbook_summary(section: str) -> dict[str, object]:
    steps = PLAYBOOKS.get(section, [])
    return {
        "section": section,
        "step_count": len(steps),
        "blocking_count": sum(1 for step in steps if step["blocking"]),
        "owners": sorted({step["owner"] for step in steps}),
    }


def owner_handoff_notes(owner: str) -> list[str]:
    steps = steps_for_owner(owner)
    return [
        f"{item['section']} requires {item['title'].lower()} and evidence: {', '.join(item['evidence'])}"
        for item in steps
    ]
