# Release Process

Release in this repo means more than publishing a score. It means packaging enough evidence that another owner can understand why a bundle moved forward, which channel it was meant for, and what staffing assumptions were in play at the time.

## Inputs to a release decision

The release path uses:

- a validated bundle
- one or more scorecards
- owner capacity and blackout data
- rollout matrix rules by channel
- a release manifest id and digest
- a matching audit packet

The process is strict on purpose. Conformance content is only one part of the decision. If the owner is blacked out for the current week, a technically healthy scorecard still cannot ship in the normal lane.

## Readiness states

The readiness module reduces scorecards into three useful states:

- ready
- watch
- blocked

Blocked is reserved for clear release failures such as low total percent or critical policy flags. Watch is a holding area for bundles that are viable but still need a human read because something moved enough to deserve attention.

## Rollout gates

Rollout gates answer two questions:

1. Does this owner still have quota for the target channel?
2. Is there any policy reason we should refuse to schedule this bundle right now?

Channel limits, owner blackouts, and current scheduled counts all factor into the answer. The gate summary should be readable by humans, not only by the test suite.

## Release manifests

The manifest records:

- release id
- timestamp
- bundle membership
- bundle summary stats
- digest
- release notes

The digest is there to make accidental drift obvious. If a supposedly identical release manifest produces a new digest, the operator should assume something real changed until proven otherwise.

## Typical operator flow

1. Validate the bundle.
2. Run representative submissions.
3. Build the scorecard.
4. Inspect readiness notes.
5. Inspect owner capacity and gate results.
6. Build the release manifest.
7. Export the audit packet.
8. Persist history and publish reporting surfaces.

## Failure modes worth separating

- score too low
- hidden score lags badly behind public score
- required review artifacts missing
- owner or channel capacity exceeded
- release digest drift
- blackout week for the owner

Keeping those reasons separate helps downstream routing. Content fixes, release scheduling, and audit repairs are not the same job.
