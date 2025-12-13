# Imaging incident patterns

The same classes of imaging incidents show up again and again. This doc turns them into named patterns so operators can reason about them faster.

## Silent metadata drift

Visual output stays clean, but the packet blocks because a required metadata field vanished or an ICC profile changed. The fix is usually in the export or metadata path, not the renderer.

## One-family codec regression

Only one codec family degrades while the others stay healthy. The right response is often a lane-limited decision rather than an all-or-nothing block.

## Topology before visibility

Tile or atlas topology breaks before a human viewer notices. Missing rows, overlap, or ordering drift should be trusted even when a screenshot still looks plausible.

## Replay says no, live says maybe

A live rerun looks fine but the replay-backed packet still blocks. Trust the replay packet until the difference is explained, because the replay path is the repo's memory of the original failure.

## Digest drift without visible change

Manifest or packet digest changes even though the image looks the same. That usually means an artifact set, metadata field, or routing detail changed and needs an explicit release note.

## Warning debt accumulation

Several warnings that are individually safe can add up to an operationally risky packet. The operator brief should not pretend they are independent if they all point at the same lane or owner group.

## Handoff mismatch

The machine summary says one thing and the human handoff says another. Treat that as a process bug. The control plane exists to keep those views aligned.
