# Render manifest

The render manifest is the contract between a lane run and every downstream surface that consumes its artifacts. A digest-stable manifest is one of the clearest signs that a release remained operationally safe.

## What the manifest records

A render manifest in PixelForge should carry:

- bundle id
- lane name
- release channel
- normalized artifact rows
- lane contract snapshot
- metadata snapshot
- inventory summary
- deterministic digest

The digest is computed over the manifest payload without the digest field itself. That seems obvious, but it matters because several tools touch the payload after it is assembled.

## Why the manifest blocks releases

Visual parity is not enough when the contract around the file set changes. A release can render the same pixels and still break consumers because:

- a required codec row disappeared
- a tile moved or went missing
- artifact naming changed and broke cache lookup
- metadata drift changed the packet meaning
- the lane emitted a new artifact type without the release note and downstream readers to match

That is why `render-manifest` is a dedicated issue code and not merely an appendix to image comparison.

## Digest stability rules

We expect the digest to change only when one of these things happened intentionally:

1. the artifact set changed
2. the lane metadata changed
3. the lane contract changed
4. the release channel or partner packaging rules changed

If the digest changes and none of those statements are true, the control plane should treat it as suspicious.

## Tile-aware validation

Tiled lanes push more work into manifest validation. A tile manifest is not just a list of files. It also carries coordinate and coverage expectations. Missing rows, duplicate positions, and path collisions should show up here before a consumer sees a broken atlas or map grid.

## Operator flow when manifest drift appears

1. Compare the current manifest to the last accepted manifest.
2. Check added, removed, and changed artifacts.
3. Decide whether the change is lane-local or partner-visible.
4. If the change was planned, confirm that the release note and partner packet reflect it.
5. If the change was not planned, stop and route the issue through the release gate.

## What a healthy manifest section looks like

A healthy manifest section should tell an operator, in one glance:

- how many artifacts were emitted
- which codecs are represented
- whether the digest changed
- whether tile coverage is complete
- whether partner-required files are present

If a packet forces the operator to reconstruct that from raw JSON by hand, the manifest layer is under-built.
