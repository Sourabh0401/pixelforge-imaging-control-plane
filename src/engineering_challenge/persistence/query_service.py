from __future__ import annotations

from contextlib import closing
import json
import sqlite3
from pathlib import Path


def recent_history(path: Path, limit: int = 10) -> list[dict[str, object]]:
    with closing(sqlite3.connect(path)) as conn:
        rows = conn.execute(
            "select payload_json from history_import order by started_at desc limit ?",
            (limit,),
        ).fetchall()
    return [json.loads(row[0]) for row in rows]


def band_counts(path: Path) -> dict[str, int]:
    with closing(sqlite3.connect(path)) as conn:
        rows = conn.execute("select band, count(*) from history_import group by band order by band").fetchall()
    return {row[0]: int(row[1]) for row in rows}


def owner_average(path: Path) -> dict[str, float]:
    with closing(sqlite3.connect(path)) as conn:
        rows = conn.execute("select owner, avg(percent) from history_import group by owner order by owner").fetchall()
    return {row[0]: round(float(row[1]), 2) for row in rows}
