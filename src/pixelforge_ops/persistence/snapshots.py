from __future__ import annotations

from contextlib import closing
import sqlite3
from pathlib import Path


def snapshot_tables(path: Path) -> list[str]:
    with closing(sqlite3.connect(path)) as conn:
        rows = conn.execute("select name from sqlite_master where type='table' order by name").fetchall()
    return [row[0] for row in rows]


def history_row_count(path: Path) -> int:
    with closing(sqlite3.connect(path)) as conn:
        row = conn.execute("select count(*) from history_import").fetchone()
    return int(row[0])


def owner_mix(path: Path) -> dict[str, int]:
    with closing(sqlite3.connect(path)) as conn:
        rows = conn.execute("select owner, count(*) from history_import group by owner order by owner").fetchall()
    return {row[0]: int(row[1]) for row in rows}
