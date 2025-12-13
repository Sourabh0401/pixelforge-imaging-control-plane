# Storage and retention

The storage layer in PixelForge is intentionally plain. We use SQLite snapshots, JSONL history rows, and deterministic audit zips because the release team needs to inspect artifacts locally and replay old states without a service dependency.

## SQLite usage

SQLite stores imported history rows, dashboard rollups, and saved query outputs used in tests and operator flows. The schema is small, but the data matters because release owners often compare the current month against a previous incident window.

Important properties:

- `history_id` is the replacement key during ingest
- owner, month, band, and bundle identifiers are query dimensions
- dashboard queries should stay deterministic so two runs over the same snapshot produce the same ordering

## JSONL history ingest

History JSONL is the raw interchange format. The ingest layer validates keys, normalizes values, and replaces rows on duplicate `history_id`. This is important for replayability. Operators sometimes rebuild a snapshot from a corrected history file, and the result needs to be predictable.

## Audit packet retention

Audit packets are kept because release decisions need durable evidence. The retention helper focuses on cutoff dates and simple classification rather than opaque policy magic. If a packet should be deleted, an operator ought to be able to explain the rule in one sentence.

## Why deterministic storage matters

A lot of imaging incidents are discovered days after the original release decision. That means the repo must support two tasks well:

1. reopen the evidence that justified a decision
2. compare that evidence against a new replay or a corrected build

If storage order, query order, or packet assembly is unstable, those comparisons get muddy fast.

## Cleanup expectations

Temporary runtime directories, coverage data, and cache junk should never leak into the repo or the final archive. The repo keeps the persistent artifacts that are part of the product story and discards the rest.

## Operator guidance

When working with storage or retention issues:

- preserve the original packet before rebuilding anything
- record the snapshot path or digest used in the investigation
- keep corrected history files separate from the raw capture until validation passes
- avoid editing old packet contents in place; create a new packet and compare digests instead
