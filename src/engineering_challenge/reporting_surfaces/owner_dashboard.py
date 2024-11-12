from __future__ import annotations

from engineering_challenge.reporting_surfaces.template_catalog import owner_panel


def owner_dashboard(owner: str, payload: dict[str, object]) -> dict[str, object]:
    panel = owner_panel(owner)
    return {
        "owner": owner,
        "headline": panel["headline"],
        "metrics": payload,
        "callouts": panel["callouts"],
    }


def owner_dashboard_markdown(owner: str, payload: dict[str, object]) -> str:
    item = owner_dashboard(owner, payload)
    lines = [f"# {item['headline']}", ""]
    for key, value in payload.items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Callouts", ""])
    lines.extend(f"- {line}" for line in item["callouts"])
    return "\n".join(lines) + "\n"
