# Troubleshooting

This guide is for the annoying cases where the repo technically runs but the results do not make sense yet.

## `make test` hangs or takes too long

The CLI tests should run in-process now. If test time suddenly spikes again:

1. check for a new subprocess-based test
2. inspect temp directory cleanup in persistence tests
3. confirm no generated artifact was written into the fixture tree

If the suite completes but the process does not exit, look first for an unclosed SQLite connection or a lingering pipe from a CLI helper.

## Scorecard percent looks wrong

Compare the following in order:

1. raw `SubmissionRun` totals
2. public versus hidden percentages
3. section totals
4. policy flags

Most score surprises are explained by hidden-case performance or timeout penalties, not by a broken average formula.

## Release gate says blocked unexpectedly

Inspect:

- current owner count for the channel
- blackout status for the target week
- readiness state from the scorecard
- any missing checklist or audit evidence items

The gate is supposed to be strict. A “blocked” result can be correct even when the score itself looks healthy.

## Owner dashboard and snapshot numbers disagree

Start with the snapshot:

```bash
python -m engineering_challenge.cli snapshot-summary tests/fixtures/sqlite_snapshots/ops_history_2026_q1.sqlite3
```

Then compare against the JSONL feed rollup:

```bash
python -m engineering_challenge.cli history-rollup tests/fixtures/history/ops_history_2026_01.jsonl
```

If the two disagree, inspect schema drift or retained row count before assuming the reporting layer is wrong.

## Audit packet digest changed

Compare:

1. manifest digest input
2. packet JSON payload
3. evidence path map
4. trace rows

Only look at raw zip bytes after the payload matches. The export code uses deterministic ordering, so a byte-level change usually means the logical packet changed first.

## Windows temp cleanup fails

This usually means something still has a SQLite file open. The persistence helpers are written to close connections explicitly, but tests that open raw `sqlite3.connect(...)` handles still need to wrap them safely.

## Import path surprises when running scripts directly

Run commands from the repo root or set `PYTHONPATH=src:tests`. The project is structured to support in-repo execution without an editable install, but the working directory still matters for fixture-relative paths.
