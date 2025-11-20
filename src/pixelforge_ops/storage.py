from __future__ import annotations

from contextlib import closing
import sqlite3
from pathlib import Path

from .models import ExerciseBundle, Scorecard, SubmissionRun
from .release import manifest_to_dict
from .scoring import scorecard_to_dict
from .utils import stable_json


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize(path: Path) -> None:
    with closing(connect(path)) as conn:
        conn.executescript(
            '''
            create table if not exists bundle_summary (
                bundle_id text primary key,
                owner text not null,
                domain text not null,
                version text not null,
                summary_json text not null
            );
            create table if not exists submission_run (
                run_id text primary key,
                bundle_id text not null,
                participant_id text not null,
                scorecard_json text,
                run_json text not null
            );
            create table if not exists release_manifest (
                release_id text primary key,
                manifest_json text not null
            );
            '''
        )
        conn.commit()


def record_bundle(path: Path, bundle: ExerciseBundle, summary: dict[str, object]) -> None:
    initialize(path)
    with closing(connect(path)) as conn:
        conn.execute(
            "replace into bundle_summary(bundle_id, owner, domain, version, summary_json) values (?, ?, ?, ?, ?)",
            (bundle.bundle_id, bundle.owner, bundle.domain, bundle.version, stable_json(summary)),
        )
        conn.commit()


def record_run(path: Path, run: SubmissionRun, scorecard: Scorecard) -> None:
    initialize(path)
    with closing(connect(path)) as conn:
        conn.execute(
            "replace into submission_run(run_id, bundle_id, participant_id, scorecard_json, run_json) values (?, ?, ?, ?, ?)",
            (
                run.run_id,
                run.bundle_id,
                run.participant_id,
                stable_json(scorecard_to_dict(scorecard)),
                stable_json(
                    {
                        "run_id": run.run_id,
                        "bundle_id": run.bundle_id,
                        "participant_id": run.participant_id,
                        "profile": run.profile,
                        "started_at": run.started_at,
                        "finished_at": run.finished_at,
                        "notes": list(run.notes),
                        "case_results": [result.__dict__ for result in run.case_results],
                    }
                ),
            ),
        )
        conn.commit()


def record_release(path: Path, release_manifest) -> None:
    initialize(path)
    with closing(connect(path)) as conn:
        conn.execute(
            "replace into release_manifest(release_id, manifest_json) values (?, ?)",
            (release_manifest.release_id, stable_json(manifest_to_dict(release_manifest))),
        )
        conn.commit()


def recent_runs(path: Path, limit: int = 10) -> list[dict[str, object]]:
    initialize(path)
    with closing(connect(path)) as conn:
        rows = conn.execute(
            "select run_id, bundle_id, participant_id, scorecard_json from submission_run order by rowid desc limit ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def owner_rollup(path: Path) -> dict[str, int]:
    initialize(path)
    with closing(connect(path)) as conn:
        rows = conn.execute(
            "select owner, count(*) as bundle_count from bundle_summary group by owner order by owner"
        ).fetchall()
    return {str(row["owner"]): int(row["bundle_count"]) for row in rows}
