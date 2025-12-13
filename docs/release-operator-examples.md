# Release operator examples

This document is a set of realistic examples for how the control plane should be used during release work.

## Example: codec-only regression in a mixed bundle

The bundle contains `jpeg-codec-fidelity`, `color-profile-parity`, and `thumbnail-generation-stability`.

Observed state:

- JPEG lane is green
- AVIF path in thumbnail lane is blocked on runtime and PSNR
- color lane warns on histogram drift but passes region diff

Operator call:

- keep JPEG lane moving
- hold AVIF thumbnail rollout to pilot-only follow-up
- record the color warning in the packet and preserve the lane digest for later comparison

Why this is safe:

The healthy lane stays visible, the blocked codec family stays explicit, and the packet still tells one coherent story.

## Example: partner export block without visible image drift

The lane passes pixel, hash, and region checks but fails metadata policy because the ICC profile disappeared.

Operator call:

- block the partner lane
- keep the machine summary and operator brief aligned on `metadata-policy`
- avoid calling it a visual regression in the release note

Why this matters:

Support and partner teams need to know this is a contract issue, not a rendering issue.

## Example: tile coverage failure with stable manifest digest

The manifest digest can remain stable if the lane reused an old manifest or if the same paths were emitted with bad coordinates. That is why tile coverage is separate from digest validation.

Operator call:

- inspect coverage summary and changed paths together
- compare seam or region summaries near the missing coordinate
- hold the lane until topology is clean

## Example: approved exception

A lane carries an approved manifest exception for a temporary artifact-lineage issue.

Operator call:

- downgrade only the allowed issue
- keep blocked issue codes blocked
- include expiry and accepting owner in the brief

## Example: replay-driven certification

A decoder recovery replay lane reconstructs a past incident. The new packet matches the old digest except for one lane note.

Operator call:

- keep the replay packet as the evidence source of truth
- certify the healthy lanes using the replay-backed packet
- note the lane note drift as advisory only if the policy allows it
