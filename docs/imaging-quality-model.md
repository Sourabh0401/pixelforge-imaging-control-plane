# Imaging quality model

PixelForge does not treat image quality as a single boolean. A lane moves through a stack of checks: pixel tolerance, perceptual hash, channel histogram drift, weighted color delta, region requirements, tile topology, metadata policy, codec profile health, and release gating. The point of the model is to keep those signals separate until the very end. That way the release owner can see whether a failure came from a visual regression, a manifest contract break, or a partner export issue that has nothing to do with visible pixels.

## The model in practice

A clean lane usually has an `ok` result for every comparator, an `ok` render manifest, and a release gate with no blocker codes. That is the easy case.

The harder cases are the ones we care about operationally:

- A lane is visually clean but metadata drift breaks partner export.
- A JPEG regression blocks one codec family while PNG and WebP remain healthy.
- Tile coverage fails even though the final composite image still looks plausible.
- Histogram drift shows the first sign of a color-management problem before region diff is loud enough to fail.
- Alpha-only errors create halos that are easy to miss if someone only looks at RGB deltas.

The quality model keeps those stories distinct. We do not want to collapse them into a generic ?failed image comparison? state.

## Signal hierarchy

### Pixel tolerance

Pixel tolerance is the shortest path to saying two matrices are close enough for a lane contract. It still matters, but it is not enough on its own. The renderer can preserve most pixels and still ship a broken partner packet or a tile manifest with missing coordinates.

Pixel tolerance is strongest in lanes where the expected output is tiny and stable. Sprite and thumbnail work often starts here.

### Perceptual hash

Perceptual hash catches broad visual drift where a strict pixel diff would be noisy or brittle. We use it as a sanity check rather than a final release gate. Hash distance is bucketed into operator-friendly language because a low numeric distance does not help the on-call shift very much on its own.

### Channel histogram drift

Histogram drift is the earliest signal for a color-concentration shift. It is useful when a release still ?looks right? in a screenshot but the distribution of color or alpha values moved in a way that will matter for downstream surfaces. The histogram check should not block lanes casually. It should explain why the color team needs to look closer.

### Weighted color delta

Color delta is where the repo moves from simple mismatch counting into lane-aware judgment. We use weighted aggregates because alpha and green-channel drift are not equally important across every surface. The weighted summary is machine-checkable, but it is also meant to be readable in a packet or a release brief.

### Region requirements

Region diff is the first place we ask ?where did the drift happen?? instead of only ?how much drift happened?? Required regions are release-signoff surfaces. Ignore regions are tightly scoped and must stay documented. We use them for debug overlays, operator watermarks, or one-off telemetry stamps that should not block shipping.

### Tile topology

Tile coverage is structural. Missing tiles, duplicate coordinates, overlapping boxes, and bad ordering are not visual opinions. They are production failures. Tiling lanes stay strict because a single bad coordinate can surface as a broken map, atlas, or preview grid long after the release owner forgot the details.

### Metadata policy

Metadata is part of the product surface. ICC profiles, EXIF orientation, partner contracts, and delivery profiles affect where the image can go. Metadata warnings are allowed only when the lane contract says the drift is advisory. Partner and export lanes are much stricter.

### Codec profile health

Codec health is the place where runtime, PSNR, SSIM-like proxies, and decode or encode failures live together. A lane can allow partial rollout for one codec family while blocking another, but the packet needs to make that explicit. We do not hide a healthy PNG lane because AVIF is having a bad day.

### Release gate

The release gate is deliberately late in the flow. It should consume richer summaries, not replace them. By the time we call the gate, every issue should already have a code, a severity, and a lane context.

## What blocks and what warns

The model draws a clear line between blocking and warning states.

Blockers usually mean one of these things:

- required region mismatch
n- tile topology problem
- render manifest contract drift
- metadata policy violation in a partner or export path
- codec-family failure where the lane does not allow partial rollout
- partner packet missing required files or required metadata

Warnings are for issues that still need attention but do not automatically stop shipping:

- histogram drift without visible region failure
- color delta above watch threshold but below block threshold
- baseline-envelope movement that still stays inside the explicit lane gate
- JPEG quantization or preset churn when the visible output still passes lane rules
- operator notes and handoff-only issues

## Why multiple summaries matter

The same release week can carry all of these states at once:

- a blocking tile gap in `raster-transform-tiling`
- a warning-only histogram shift in `color-profile-parity`
- a clean `jpeg-codec-fidelity` lane
- a blocked partner packet in `partner-format-compatibility`

That is normal. The job of the control plane is to preserve the shape of the failure so the team can ship the healthy lanes and hold the broken ones.

## Operator expectations

Operators should leave the repo with these answers every time:

1. Which lane failed?
2. Which comparator or policy saw the failure first?
3. Was the problem visual, structural, metadata-related, or partner-related?
4. Can unaffected lanes continue?
5. What should the next shift inspect before asking for another rerender?

If the packet cannot answer those questions, the quality model is not doing enough work.
