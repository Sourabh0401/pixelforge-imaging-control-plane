# Storage Retention

The repo keeps two durable storage forms: monthly JSONL history feeds and quarterly SQLite snapshots. Both are checked in because the reporting and retention code is part of the product, not a side script.

## Why SQLite

SQLite works well for this tool because operators often run it on laptops or short-lived review hosts. It gives us:

- deterministic local queries
- easy fixture snapshots for tests
- no external service dependency for release rehearsals

The persistence package wraps SQLite access in a small set of query and snapshot helpers so we do not spread raw SQL access all over the repo.

## Stored tables

The main history table contains:

- history id
- bundle id
- owner
- percent
- hidden percent
- band
- started at
- raw payload JSON

Additional tables and query catalogs are treated as derived structures. If they drift or need rebuilding, the raw import history remains the source of truth.

## Retention policy

Retention differs by release channel and artifact class. In practice:

- internal and rehearsal artifacts can age out sooner
- partner and pilot artifacts stay longer
- manifests and scorecards outlive some raw run payloads
- audit packets must exist before pruning happens

The policy module turns those business rules into explicit plans rather than leaving cleanup to ad hoc scripts.

## Schema drift

Snapshots live long enough that schema drift is inevitable. The repo now includes schema comparison helpers so we can answer:

- which tables are missing
- which columns changed type
- which additions are safe
- which differences would break saved queries or dashboards

That is useful both for migration work and for debugging why a fixture snapshot suddenly stopped satisfying a reporting test.

## Safe cleanup rules

Cleanup should follow this order:

1. confirm the audit packet exists for releasable runs
2. confirm the bundle version is stable
3. archive rows that still have operational value
4. prune rows only when policy says the channel and artifact class allow it

Deleting raw payloads before step one defeats the point of keeping an audit path at all.

## Local operator expectations

Operators should treat checked-in SQLite snapshots as read-mostly fixtures. Temporary test databases belong in a temp directory. Snapshot repair belongs in source control so schema and query changes travel together.
