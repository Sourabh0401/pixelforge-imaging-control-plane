# Release decision examples

This doc collects concrete decision patterns the team sees often enough that they should not live only in tribal memory.

## Healthy bundle with one advisory lane

A bundle can carry one advisory lane and still move. The packet should show the advisory issue code, explain why it stayed advisory, and preserve the healthy lane evidence so nobody has to reconstruct that later.

## Partial codec rollout

If a codec family blocks but the lane policy allows partial rollout, the decision should say exactly which family moved, which family stayed back, and how the partner matrix changed because of that split.

## Partner hold with internal continue

Some releases continue internally while a partner-facing lane remains blocked. That is acceptable only when the packet makes the split obvious. The release note should say the internal decision did not imply a partner approval.

## Replay packet as final evidence

When a replay lane is the cleanest reconstruction of a failure and fix, the replay packet may become the final evidence packet. The digest, issue codes, and lane note should make that explicit.

## When to stop and gather more evidence

Stop when:

- the gate and the human brief disagree
- the same issue appears under multiple conflicting codes
- a manifest exception would hide a required-file or metadata failure
- a lane contract changed but the release note did not

That is the point where another quick rerun usually wastes time instead of helping.
