# Lane contract catalog

Lane contracts are the bridge between code and operations. This catalog describes what each major lane family expects.

## Codec lanes

Codec lanes care about quality metrics, codec-family health, and whether the manifest still exposes the required artifacts. The contract should always name required codecs and the acceptable partial-rollout behavior.

## Color lanes

Color lanes use tighter drift thresholds, expected profile names, and stronger required-region language. They should keep advisory histogram drift separate from real required-region failure.

## Alpha lanes

Alpha lanes are strict about premultiplication, halo behavior, and alpha-only mismatches. A lane may tolerate RGB noise while still blocking alpha errors.

## Metadata lanes

Metadata lanes treat EXIF, orientation, capture timestamp, and related fields as part of the shipped artifact. The contract is less about visual output and more about structural correctness.

## Tiling and thumbnail lanes

These lanes need coordinate expectations, tile count rules, and render-budget limits. Throughput and topology are part of the contract, not afterthoughts.

## Partner and export lanes

Partner lanes care about delivery profiles, sidecars, strict digests, and required files. Export lanes add packet-assembly expectations and routing behavior.

## Replay and telemetry lanes

Replay lanes need reproducibility. Telemetry lanes need runtime and packet-volume visibility. Their contracts keep those concerns visible without pretending they are identical to shipping-image surfaces.
