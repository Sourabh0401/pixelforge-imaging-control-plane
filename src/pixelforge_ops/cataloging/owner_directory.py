from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data


_DATA = load_json_data("cataloging", "owner_directory.json")
OWNER_DIRECTORY = _DATA["owners"]
ROLE_DIRECTORY = _DATA["roles"]
QUEUE_SERVICE_LEVELS = _DATA["queue_service_levels"]


def owner_row(owner: str) -> dict[str, object]:
    return clone_data(OWNER_DIRECTORY[owner])


def primary_contact(owner: str) -> str:
    return str(OWNER_DIRECTORY[owner]["contacts"]["lead"])


def escalation_chain(owner: str) -> tuple[str, ...]:
    return tuple(OWNER_DIRECTORY[owner]["escalation_chain"])


def owners_by_region(region: str) -> list[str]:
    return sorted(owner for owner, payload in OWNER_DIRECTORY.items() if payload["region"] == region)


def queue_service_level(queue_name: str) -> dict[str, int]:
    return clone_data(QUEUE_SERVICE_LEVELS[queue_name])


def weekly_digest_roles() -> list[str]:
    return [str(row["role"]) for row in ROLE_DIRECTORY if row["requires_weekly_digest"]]
