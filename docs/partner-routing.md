# Partner routing

Partner routing exists so a blocked packet reaches the right humans quickly. The packet should already know the lane owner, release owner, partner owner, and support path.

## Routing rules

- codec issues go first to codec or lane owners
- metadata and export issues go to partner and metadata owners
- packet-digest or manifest issues go to release owners
- replay-only issues can stay with support or replay owners until they affect shipping lanes

## Why this matters

Routing errors look small when the repo is calm. They become expensive during a release window because people rerun work instead of using the packet that already exists.
