# Operator handoffs

This repo is built around the idea that imaging release work moves between people and shifts. A good handoff is not optional.

## Minimum handoff content

Every handoff should include:

- lane name
- packet digest
- top issue codes
- current status
- owner group
- safe next action

If any of those are missing, the next shift will spend time rediscovering state instead of moving the release forward.

## What a bad handoff looks like

Bad handoffs are vague. They say ?codec issue? instead of `codec-profile`, or ?manifest changed? without the digest, or ?waiting on partner team? without the specific lane and packet.

## What a good handoff looks like

A good handoff is short but concrete. It names the lane, names the issue code, says whether unaffected lanes can continue, and points to the packet or brief the next person should open first.

## When to write a deeper note

Write a deeper note when:

- a blocker was downgraded by policy
- a partial rollout was allowed
- a partner packet remained blocked while internal lanes continued
- a replay packet became the source of truth for an incident

## Handoff tone

Keep it plain. Avoid internal shorthand that only makes sense to the current shift. The goal is not to sound clever. The goal is to preserve decision context.
