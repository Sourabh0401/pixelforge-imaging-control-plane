# Data model

PixelForge keeps a small number of top-level objects and lets each of them carry imaging-specific detail instead of hiding everything in one giant generic blob.

## Bundle

A bundle is the certification unit. It groups cases, metadata, lane ownership, release notes, and rubric settings. Bundles are versioned because release expectations change over time and the team needs to replay older decisions without guessing which contract was active.

Important bundle fields include:

- `bundle_id`
- version
- domain and title
- owner
- metadata such as release channel and author
- cases
- bundle notes and lane-specific playbooks

## Case

A case is one executable comparison unit. Cases define:

- comparator name
- expected payload
- time limit
- hidden or public state
- tags and section
- weight inside the scorecard

Cases should be small enough to explain but rich enough to prove a lane-level concern. In imaging bundles that often means a case is anchored to one comparator family and one lane behavior.

## Attempt run

An attempt run is the normalized result of evaluating a participant or replay payload against a bundle. It captures per-case outcomes, runtime, normalized answers, and top-level pass or fail state. Imaging work uses the same run model for live attempts and replayed certification evidence.

## Imaging signal summaries

The imaging package returns stable summaries rather than raw booleans. Those summaries are part of the data model even when they are transient. Common fields are:

- `status`
- `severity`
- `issues`
- issue-code style fields
- lane name
- deterministic counts or digests

These summaries are designed so audit, release, reporting, and operator surfaces can reuse the same payloads.

## Render manifest

The render manifest is the canonical artifact contract for a lane run. It carries normalized artifacts, metadata, inventory summaries, and a digest. It is not only a reporting artifact. Other systems in the repo treat it as the thing that defines what a lane actually produced.

## Audit packet

An audit packet freezes release evidence into a deterministic export. The packet includes bundle context, run results, issue summaries, and supporting artifacts. In imaging work it can also include lane-level gate or quality information so an operator can explain a block later.

## History row

History ingest converts JSONL rows into SQLite-backed reporting state. Each row captures lane, owner, month, score band, release state, and a stable `history_id`. The ingest path is intentionally strict because a malformed historical row can break trend views without any immediate stack trace.

## Why this model works

The data model stays small at the top and detailed at the edges. That gives the repo two advantages:

1. release, audit, and reporting surfaces can share the same bundle and run objects
2. imaging-specific modules can add richer summaries without forcing a redesign of the whole repo
