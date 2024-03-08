# Operator Runbook

This runbook is for the day someone has to answer, “Is this bundle safe to release, and if not, what do we fix first?”

## Common commands

Catalog health:

```bash
python -m engineering_challenge.cli catalog-summary tests/fixtures/catalog
python -m engineering_challenge.cli validate-bundle tests/fixtures/catalog/merchant-closeout
```

Execution and scoring:

```bash
python -m engineering_challenge.cli run-attempt tests/fixtures/catalog/merchant-closeout tests/fixtures/attempts/merchant-closeout_mixed.json
python -m engineering_challenge.cli build-scorecard tests/fixtures/catalog/merchant-closeout tests/fixtures/attempts/merchant-closeout_mixed.json
```

Release and audit:

```bash
python -m engineering_challenge.cli build-release tests/fixtures/catalog merchant-closeout warehouse-routing --release-id train-17
python -m engineering_challenge.cli build-audit tests/fixtures/catalog/merchant-closeout tests/fixtures/attempts/merchant-closeout_mixed.json --output runtime/merchant-closeout.zip
```

History and SQLite:

```bash
python -m engineering_challenge.cli history-rollup tests/fixtures/history/ops_history_2026_01.jsonl
python -m engineering_challenge.cli snapshot-summary tests/fixtures/sqlite_snapshots/ops_history_2026_q1.sqlite3
python -m engineering_challenge.cli owner-dashboard tests/fixtures/sqlite_snapshots/ops_history_2026_q1.sqlite3 finance_ops
```

## Release-day checklist

1. Validate the bundle before scoring any attempt payloads.
2. Build a scorecard from a representative mixed attempt.
3. Check readiness state and policy flags.
4. Confirm owner capacity and rollout gate status for the channel.
5. Export an audit packet before pruning any raw history.
6. Snapshot the release manifest and scorecard output into the expected artifact directory.

## When a bundle is blocked

Start with the scorecard flags, then look at:

- section-level weak spots
- hidden versus public gap
- owner capacity or blackout constraints
- missing audit evidence
- stale release notes or metadata

Do not jump straight to changing thresholds. A blocked bundle is often telling you that the case set, attempt payload, or release policy moved out of sync.

## When history numbers look wrong

Compare:

1. raw JSONL row count
2. SQLite snapshot table count
3. band counts from `query_service`
4. owner dashboard rollup

If the JSONL feed and SQLite snapshot disagree, inspect schema drift or retention-plan logic before blaming the dashboard.

## Expected recovery moves

- Missing artifact paths: rebuild the packet payload, then re-export
- Bundle metadata drift: fix catalog metadata and rerun validation
- Owner capacity exhaustion: move the bundle to the next train or another approved channel
- Hidden score collapse: inspect hidden cases first, not public ones
- Snapshot schema mismatch: compare the snapshot with `schema_diff` before importing more data

## Local working expectations

The repo is designed to run directly from source. The Makefile and CLI assume the project root as the working directory. Generated artifacts belong under `runtime/` or a temp directory, not beside checked-in fixtures.
