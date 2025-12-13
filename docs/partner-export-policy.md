# Partner export policy

Partner export is where PixelForge stops being an internal rendering concern and becomes an external contract problem. This document is the operational policy behind the partner lanes.

## Why partner export is stricter

Partner consumers cache, validate, transform, and sometimes archive what we send them. Once a bad packet escapes, rollback is slower and harder than an internal rerender. That is why partner export treats file presence, ICC data, delivery profiles, and manifest stability as release-critical signals.

## Required packet pieces

Every partner packet should carry the lane render manifest, a machine-readable issues payload, a human brief, and the files the partner profile marks as required. Some lanes also require tile spreadsheets or sidecars. If the packet is missing one of those pieces, the lane should block immediately.

## Profile-specific behavior

### Retail storefronts

Retail lanes care about stable display profiles, deterministic filenames, and sidecars that match the manifest digest. They are less tolerant of metadata drift because their ingestion checks are usually strict and front-loaded.

### Marketplace feeds

Marketplace feeds need fallback codec coverage and predictable dimensional metadata. A marketplace lane can stay in watch mode for a codec-specific issue only when the required fallback family stays healthy and the manifest contract is unchanged.

### Archive and backfill consumers

Archive consumers care most about determinism. They will flag a packet that changes its digest or its sidecar meaning even when the pixels are the same. That makes manifest and metadata checks just as important as visual checks.

### Support replay consumers

Support replay lanes use the packet to reproduce incidents. They need the same digest, issue codes, and operator story the release team saw. If those are unstable, debugging quality drops fast.

## Routing rules

The packet should always make these groups obvious:

- lane owner group
- release owner group
- partner owner group
- support group when an incident or replay context exists

That sounds administrative, but it prevents a lot of thrash during release weeks.

## What can warn

Warnings are rare in partner lanes. They usually cover documentation-only drift or side effects that stay outside the partner contract. Missing delivery files, missing ICC data, missing required metadata, and manifest mismatch are not warnings here.

## Required note in a partial rollout

If a partner lane allows one codec family to move while another stays blocked, the packet must say:

1. which family was allowed to continue
2. why it is safe
3. which families remain blocked
4. how the partner packet reflects that split

Without that note, partial rollout is easy to misread later.
