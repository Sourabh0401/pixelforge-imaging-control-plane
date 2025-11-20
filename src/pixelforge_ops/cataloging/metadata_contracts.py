from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data


_DATA = load_json_data("cataloging", "metadata_contracts.json")
METADATA_CONTRACTS = _DATA["metadata_contracts"]
OWNER_CONTACTS = _DATA["owner_contacts"]


def required_fields(channel: str) -> list[str]:
    return [row["field"] for row in METADATA_CONTRACTS if channel in row["channels"] and row["required"]]


def fields_for_section(section: str) -> list[str]:
    return [row["field"] for row in METADATA_CONTRACTS if section in row["sections"]]


def contact_for_owner(owner: str) -> dict[str, str]:
    return clone_data(OWNER_CONTACTS[owner])
