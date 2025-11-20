from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data


FIELD_DICTIONARY = load_json_data("auditpack", "field_dictionary.json")


def field_definition(name: str) -> dict[str, object]:
    for row in FIELD_DICTIONARY:
        if row["field"] == name:
            return clone_data(row)
    raise KeyError(name)


def required_fields() -> list[str]:
    return [row["field"] for row in FIELD_DICTIONARY if row["required"]]


def fields_for_source(source: str) -> list[str]:
    return [row["field"] for row in FIELD_DICTIONARY if row["source"] == source]
