from __future__ import annotations


MIGRATIONS = [
    {
        "version": 1,
        "name": "bundle_summary",
        "sql": "create table if not exists bundle_summary (bundle_id text primary key, owner text not null, domain text not null, version text not null, summary_json text not null)",
    },
    {
        "version": 2,
        "name": "submission_run",
        "sql": "create table if not exists submission_run (run_id text primary key, bundle_id text not null, participant_id text not null, scorecard_json text, run_json text not null)",
    },
    {
        "version": 3,
        "name": "release_manifest",
        "sql": "create table if not exists release_manifest (release_id text primary key, manifest_json text not null)",
    },
    {
        "version": 4,
        "name": "history_import",
        "sql": "create table if not exists history_import (history_id text primary key, bundle_id text not null, owner text not null, percent real not null, hidden_percent real not null, band text not null, started_at text not null, payload_json text not null)",
    },
]


def latest_version() -> int:
    return MIGRATIONS[-1]["version"]


def migration_sql() -> list[str]:
    return [item["sql"] for item in MIGRATIONS]
