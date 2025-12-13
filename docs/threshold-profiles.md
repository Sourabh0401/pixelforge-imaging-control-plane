# Threshold profiles

Threshold profiles are the lane-specific guardrails that keep the imaging comparators honest. Without them, every lane would use the same tolerance numbers and the repo would drift toward either false alarms or silent misses.

## What a profile contains

A profile in PixelForge carries:

- comparator thresholds
- required regions and ignore regions
- render budget limits
- metadata expectations
- watch signals and release blockers
- owner group and release channel

The profile is not only a config convenience. It is the lane contract the rest of the repo uses when it renders briefs and gates.

## Why lanes diverge

### Alpha lanes

Alpha work needs tighter mismatch thresholds and stronger treatment of alpha-only failure paths. A tolerance that is acceptable in a lossy photographic lane may be dangerous here.

### Color lanes

Color work pulls histogram and weighted delta closer together. The profile needs tighter warning and block thresholds because seemingly small drifts can matter on a calibrated surface.

### Thumbnail and tiling lanes

These lanes need explicit tile expectations and render-budget ceilings because throughput and topology both matter.

### Partner lanes

Partner work is strict about metadata, allowed codecs, and digest stability. A threshold profile keeps those expectations near the lane instead of scattering them across ad hoc code branches.

## How to change a profile

1. Update the profile and the lane notes together.
2. Re-run the lane workflow and compare quality report output.
3. Confirm that the operator brief still tells the same story as the machine summary.
4. Capture why the threshold changed in the release note or lane playbook.

## Smells that a profile is wrong

- operators constantly waive the same warning
- one comparator is noisy while the other summaries stay flat
- partner lanes pass visually but keep blocking on metadata
- the profile says one thing and the human playbook says another

The fix is usually to make the lane contract more explicit, not to delete a signal.
