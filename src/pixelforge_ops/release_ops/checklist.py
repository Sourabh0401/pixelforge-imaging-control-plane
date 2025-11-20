from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data


CHECKLIST_ITEMS = load_json_data("release_ops", "checklist.json")


def checklist_items(channel: str) -> list[dict[str, object]]:
    return [clone_data(item) for item in CHECKLIST_ITEMS if channel in item["channel_scope"]]


def blocking_items(channel: str) -> list[dict[str, object]]:
    return [clone_data(item) for item in checklist_items(channel) if item["blocking"]]


def group_by_phase(channel: str) -> dict[str, list[dict[str, object]]]:
    output: dict[str, list[dict[str, object]]] = {}
    for item in checklist_items(channel):
        output.setdefault(item["phase"], []).append(clone_data(item))
    return output


def required_files(channel: str) -> list[str]:
    files = []
    for item in checklist_items(channel):
        files.extend(item["required_files"])
    return sorted(dict.fromkeys(files))


def evaluate_checklist(channel: str, present_files: list[str]) -> list[dict[str, object]]:
    present = set(present_files)
    rows = []
    for item in checklist_items(channel):
        missing = [name for name in item["required_files"] if name not in present]
        rows.append({**item, "missing": missing, "passed": not missing})
    return rows
