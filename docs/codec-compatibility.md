# Codec compatibility

Codec compatibility in PixelForge is lane-aware. We do not use one global ?best codec? rule and hope it fits every surface. A thumbnail lane, a partner packet, a replay lane, and a JPEG fidelity lane each care about different failure modes.

## Codec families we track

### JPEG

JPEG is still the default for many internal surfaces because decode support is universal and artifact size is predictable. The repo treats JPEG as a lane with visible failure modes:

- preset churn that changes ringing or text edge fidelity
- quantization-table drift that makes small text smear at common view sizes
- color-profile loss during transcode handoff
- runtime spikes when a preset change silently increases encoder work

### PNG

PNG shows up in alpha, sprite, partner, and structural lanes. The compatibility problem is usually not ?can we encode PNG?? It is ?did we preserve alpha, metadata, and predictable naming while we did it?? PNG also acts as a reference lane when lossy families drift.

### WebP

WebP is often the middle ground. It can be close to JPEG for photographic content and closer to PNG for alpha-sensitive work, but the operational story matters: some partner lanes allow WebP, some require it, and some keep it as a watch-only optimization. The rollout policy keeps those cases separate.

### AVIF

AVIF is the codec most likely to have longer runtimes and more conditional rollout. That is why the rollout policy gives it larger runtime budgets but still treats decode failure as a hard block. If AVIF drifts and JPEG stays clean, we prefer a lane-limited decision over blocking the entire release blindly.

## Compatibility dimensions

PixelForge evaluates codec families across four dimensions.

### Visual parity

We look at pixel tolerance, color delta, histogram drift, and region requirements. This is the part most people expect.

### Runtime behavior

Some lanes can absorb a modest encode slowdown. Others, especially nightly telemetry and thumbnail surfaces, cannot. Runtime budgets are lane contracts, not informal preferences.

### Manifest and delivery contract

A codec can be visually perfect and still break the release because the manifest no longer lists the files a partner expects, the delivery profile changed, or the lane now emits a different artifact set.

### Lane independence

A codec-family failure should stay local whenever policy allows it. That is why the rollout policy carries `allow_partial_rollout` and per-codec canary percentages. The repo should make it easy to ship healthy lanes while holding the broken family.

## Compatibility matrix use

The compatibility matrix is not only a report. It is also an operator decision aid.

When a release owner sees:

- `jpeg: ok`
- `webp: warn`
- `avif: block`

that should lead to different next steps than a generic failure state. The matrix tells you whether to stop the release completely, continue with a narrower rollout, or gather more evidence without rolling back unrelated codec families.

## Lane-specific rules

### `jpeg-codec-fidelity`

Expect JPEG and WebP together. A missing WebP artifact is a lane issue because we use it as a side-by-side comparison surface. JPEG quantization warnings alone do not always block, but visible region drift does.

### `thumbnail-generation-stability`

This lane can tolerate codec-family divergence if cache keys, runtime budgets, and required manifest rows stay stable. Thumbnail work is often where an AVIF experiment can stay in watch mode while JPEG and WebP continue.

### `partner-format-compatibility`

Partner lanes are strict. Missing required codecs, missing sidecars, or profile mismatches are blockers. We never hide those behind a ?visual pass? label.

### `sprite-identity-refresh`

Sprite work cares about PNG and WebP with alpha-safe handling. Codec compatibility here is really about whether the sheet stays complete and patchable.

## Operator checklist for codec findings

1. Identify the failing codec family and lane.
2. Check whether partial rollout is allowed.
3. Compare the codec issue to manifest and metadata state.
4. Decide whether the healthy families should keep moving.
5. Record the lane-specific decision in the packet and the operator brief.

If the packet cannot tell that story, the codec section is too thin.
