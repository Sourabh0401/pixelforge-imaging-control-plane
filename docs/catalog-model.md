# Catalog Model

The catalog is the durable authoring layer for the workbench. It holds bundles, case rows, owner metadata, release annotations, and the workflow contracts that tell the rest of the system how a bundle is supposed to be reviewed.

## Bundle shape

A bundle is defined by:

- `bundle_id`
- `version`
- `domain`
- `owner`
- `title`
- `tags`
- `rubric`
- `metadata`
- `cases`

The source fixture format keeps metadata in `bundle.json` and case rows in `cases.jsonl`. That split makes version review easier. Metadata changes are usually policy or ownership changes. Case-row changes tend to be scoring or comparator changes.

## Case shape

Each case row becomes an `AssessmentCase` with:

- a stable `case_id`
- a `section`
- a `comparator`
- a `difficulty`
- a visibility flag
- a weighted point value
- a runtime budget
- input payload and expected output

The catalog loader preserves these fields exactly because downstream drift debugging depends on them. A small change in comparator type or visibility can move hidden scores, policy flags, and readiness state all at once.

## Ownership metadata

Ownership is not cosmetic here. The catalog stores enough information to answer:

- who authors the bundle
- who reviews it during release week
- which channel it normally ships through
- whether notes are required on the rubric

That is why the repo includes owner directories, policy matrices, review playbooks, and workflow contracts in source. The same bundle can be technically valid while still missing an operational requirement, such as the right owner handoff or a release checklist attachment.

## Workflow contracts

Workflow contracts describe the non-code expectations around a bundle:

- required evidence artifacts
- review handoff steps
- downstream consumers
- escalation routes
- release blockers

These contracts are used to flag gaps early. A bundle with a full case list but missing an escalation path is not ready for a real control-room rollout.

## Summary and indexing helpers

The loader package exposes summary and indexing helpers because release tooling asks bundle-level questions far more often than it asks for raw rows:

- case count by section
- public versus hidden mix
- comparator mix
- duplicate case identifiers
- owner-normalized token

The repo keeps these helpers close to the loader so one piece of code defines what a healthy bundle summary means.

## Authoring expectations

Bundles should:

- include both public and hidden cases
- spread across meaningful sections
- use stable comparator types
- keep release notes and owner metadata current
- avoid duplicate `case_id` values

The test suite leans on those expectations heavily. Many release and reporting tests are really catalog regression tests wearing a different hat.
