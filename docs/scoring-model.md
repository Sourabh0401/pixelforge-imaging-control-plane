# Scoring Model

The scoring model is meant to be explainable under pressure. An operator should be able to tell whether a bundle missed because public cases failed, hidden cases failed, one section drifted, or a policy flag fired even though the raw percent looked passable.

## Core score inputs

Each scorecard starts from case-level results produced by `evaluate_attempt`. For each case we know:

- section
- visibility
- max points
- earned points
- status
- runtime

The scorer aggregates those rows into:

- total percent
- public percent
- hidden percent
- section totals
- policy flags
- owner id
- release band

## Visibility split

The public-hidden split is deliberate. Internal assessment content tends to drift in hidden cases first because those are changed less often and reviewed by fewer people. If the product only reported one global percent, that signal would disappear.

The scorer therefore keeps:

- public section totals
- hidden section totals
- blended totals only where they are actually useful

## Thresholds and bands

Bands are coarse enough to communicate quickly:

- ready
- watch
- blocked

Threshold helpers live alongside fairness and drift helpers because a band is rarely determined by percent alone. A bundle can be blocked by a large public-hidden gap or a release-review policy even when the blended percent is respectable.

## Policy flags

Common policy flags include:

- `requires-review`
- `public-hidden-gap`
- threshold drift markers
- remediation hints

Flags are part of the scorecard, not an afterthought added in the dashboard layer. That keeps release decisions and audit exports consistent.

## Section rollups

Sections are the operational explanation layer. They tell us where the score moved:

- validation
- execution
- scoring
- catalog
- audit

The exact section set comes from the bundle cases, but the workbench expects enough spread that a bundle is not effectively one opaque metric.

## Fairness and drift

The scoring model includes helpers for fairness and drift detection because assessments can look healthy overall while still becoming biased or brittle in one slice. Trend modules use stored history to catch slow movement that a single run would miss.

## Why late penalties belong in execution input

Runtime penalties are calculated while building case results rather than patched in later. That keeps the scorer simple: it only has to total awarded points, not reinterpret runtime policy after the fact.
