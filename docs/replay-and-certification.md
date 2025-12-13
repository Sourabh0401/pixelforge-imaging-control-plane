# Replay and certification flow

The imaging control plane treats replay and certification as one loop. Replay proves what happened. Certification decides what can move.

## Replay flow

Replay lanes start with stored attempts, manifests, and metadata snapshots. The point is to reconstruct a run closely enough that an operator can compare the new output with the last accepted packet.

Good replay packets preserve:

- bundle id and lane
- issue codes
- manifest digest
- codec-family outcome
- enough metadata to explain profile and partner behavior

## Certification flow

Certification is where the lane evidence becomes a release decision. The packet should capture not only the final status but also which gate or comparator forced the decision.

## Why they belong together

A certification decision without replay context is brittle. A replay packet without a certification decision is just a pile of artifacts. The repo keeps them together so an operator can answer ?what changed, why does it matter, and can we ship anyway?? in one place.

## Typical incident pattern

1. replay lane catches the regression
2. operator compares against last accepted packet
3. issue taxonomy assigns owner and family
4. lane gate decides block, warn, or pass
5. certification queue decides whether other lanes can keep moving
6. release note and audit packet freeze the decision

## Shift handoff expectations

A replay packet handed to another shift should be enough to continue work without rerunning the renderer immediately. That means the packet needs digest, issue rollup, lane notes, and the safe next action.
