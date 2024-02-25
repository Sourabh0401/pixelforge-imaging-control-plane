# Audit Packets

Audit packets are the product’s answer to the question, “Can we prove what we released and why it was approved?” A packet is not just a convenience export. It is the frozen record the team can hand to finance, compliance, or a release owner three weeks later when a score or rollout decision is challenged.

## Packet contents

Each packet includes:

- release manifest metadata
- bundle summary metadata
- run and scorecard details
- required artifact path map
- trace rows for case-level replay
- field coverage checks
- digest inputs used to stabilize the exported archive

The export path uses deterministic zip entry ordering and fixed timestamps. If two packets were built from the same bundle, attempt, and manifest, the archive payload should remain byte-stable.

## Contracts

The `auditpack.contracts` module describes required artifacts and field obligations. The workbench uses those contracts in two places:

1. during export, to decide what must be present
2. during validation, to explain why an archive is incomplete

This helps with one of the common failure cases in internal release tooling: a packet exists, but the important evidence is either missing or disconnected from the bundle/run pair it belongs to.

## Evidence path rules

Paths are rooted under `bundle_id/run_id/`. That naming convention is intentionally dull. It gives operators a stable way to inspect archives manually and it makes diffing two packets straightforward. The validator treats missing paths, unexpected paths, and field-level gaps as separate problems so a bad archive can be repaired without guessing which contract was broken.

## Trace expectations

Trace rows are case-level summaries derived from the `SubmissionRun`. Each row should preserve:

- case identifier
- section
- status
- runtime
- awarded points
- visibility

The validator checks that trace rows cover the same cases as the run results. A packet with a complete manifest but partial trace content is still considered broken.

## Common audit questions

### Why did a packet digest change?

Start with the manifest payload, then compare bundle summaries, then compare scorecard payloads, and only then look at the zip bytes. The zip export is deterministic after the logical payload is stable.

### Why do we keep field dictionaries in source?

Because packet review is usually done by people who were not part of the original release. A field dictionary is the handoff layer between code and operations. It explains what a value means, where it came from, and whether it is required for replay or only for operator convenience.

### Why are retention rules tied to channel?

Internal and rehearsal releases can often be pruned sooner than partner-facing exports. The audit path needs to encode that policy in one place so storage cleanup does not quietly violate a retention promise.

## Repair workflow

When packet validation fails, the normal workflow is:

1. rebuild the scorecard and trace rows from the same bundle and attempt
2. compare required paths with present paths
3. confirm required fields for each artifact source
4. rebuild the zip only after payload gaps are fixed

The workbench treats repairability as a product feature. A validator that only says “digest mismatch” is not enough; it has to point at the missing or inconsistent evidence.
