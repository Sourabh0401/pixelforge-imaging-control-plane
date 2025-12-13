# Tile and atlas diagnostics

Tile lanes fail in ways that are easy to describe once you know the pattern and surprisingly hard to debug when you do not. This doc is the working guide for those failures.

## The main failure classes

### Missing coordinates

A missing coordinate usually means one of three things: a stage dropped a tile, the tile planner miscomputed the grid, or an artifact naming change caused a row to disappear from the manifest. The packet should show the exact coordinate so the operator can compare it with the previous accepted manifest.

### Duplicate coordinates

Duplicate coordinates often point to a replay or stitching bug. They can also appear when two codec outputs race to the same logical tile position. The control plane should keep the codec family visible when that happens.

### Overlap

Overlap tends to come from width or height drift, bad crop math, or a stale tiling profile. It matters because overlap can look visually subtle at first while still breaking consumers that expect non-overlapping boxes.

### Ordering drift

Ordering matters because some consumers digest the tile list directly. A tile list that still covers the same space can break downstream code when ordering changes unexpectedly.

## What operators inspect first

1. tile coverage summary
2. manifest digest and changed paths
3. region diff around the seam or gap
4. transform chain for crop or resize stages
5. recent lane or threshold profile changes

## Atlas-specific concerns

Sprite and atlas lanes care about a few extra things:

- alpha integrity at tile edges
- deterministic atlas frame names
- whether one missing frame affects an active consumer or an unused region
- whether a replacement frame moved to a different coordinate without the manifest documenting it

## Safe downgrade cases

There are only a few cases where a tile issue can be downgraded to watch:

- an unused advisory tile in a pilot lane changed order but not content
- a support-only replay lane emitted an extra non-delivery tile and the packet explains it
- a manifest exception was approved and still left required coordinates intact

Anything that changes required coverage should block.
