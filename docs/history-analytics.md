# History Analytics

The workbench stores history as monthly JSONL feeds and quarterly SQLite snapshots because those two forms solve different problems.

- JSONL is the append-friendly import format.
- SQLite is the query-friendly analysis format.

Both are first-class artifacts. The repo carries a large history corpus because it needs enough shape to exercise owner rollups, drift summaries, release windows, and retention planning under realistic load.

## Monthly feeds

Each JSONL row captures:

- bundle and owner identity
- public and hidden score percentages
- release channel
- review state
- queue latency
- digest identifiers
- section-level scores
- worker version

The monthly feeds are the easiest place to answer questions like “when did the hidden score start sagging for this owner?” or “which release channel saw the spike in review latency?”

## SQLite snapshots

Quarterly snapshots exist so operator tooling can run fast local queries without reparsing raw JSONL files. The persistence package exposes:

- recent history readers
- band counts
- owner averages
- schema comparison helpers
- dashboard and saved-query catalogs

Snapshots are also handy in test runs because they let us validate query shape against a fixed schema rather than rebuilding a temporary database for every assertion.

## Rollups that matter

The product uses a few rollups repeatedly:

- owner average percent
- band counts by channel
- public-hidden gap counts
- release readiness movement over time
- queue latency distribution
- top at-risk owners

The history fixtures were built to make those rollups nontrivial. A history corpus with only five rows would not tell us whether the reporting code actually holds up when a review month gets messy.

## Drift analysis

History analytics is also where we catch scoring drift. The same bundle can look fine in a one-off scorecard and still show a slow trend downward over a quarter. That is why trend analysis lives next to storage and reporting rather than inside the core scoring function.

## Operator usage

Normal operator flow:

1. import or inspect the latest month feed
2. compare owner averages against readiness thresholds
3. inspect channel-specific band counts
4. open an at-risk owner summary
5. review whether the bundle needs a release gate change, a rubric update, or a case-authoring correction

The workbench is not trying to be a general BI tool. It is trying to be dependable at exactly these release-ops questions.
