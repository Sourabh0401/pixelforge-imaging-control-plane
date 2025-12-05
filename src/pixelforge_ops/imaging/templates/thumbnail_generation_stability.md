# Thumbnail Generation Stability operator template

## What this lane protects
Thumbnail work has real budget pressure, so include render size, runtime, and cache-key impact in every handoff.

## Signals that matter
- Compare the lane digest, render manifest, and issue digest before you try a rerun.
- Separate lane-specific blockers from broader bundle health so a single codec regression does not hide clean work elsewhere.
- Keep partner-export state explicit. An apparently harmless metadata change can still break downstream validation.

## First-pass triage
1. Confirm the active release channel for `thumbnail-generation-stability` is still `pilot` and that the packet was built from the expected bundle.
2. Read the machine summary, then pull the human brief. The control plane is supposed to tell the same story in both places.
3. Compare the current packet against the last accepted packet. Check digest drift, changed paths, and any lane-specific warnings.
4. Decide whether the lane is blocked, watch-only, or safe to continue. Write that decision down before you hand work to another team.

## Required artifacts
- render manifest JSON
- quality report markdown
- operator brief markdown
- issue digest payload
- partner or archive sidecars when the lane feeds an external consumer

## Questions to answer before unblocking the lane
- Did the drift land in a required region or only a debug or advisory region?
- Did the manifest contract change, or did the packet only reorder artifacts while staying digest-stable?
- Is the regression isolated to one codec family, one partner profile, or one replay path?
- If this lane can move in watch mode, what evidence proves the unaffected lanes are still green?

## Handoff notes
Write the handoff as if the next person will look at it at 3 AM during an incident. Keep the lane name, digest, issue codes, and safe next action in the first screenful.

## Escalation map
- Lane owner group: `thumbnail-ops`
- Release owner group: `release-ops`
- Support owner group: `support-ops`
- Partner owner group: `partner-ops` when an external packet is in play

## When a warning is still allowed to ship
Warnings can move forward only when the packet records why the warning is safe, the unaffected lanes remain machine-checkable, and the next operator can reproduce the same decision from the brief.

## Common mistakes
- Treating a lane-level watch signal as a pass without checking whether the same issue becomes a blocker for partner export.
- Re-running the renderer before saving the original manifest digest and issue summary.
- Collapsing multiple codec-family outcomes into one generic decision, which hides healthy lanes and slows down release work.

## Longer notes
The `thumbnail-generation-stability` lane exists because image releases fail in different ways depending on codec, metadata, transform ordering, alpha handling, and export policy. This template keeps those branches explicit. For this lane, operators should pay extra attention to thumbnail work has real budget pressure, so include render size, runtime, and cache-key impact in every handoff.
The goal is not just to say pass or fail. The goal is to leave behind enough structured evidence that the next shift can make the same decision without re-learning the lane from scratch. That is why the control plane carries manifest digests, machine summaries, owner routing, and operator prose together.
