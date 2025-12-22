from __future__ import annotations

"""
Build a coherent release story from lane summaries.

By the time a lane reaches a release owner, the repo has machine summaries from
comparators, policies, and packet checks. The missing piece is often a single
structured object that explains the lane in the order humans actually read it:
what changed, what blocked, what can still move, and what the next shift should
do. That is the role of this module.
"""

from typing import Mapping


def story_headline(lane: str, gate: Mapping[str, object], readiness: Mapping[str, object]) -> str:
    gate_status = str(gate.get("status", "unknown"))
    band = str(readiness.get("band", "unknown"))
    if gate_status == "block":
        return f"{lane} is blocked and not export-ready"
    if band == "watch":
        return f"{lane} can move in watch mode with a constrained packet"
    if band == "stabilize":
        return f"{lane} needs stabilization before wider rollout"
    return f"{lane} is ready for the next release checkpoint"


def story_sections(summary: Mapping[str, object]) -> list[dict[str, object]]:
    lane = str(summary.get("lane", "unknown"))
    gate = dict(summary.get("gate", {}))
    readiness = dict(summary.get("export_readiness", {}))
    sections = [
        {
            "title": "Lane state",
            "lines": [
                f"lane: {lane}",
                f"gate status: {gate.get('status', 'unknown')}",
                f"readiness band: {readiness.get('band', 'unknown')}",
            ],
        },
        {
            "title": "Primary issues",
            "lines": [str(value) for value in gate.get("issues", [])] or ["no primary issues recorded"],
        },
        {
            "title": "Export actions",
            "lines": [str(value) for value in readiness.get("actions", [])] or ["no export actions required"],
        },
    ]
    manifest = dict(summary.get("manifest_consistency", {}))
    if manifest:
        sections.append(
            {
                "title": "Manifest drift",
                "lines": [str(value) for value in manifest.get("issues", [])] or ["manifest stayed consistent with the reference packet"],
            }
        )
    reconciliation = dict(summary.get("artifact_reconciliation", {}))
    if reconciliation:
        sections.append(
            {
                "title": "Artifact contract",
                "lines": [str(value) for value in reconciliation.get("issues", [])] or ["artifact contract matched expectations"],
            }
        )
    return sections


def release_story(summary: Mapping[str, object]) -> dict[str, object]:
    lane = str(summary.get("lane", "unknown"))
    gate = dict(summary.get("gate", {}))
    readiness = dict(summary.get("export_readiness", {}))
    sections = story_sections(summary)
    return {
        "lane": lane,
        "headline": story_headline(lane, gate, readiness),
        "status": str(gate.get("status", "unknown")),
        "readiness_band": str(readiness.get("band", "unknown")),
        "sections": sections,
        "next_actions": list(readiness.get("actions", [])),
    }


def render_release_story(summary: Mapping[str, object]) -> str:
    story = release_story(summary)
    lines = [f"# {story['headline']}", "", f"- lane: {story['lane']}", f"- gate status: {story['status']}", f"- readiness band: {story['readiness_band']}"]
    for section in story["sections"]:
        lines.extend(["", f"## {section['title']}"])
        for line in section["lines"]:
            lines.append(f"- {line}")
    return "\n".join(lines) + "\n"
