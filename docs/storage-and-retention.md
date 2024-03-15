# Storage And Retention

This page is a compatibility entry point for the older storage notes.

The current detailed references are:

- [storage-retention.md](./storage-retention.md) for retention rules and snapshot handling
- [history-analytics.md](./history-analytics.md) for monthly feeds and SQLite rollups
- [audit-packets.md](./audit-packets.md) for artifact lifetimes tied to exported evidence

Short version:

- SQLite is the local query layer.
- JSONL is the import and replay layer.
- retention is channel-aware and artifact-aware.
- raw run payloads are never pruned before audit evidence exists.
