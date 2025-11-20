# Engine Lanes

The PixelForge program is organized around release lanes instead of one flat queue of bundles. That keeps expectations honest. Codec work has very different evidence needs from transform work, and both differ again from partner export drills.

## Current lane model

The control plane supports the following lane families:

- format decode and encode behavior for BMP, PNG, JPEG, and raw interchange lanes
- transform contract stability for resize, rotate, crop, affine, and pixel-grid operations
- filter correctness for blur, sharpen, convolution, histogram, and edge-detection paths
- color management behavior across RGB, grayscale, YCbCr, and export-specific transforms
- compositing, alpha, masking, and draw-surface stability
- reference export and partner interoperability drills
- artifact ingestion, dashboard rollups, and release replay feeds
- exact-output and digest stability checks for audit lanes
- operator rehearsal lanes for release and evidence workflows

Each lane still uses the same durable artifacts:

1. A bundle with metadata, case rows, owner expectations, and release notes.
2. Replay payloads that can be converted into a stable execution transcript.
3. A scorecard with public, hidden, and section-level signals.
4. A release manifest and audit packet for downstream review.

## What lane ownership changes

Lane ownership affects more than dashboard grouping.

- section weights differ by owner and by release channel
- operator playbooks call out different evidence requirements
- rollout quotas are not shared evenly across every lane
- audit repair routing goes to different owner groups
- history rollups need to preserve lane context for trend analysis

That is why the code keeps catalog policy, scoring, release gates, and evidence routing as separate modules instead of flattening everything into one report generator.

## Fixture codenames

In the checked-in corpus, bundle ids still use legacy internal codenames such as `jpeg-codec-fidelity`, `raster-transform-tiling`, and `export-pipeline-integrity`. Those names now map to imaging lanes:

- `jpeg-codec-fidelity` and `partner-format-compatibility` cover codec fidelity and exact-output digest lanes
- `raster-transform-tiling` and `color-profile-parity` cover transform, tiling, and compositing behaviors
- `thumbnail-generation-stability` and `metadata-exif-ingest` cover metadata ingestion, EXIF handling, and export-shape validation
- `export-pipeline-integrity` and `alpha-channel-recovery` cover release, audit, partner replay, and archive integrity paths

The codenames stay because they give the history corpus continuity. The control plane itself stays general enough to handle a wider imaging program without rewiring storage or reporting.
