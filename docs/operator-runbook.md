# Operator Runbook

This runbook is for the day someone has to answer, "Is this PixelForge lane safe to ship, and if not, what do we fix first?"

## Common commands

Catalog health:

```bash
python -m pixelforge_ops.cli catalog-summary tests/fixtures/catalog
python -m pixelforge_ops.cli validate-bundle tests/fixtures/catalog/jpeg-codec-fidelity
```

Execution and scoring:

```bash
python -m pixelforge_ops.cli run-attempt tests/fixtures/catalog/jpeg-codec-fidelity tests/fixtures/attempts/jpeg-codec-fidelity_mixed.json
python -m pixelforge_ops.cli build-scorecard tests/fixtures/catalog/jpeg-codec-fidelity tests/fixtures/attempts/jpeg-codec-fidelity_mixed.json
```

Release and audit:

```bash
python -m pixelforge_ops.cli build-release tests/fixtures/catalog jpeg-codec-fidelity raster-transform-tiling --release-id train-17
python -m pixelforge_ops.cli build-audit tests/fixtures/catalog/jpeg-codec-fidelity tests/fixtures/attempts/jpeg-codec-fidelity_mixed.json --output runtime/jpeg-codec-fidelity.zip
```

History and SQLite:

```bash
python -m pixelforge_ops.cli history-rollup tests/fixtures/history/ops_history_2026_01.jsonl
python -m pixelforge_ops.cli snapshot-summary tests/fixtures/sqlite_snapshots/ops_history_2026_q1.sqlite3
python -m pixelforge_ops.cli owner-dashboard tests/fixtures/sqlite_snapshots/ops_history_2026_q1.sqlite3 codec_ops
```

## Release-day checklist

1. Validate the lane before scoring any replay payloads.
2. Build a scorecard from a representative mixed run.
3. Check readiness state and policy flags.
4. Confirm owner capacity and rollout gate status for the channel.
5. Export an audit packet before pruning any raw history.
6. Snapshot the release manifest and scorecard output into the expected artifact directory.

## When a lane is blocked

Start with the scorecard flags, then look at:

- section-level weak spots
- hidden versus public gap
- owner capacity or blackout constraints
- missing audit evidence
- stale release notes or metadata

Do not jump straight to changing thresholds. A blocked lane is often telling you that the image corpus, replay payload, or release policy moved out of sync.

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
- Owner capacity exhaustion: move the lane to the next train or another approved channel
- Hidden score collapse: inspect hidden cases first, not public ones
- Snapshot schema mismatch: compare the snapshot with `schema_diff` before importing more data

## Imaging-specific checks

When the failing lane maps to an imaging workflow, sanity-check the release packet in this order:

1. verify the replay transcript still points at the expected reference artifact family
2. confirm the hidden cases cover the same export modes as the public smoke run
3. inspect the digest and evidence status output before touching lane policy
4. compare the latest scorecard against the prior SQLite snapshot for the same owner and channel

That sequence sounds plain, but it saves a lot of thrash. Many bad release mornings turn out to be digest drift, stale reference outputs, or a lane running against the wrong compatibility profile.

## Local working expectations

The repo is designed to run directly from source. The Makefile and CLI assume the project root as the working directory. Generated artifacts belong under `runtime/` or a temp directory, not beside checked-in fixtures.
