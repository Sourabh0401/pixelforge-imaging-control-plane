# Imaging baselines

Baselines tell the control plane what ?normal? looked like before the current run. They are not release approvals by themselves. They are context.

## What belongs in a baseline

A good baseline records the accepted packet digest, the lane name, comparator summaries, and enough metadata to recreate why the packet was accepted. The repo should never treat a pile of raw images without lane context as a baseline.

## When to refresh a baseline

Refresh after an accepted release that intentionally changed the lane contract, codec family mix, or required regions. Do not refresh a baseline by averaging a failing run into history just to make the graph look calmer.

## What operators compare

- histogram envelope
- weighted color delta
- required-region outcomes
- manifest digest
- codec-family health
- packet routing state

## Warning versus blocker

A baseline drift can warn without blocking when the explicit lane thresholds still pass. A baseline alone should not override a hard blocker from manifest, metadata, tile coverage, or partner export.
