# Manifest exceptions

Manifest exceptions are narrow policies for cases where the packet changed in a known, bounded way that still does not justify a full block. They are not a shortcut around release quality.

## Allowed use

Use an exception when the packet carries a documented artifact-lineage change, a temporary budget variance, or a planned note that still leaves the shipping contract intact.

## Disallowed use

Do not use an exception to hide:

- missing partner files
- missing required metadata
- missing required tiles
- decode failure in a required codec family
- silent lane-contract drift

## Expiry classes

Exceptions expire. Same-shift exceptions are for immediate coordination. Two-day exceptions are for short-lived operational follow-up. Weekly exceptions are rare and should usually come with a release note update.

## Operator requirement

If an exception downgrades a blocker, the packet must record who accepted it, when it expires, and what remains blocked.
