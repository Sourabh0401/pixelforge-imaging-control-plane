# Image release gates

The image release gate is where PixelForge turns a pile of imaging evidence into a release decision. It should feel strict but explainable. A gate that only says block without telling the operator why is not helping.

## Gate inputs

The gate consumes lane-aware summaries from:

- histogram drift
- weighted color delta
- region diff
- tile coverage
- metadata policy
- codec profile
- render manifest
- partner export validation

The gate does not replace those summaries. It ranks and orders them.

## Ordering rule

Blockers sort by severity first, then by lane, then by issue code. That sounds mechanical, but it matters for operator trust. If two people open the same packet, they should see the same blocker order.

## Mixed-result bundles

A bundle can carry a blocked AVIF lane, a warning-only histogram issue in a color lane, and a clean JPEG lane. The gate should keep those branches visible. It is better to ship an explainable partial decision than to flatten everything into one red light.

## What blocks immediately

These usually block without debate:

- required region mismatch
- tile coverage failure
- missing partner-export file or metadata
- render manifest drift that changed the effective artifact contract
- decode or encode failure in a required codec family

## What usually warns

Warnings are still important, but they do not automatically stop a release:

- histogram drift without region failure
- quantization or preset churn without visible regression
- baseline-envelope movement where the explicit lane thresholds still pass
- operator notes and routing-only annotations

## Lane-local decisions

The release gate should let a lane fail without erasing healthy evidence from neighboring lanes. This is why the repo keeps lane names, codec families, partner state, and operator briefs close together.

## Operator behavior on a block

When a gate blocks, the operator should be able to answer three things immediately:

1. Which issue code caused the block?
2. Which lane or codec family is affected?
3. Is the rest of the bundle still eligible to move?

The gate does not need to make every release decision automatically. It needs to make the next human decision faster and safer.
