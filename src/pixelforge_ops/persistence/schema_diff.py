from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
import sqlite3
from pathlib import Path


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    declared_type: str
    not_null: bool
    default_value: str | None
    primary_key_order: int


@dataclass(frozen=True)
class TableDiff:
    table: str
    missing_left: tuple[str, ...]
    missing_right: tuple[str, ...]
    changed_types: tuple[str, ...]
    changed_nullability: tuple[str, ...]


def _connect(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(path)


def tables(path: Path) -> tuple[str, ...]:
    with closing(_connect(path)) as conn:
        rows = conn.execute(
            "select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name"
        ).fetchall()
    return tuple(row[0] for row in rows)


def columns(path: Path, table: str) -> tuple[ColumnSpec, ...]:
    with closing(_connect(path)) as conn:
        rows = conn.execute(f"pragma table_info('{table}')").fetchall()
    return tuple(
        ColumnSpec(
            name=str(row[1]),
            declared_type=str(row[2]).upper(),
            not_null=bool(row[3]),
            default_value=row[4],
            primary_key_order=int(row[5]),
        )
        for row in rows
    )


def schema_snapshot(path: Path) -> dict[str, tuple[ColumnSpec, ...]]:
    return {table: columns(path, table) for table in tables(path)}


def table_signature(path: Path, table: str) -> tuple[tuple[str, str, bool, str | None, int], ...]:
    return tuple(
        (column.name, column.declared_type, column.not_null, column.default_value, column.primary_key_order)
        for column in columns(path, table)
    )


def compare_table(left: tuple[ColumnSpec, ...], right: tuple[ColumnSpec, ...], table: str) -> TableDiff:
    left_index = {column.name: column for column in left}
    right_index = {column.name: column for column in right}
    missing_left = sorted(set(right_index) - set(left_index))
    missing_right = sorted(set(left_index) - set(right_index))
    changed_types: list[str] = []
    changed_nullability: list[str] = []
    for name in sorted(set(left_index) & set(right_index)):
        left_column = left_index[name]
        right_column = right_index[name]
        if left_column.declared_type != right_column.declared_type:
            changed_types.append(name)
        if left_column.not_null != right_column.not_null:
            changed_nullability.append(name)
    return TableDiff(
        table=table,
        missing_left=tuple(missing_left),
        missing_right=tuple(missing_right),
        changed_types=tuple(changed_types),
        changed_nullability=tuple(changed_nullability),
    )


def compare_snapshots(left_path: Path, right_path: Path) -> list[TableDiff]:
    left_schema = schema_snapshot(left_path)
    right_schema = schema_snapshot(right_path)
    diffs: list[TableDiff] = []
    all_tables = sorted(set(left_schema) | set(right_schema))
    for table in all_tables:
        diffs.append(compare_table(left_schema.get(table, ()), right_schema.get(table, ()), table))
    return diffs


def breaking_changes(diffs: list[TableDiff]) -> list[TableDiff]:
    return [
        diff
        for diff in diffs
        if diff.missing_right or diff.changed_types or diff.changed_nullability
    ]


def additive_changes(diffs: list[TableDiff]) -> list[TableDiff]:
    return [diff for diff in diffs if diff.missing_left and not diff.missing_right and not diff.changed_types and not diff.changed_nullability]


def schema_health(left_path: Path, right_path: Path) -> dict[str, object]:
    diffs = compare_snapshots(left_path, right_path)
    breaking = breaking_changes(diffs)
    additive = additive_changes(diffs)
    return {
        "table_count_left": len(tables(left_path)),
        "table_count_right": len(tables(right_path)),
        "breaking_count": len(breaking),
        "additive_count": len(additive),
        "tables": [diff.table for diff in diffs if any((diff.missing_left, diff.missing_right, diff.changed_types, diff.changed_nullability))],
    }


def required_tables_missing(path: Path, required: tuple[str, ...] = ("history_import",)) -> list[str]:
    present = set(tables(path))
    return sorted(set(required) - present)


def render_report(left_path: Path, right_path: Path) -> str:
    diffs = compare_snapshots(left_path, right_path)
    lines = [f"# Schema diff", "", f"- left: {left_path.name}", f"- right: {right_path.name}", ""]
    for diff in diffs:
        if not any((diff.missing_left, diff.missing_right, diff.changed_types, diff.changed_nullability)):
            continue
        lines.append(f"## {diff.table}")
        if diff.missing_left:
            lines.append(f"- added on right: {', '.join(diff.missing_left)}")
        if diff.missing_right:
            lines.append(f"- missing on right: {', '.join(diff.missing_right)}")
        if diff.changed_types:
            lines.append(f"- changed types: {', '.join(diff.changed_types)}")
        if diff.changed_nullability:
            lines.append(f"- changed nullability: {', '.join(diff.changed_nullability)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
