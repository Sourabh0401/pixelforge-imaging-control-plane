# Data Model

This file is a short compatibility guide for teammates who still look for the older data-model notes.

The detailed model docs now live in:

- [catalog-model.md](./catalog-model.md) for bundle and case authoring
- [scoring-model.md](./scoring-model.md) for scorecard math and policy flags
- [storage-retention.md](./storage-retention.md) for SQLite snapshots, history imports, and retention planning

At a high level, the system revolves around four durable shapes:

1. `ExerciseBundle`, which is the authoring unit for a codec, transform, color, compositing, or export lane
2. `SubmissionRun`, which is the replay and comparison record
3. `Scorecard`, which is the release decision surface
4. `ReleaseManifest`, which is the frozen train record

Those types are intentionally reused across CLI, release, audit, and persistence paths so operators can compare outputs without losing context between modules.
