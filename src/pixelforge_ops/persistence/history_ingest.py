from __future__ import annotations

import json
import sqlite3
from pathlib import Path

REQUIRED_FIELDS = (
    "history_id",
    "bundle_id",
    "owner",
    "percent",
    "hidden_percent",
    "band",
    "started_at",
)


class HistoryRowError(ValueError):
    def __init__(self, message: str, line_number: int | None = None):
        self.line_number = line_number
        prefix = f"line {line_number}: " if line_number is not None else ""
        super().__init__(prefix + message)


def normalize_row(row: dict[str, object], *, line_number: int | None = None) -> dict[str, object]:
    missing = [field for field in REQUIRED_FIELDS if field not in row]
    if missing:
        raise HistoryRowError(f"missing required field(s): {', '.join(missing)}", line_number)

    clean = dict(row)
    for field in ("history_id", "bundle_id", "owner", "band", "started_at"):
        value = str(clean[field]).strip()
        if not value:
            raise HistoryRowError(f"{field} must be non-empty", line_number)
        clean[field] = value

    for field in ("percent", "hidden_percent"):
        try:
            clean[field] = float(clean[field])
        except (TypeError, ValueError) as exc:
            raise HistoryRowError(f"{field} must be numeric", line_number) from exc

    return clean


def load_rows(path: Path) -> list[dict[str, object]]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        text = line.strip()
        if text:
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError as exc:
                raise HistoryRowError("malformed JSON row", line_number) from exc
            if not isinstance(parsed, dict):
                raise HistoryRowError("row must decode to an object", line_number)
            rows.append(normalize_row(parsed, line_number=line_number))
    return rows


def insert_rows(conn: sqlite3.Connection, rows: list[dict[str, object]]) -> None:
    normalized_rows = [normalize_row(row) for row in rows]
    conn.executemany(
        "replace into history_import(history_id, bundle_id, owner, percent, hidden_percent, band, started_at, payload_json) values (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                row["history_id"],
                row["bundle_id"],
                row["owner"],
                row["percent"],
                row["hidden_percent"],
                row["band"],
                row["started_at"],
                json.dumps(row, sort_keys=True),
            )
            for row in normalized_rows
        ],
    )
    conn.commit()


def monthly_rollup(rows: list[dict[str, object]]) -> dict[str, object]:
    normalized = [normalize_row(row) for row in rows]
    if not normalized:
        return {"count": 0, "average_percent": 0.0, "average_hidden_percent": 0.0}
    return {
        "count": len(normalized),
        "average_percent": round(sum(float(row["percent"]) for row in normalized) / len(normalized), 2),
        "average_hidden_percent": round(
            sum(float(row["hidden_percent"]) for row in normalized) / len(normalized), 2
        ),
        "first_started_at": min(str(row["started_at"]) for row in normalized),
        "last_started_at": max(str(row["started_at"]) for row in normalized),
    }


def owner_rollup(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    buckets: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        normalized = normalize_row(row)
        buckets.setdefault(str(normalized["owner"]), []).append(normalized)
    return {
        owner: {
            "count": len(items),
            "average_percent": round(sum(float(item["percent"]) for item in items) / len(items), 2),
            "average_hidden_percent": round(sum(float(item["hidden_percent"]) for item in items) / len(items), 2),
        }
        for owner, items in sorted(buckets.items())
    }


def band_rollup(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    buckets: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        normalized = normalize_row(row)
        buckets.setdefault(str(normalized["band"]), []).append(normalized)
    return {
        band: {
            "count": len(items),
            "average_percent": round(sum(float(item["percent"]) for item in items) / len(items), 2),
        }
        for band, items in sorted(buckets.items())
    }


def month_rollup(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    buckets: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        normalized = normalize_row(row)
        month = str(normalized["started_at"])[:7]
        buckets.setdefault(month, []).append(normalized)
    return {
        month: {
            "count": len(items),
            "owners": sorted({str(item["owner"]) for item in items}),
            "average_percent": round(sum(float(item["percent"]) for item in items) / len(items), 2),
        }
        for month, items in sorted(buckets.items())
    }


def import_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        "monthly": monthly_rollup(rows),
        "owners": owner_rollup(rows),
        "bands": band_rollup(rows),
        "months": month_rollup(rows),
    }
