from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data


QUERY_CATALOG = load_json_data("persistence", "query_catalog.json")


def saved_queries() -> list[dict[str, object]]:
    return [clone_data(item) for item in QUERY_CATALOG["saved_queries"]]


def query_by_id(query_id: str) -> dict[str, object]:
    for item in QUERY_CATALOG["saved_queries"]:
        if item["query_id"] == query_id:
            return clone_data(item)
    raise KeyError(query_id)


def materialized_views() -> list[dict[str, object]]:
    return [clone_data(item) for item in QUERY_CATALOG["materialized_views"]]
