# Color profile policy

Color policy in PixelForge is stricter than a typical image diff setup because the repo sits between renderer changes, release decisions, and partner export validation. A file that renders ?close enough? can still be wrong if it drops an ICC profile, changes gamut unexpectedly, or moves a lane from P3 to sRGB without a planned contract change.

## What we enforce

### Embedded profile presence

Lanes that feed partner export or archive workflows expect an embedded profile, not only a display hint. If the embedded profile disappears, the packet should block. Internal-only lanes can warn when the lane profile says the change is advisory, but the operator brief still has to record it.

### Allowed profile names

The policy currently expects names such as `sRGB`, `Display P3`, and `Rec.709`. The point is not brand purity. The point is to keep profile changes explicit and machine-checkable. If a renderer starts emitting an unfamiliar label, the team should evaluate it deliberately instead of letting it slide through as a silent rename.

### Allowed gamuts and transfer functions

Gamut and transfer checks matter because some regressions are not obvious from the profile name alone. A packet that claims Display P3 but behaves like sRGB is still a problem. The policy keeps those fields separate for that reason.

### Hard-block metadata fields

Partner and export lanes raise the bar. Missing `icc_profile`, `delivery_profile`, or other lane-critical metadata should block even when the pixel result still looks fine. This is one of the main differences between an internal renderer repo and an imaging control plane.

## Drift types

### Advisory drift

Advisory drift is the class of problem that should surface in the brief but does not automatically stop the release. Examples:

- profile name formatting changes with no digest or gamut change
- harmless order differences in sidecar metadata
- a lane where the same render remains clean and partner export is unaffected

### Warning drift

Warnings mean an operator should pay attention. Examples:

- histogram movement concentrated in channels tied to color management
- color-delta movement that still stays out of required regions
- profile or gamut changes in an internal lane with no partner dependency

### Blocking drift

Block when:

- required ICC or delivery metadata is missing
- a lane drops an embedded profile that downstream consumers require
- the effective profile or gamut changes in a partner or export lane
- required regions and color policy drift together, which usually signals a real rendering bug rather than paperwork noise

## How operators should read the policy

Start with the lane. `color-profile-parity` and `partner-format-compatibility` should not be read the same way. The policy modules return machine summaries, but the operator brief should still explain the lane context in plain language.

Look for these combinations:

- profile issue + no region diff: probably a metadata or packaging problem
- profile issue + region diff + histogram drift: likely real rendering or color-transform regression
- no profile issue + region diff: probably a raster or transform bug rather than color policy

## Release notes and partner communication

When a color policy issue blocks a release, the release note should say which lane moved, which profile or gamut changed, whether partner packets were affected, and what evidence the team used to decide. That keeps support and partner teams from rediscovering the same context later.
