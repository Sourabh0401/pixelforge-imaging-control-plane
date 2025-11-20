from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data
from pixelforge_ops.utils import json_digest


_DATA = load_json_data("persistence", "saved_query_sql.json")
QUERY_SPECS = tuple(_DATA["query_specs"])


def queries() -> list[dict[str, object]]:
    return [clone_data(spec) for spec in QUERY_SPECS]


def query_spec(query_id: str) -> dict[str, object]:
    for spec in QUERY_SPECS:
        if spec["query_id"] == query_id:
            return clone_data(spec)
    raise KeyError(query_id)


def render_sql(query_id: str) -> str:
    return str(query_spec(query_id)["sql"]) + "\n"


def parameter_names(query_id: str) -> tuple[str, ...]:
    return tuple(query_spec(query_id)["parameters"])


def requires_tables(query_id: str) -> tuple[str, ...]:
    return tuple(query_spec(query_id)["tables"])


def queries_for_owner(owner: str) -> list[dict[str, object]]:
    return [clone_data(spec) for spec in QUERY_SPECS if spec["owner"] == owner]


def digest(query_id: str) -> str:
    return json_digest(query_spec(query_id))


def markdown_catalog() -> str:
    lines = ["# Saved query catalog", ""]
    for spec in QUERY_SPECS:
        lines.append(f"## {spec['title']}")
        lines.append(f"- id: `{spec['query_id']}`")
        lines.append(f"- owner: `{spec['owner']}`")
        lines.append(f"- tables: {', '.join(spec['tables'])}")
        lines.append(f"- parameters: {', '.join(spec['parameters']) or 'none'}")
        lines.append(f"- description: {spec['description']}")
        lines.append("")
    return "\n".join(lines) + "\n"
