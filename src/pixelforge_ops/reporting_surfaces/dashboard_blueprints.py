from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data
from pixelforge_ops.utils import json_digest


DASHBOARD_BLUEPRINTS = load_json_data("reporting_surfaces", "dashboard_blueprints.json")


def blueprint(owner: str) -> dict[str, object]:
    return clone_data(DASHBOARD_BLUEPRINTS[owner])


def primary_panels(owner: str) -> list[str]:
    return list(DASHBOARD_BLUEPRINTS[owner]["primary_panels"])


def drilldowns(owner: str) -> list[str]:
    return list(DASHBOARD_BLUEPRINTS[owner]["drilldowns"])


def alerts(owner: str) -> list[str]:
    return list(DASHBOARD_BLUEPRINTS[owner]["alerts"])


def digest(owner: str) -> str:
    return json_digest(DASHBOARD_BLUEPRINTS[owner])


def render_markdown(owner: str) -> str:
    item = DASHBOARD_BLUEPRINTS[owner]
    lines = [f"# {item['headline']}", "", item["narrative"], "", "## Primary panels"]
    lines.extend(f"- {panel}" for panel in item["primary_panels"])
    lines.extend(["", "## Drilldowns"])
    lines.extend(f"- {entry}" for entry in item["drilldowns"])
    lines.extend(["", "## Alerts"])
    lines.extend(f"- {entry}" for entry in item["alerts"])
    return "\n".join(lines) + "\n"
