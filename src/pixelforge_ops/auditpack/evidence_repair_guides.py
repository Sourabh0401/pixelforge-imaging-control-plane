from __future__ import annotations

from typing import Mapping

from pixelforge_ops.datafiles import clone_data, load_json_data
from pixelforge_ops.utils import json_digest


REPAIR_GUIDES = load_json_data("auditpack", "evidence_repair_guides.json")
REQUIRED_GUIDE_KEYS = ("owner", "symptoms", "likely_causes", "checks", "repairs")


def _as_text_list(name: str, key: str, value: object) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"repair guide {name} must define a non-empty {key} list")
    cleaned: list[str] = []
    for index, entry in enumerate(value):
        text = str(entry).strip()
        if not text:
            raise ValueError(f"repair guide {name} has a blank {key}[{index}] entry")
        cleaned.append(text)
    return tuple(cleaned)


def validate_guides_data(guides: Mapping[str, object] | None = None) -> dict[str, dict[str, object]]:
    source = dict(guides or REPAIR_GUIDES)
    normalized: dict[str, dict[str, object]] = {}
    for name, raw in sorted(source.items()):
        if not isinstance(raw, Mapping):
            raise ValueError(f"repair guide {name} must be a mapping")
        missing = [key for key in REQUIRED_GUIDE_KEYS if key not in raw]
        if missing:
            raise ValueError(f"repair guide {name} is missing keys: {', '.join(missing)}")
        owner = str(raw["owner"]).strip()
        if not owner:
            raise ValueError(f"repair guide {name} must define a non-empty owner")
        normalized[name] = {
            "owner": owner,
            "symptoms": list(_as_text_list(name, "symptoms", raw["symptoms"])),
            "likely_causes": list(_as_text_list(name, "likely_causes", raw["likely_causes"])),
            "checks": list(_as_text_list(name, "checks", raw["checks"])),
            "repairs": list(_as_text_list(name, "repairs", raw["repairs"])),
        }
    return normalized


VALIDATED_REPAIR_GUIDES = validate_guides_data()


def guide(name: str) -> dict[str, object]:
    return clone_data(VALIDATED_REPAIR_GUIDES[name])


def owners() -> list[str]:
    return sorted({str(item["owner"]) for item in VALIDATED_REPAIR_GUIDES.values()})


def symptoms(name: str) -> list[str]:
    return list(VALIDATED_REPAIR_GUIDES[name]["symptoms"])


def checks(name: str) -> list[str]:
    return list(VALIDATED_REPAIR_GUIDES[name]["checks"])


def repairs(name: str) -> list[str]:
    return list(VALIDATED_REPAIR_GUIDES[name]["repairs"])


def guide_digest(name: str) -> str:
    return json_digest(VALIDATED_REPAIR_GUIDES[name])


def guide_names() -> list[str]:
    return sorted(VALIDATED_REPAIR_GUIDES)


def owner_routes() -> dict[str, list[str]]:
    routes: dict[str, list[str]] = {}
    for name, payload in VALIDATED_REPAIR_GUIDES.items():
        routes.setdefault(str(payload["owner"]), []).append(name)
    return {owner: sorted(names) for owner, names in sorted(routes.items())}


def render_markdown(name: str) -> str:
    item = VALIDATED_REPAIR_GUIDES[name]
    lines = [f"# {name} repair guide", "", f"- owner: {item['owner']}", "", "## Symptoms"]
    lines.extend(f"- {entry}" for entry in item["symptoms"])
    lines.extend(["", "## Likely causes"])
    lines.extend(f"- {entry}" for entry in item["likely_causes"])
    lines.extend(["", "## Checks"])
    lines.extend(f"- {entry}" for entry in item["checks"])
    lines.extend(["", "## Repairs"])
    lines.extend(f"- {entry}" for entry in item["repairs"])
    return "\n".join(lines) + "\n"

