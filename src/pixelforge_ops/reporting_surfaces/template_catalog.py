from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data


TEMPLATE_CATALOG = load_json_data("reporting_surfaces", "template_catalog.json")


def owner_panel(owner: str) -> dict[str, object]:
    for item in TEMPLATE_CATALOG["panels"]:
        if item["owner"] == owner:
            return clone_data(item)
    raise KeyError(owner)


def content_blocks() -> list[dict[str, object]]:
    return [clone_data(item) for item in TEMPLATE_CATALOG["blocks"]]


def block_for_section(section: str) -> dict[str, object]:
    for item in TEMPLATE_CATALOG["blocks"]:
        if item["block_id"] == f"block-{section}":
            return clone_data(item)
    raise KeyError(section)
