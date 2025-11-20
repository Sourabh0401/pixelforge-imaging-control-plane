from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data


CONTRACTS = load_json_data("auditpack", "contracts.json")


def artifact_contracts() -> list[dict[str, object]]:
    return [clone_data(item) for item in CONTRACTS["artifact_contracts"]]


def field_contracts() -> list[dict[str, object]]:
    return [clone_data(item) for item in CONTRACTS["field_contracts"]]


def required_artifact_paths() -> list[str]:
    return [item["path"] for item in CONTRACTS["artifact_contracts"]]


def required_fields_for_source(source: str) -> list[str]:
    return [item["field"] for item in CONTRACTS["field_contracts"] if item["source"] == source and item["required"]]


def validate_record_fields(source: str, payload: dict[str, object]) -> list[str]:
    missing = []
    for field in required_fields_for_source(source):
        if payload.get(field) in (None, "", []):
            missing.append(field)
    return missing
