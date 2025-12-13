# PixelForge Imaging Control Plane

PixelForge Imaging Control Plane is the internal release and certification repo behind PixelForge image engine drops. The team uses it to manage codec and raster conformance bundles, replay nightly decode and transform runs, score filter regressions, gate release windows, persist monthly history, and freeze deterministic audit packets before a build moves into a wider channel. It sits between imaging engineering, QA, release management, partner enablement, and support, so the repo is shaped like an operations product instead of a one-shot test harness.

The product has six connected surfaces:

- `cataloging` loads certification bundles, owner metadata, workflow contracts, and lane playbooks.
- `execution_engine` normalizes replay payloads, compares outputs, budgets execution time, and records transcripts.
- `scoring_model` computes weighted section totals, drift checks, fairness signals, and remediation queues.
- `release_ops` builds manifests, applies rollout calendars, enforces checklists, and evaluates ship gates.
- `auditpack` assembles evidence contracts, traces, deterministic zip exports, and retention rules.
- `persistence` stores summaries and history in SQLite, then feeds dashboard and owner review views.

The checked-in fixture corpus still uses durable codenames such as `jpeg-codec-fidelity` and `raster-transform-tiling`. Those names predate the current PixelForge branding and now stand in for imaging certification lanes like codec fidelity, raster transforms, color management, partner export compatibility, and recovery drills. The codenames stay because they keep long-lived history snapshots stable.

The imaging layer is no longer a thin comparison wrapper. It now carries lane-aware threshold profiles, package-local operator templates, partner delivery contracts, codec rollout policy, manifest exception rules, and render-quality report builders. That matters because the release team does not only ask “did the image match?” They also ask “which lane failed, which codec family is still safe, does the packet still satisfy partner rules, and what should the next shift inspect first?”

## Commands operators actually use

```bash
PYTHONPATH=src python -m pixelforge_ops.cli catalog-summary tests/fixtures/catalog
PYTHONPATH=src python -m pixelforge_ops.cli validate-bundle tests/fixtures/catalog/jpeg-codec-fidelity
PYTHONPATH=src python -m pixelforge_ops.cli run-attempt tests/fixtures/catalog/jpeg-codec-fidelity tests/fixtures/attempts/jpeg-codec-fidelity_mixed.json
PYTHONPATH=src python -m pixelforge_ops.cli build-scorecard tests/fixtures/catalog/jpeg-codec-fidelity tests/fixtures/attempts/jpeg-codec-fidelity_mixed.json
PYTHONPATH=src python -m pixelforge_ops.cli build-release tests/fixtures/catalog tests/fixtures/catalog/jpeg-codec-fidelity tests/fixtures/catalog/raster-transform-tiling
PYTHONPATH=src python -m pixelforge_ops.cli build-audit tests/fixtures/catalog/jpeg-codec-fidelity tests/fixtures/attempts/jpeg-codec-fidelity_mixed.json --output examples/audit_packets/manual.zip
PYTHONPATH=src python -m pixelforge_ops.cli release-readiness tests/fixtures/catalog/jpeg-codec-fidelity tests/fixtures/attempts/jpeg-codec-fidelity_mixed.json
PYTHONPATH=src python -m pixelforge_ops.cli history-rollup tests/fixtures/history/ops_history_2026_01.jsonl
python -m unittest discover -s tests -q
```

## What lives here

- 12 certification bundle directories with case catalogs, owner notes, and release metadata
- mixed, strong, and weak replay payloads for each lane
- monthly history JSONL corpora for trend and dashboard tests
- SQLite snapshot databases with imported release history rows
- deterministic audit packet samples, scorecard exports, release manifests, and dashboard views
- package-local imaging reference assets for threshold profiles, partner rules, rollout policy, exception policy, and operator questionnaires
- lane-specific operator templates that render stable handoff context into quality reports and release packets

## Why the repo is bigger than a small library

PixelForge itself is the image engine. This repo is the release control plane around it. The bundle corpus, history snapshots, and audit packet fixtures are the point: they let the team replay an old release week, prove that a JPEG regression was already visible in hidden cases, compare partner lanes before and after a fix, and export the exact evidence packet that justified a rollout decision.

## Repository map

- [docs/architecture.md](docs/architecture.md)
- [docs/imaging-quality-model.md](docs/imaging-quality-model.md)
- [docs/codec-compatibility.md](docs/codec-compatibility.md)
- [docs/color-profile-policy.md](docs/color-profile-policy.md)
- [docs/render-manifest.md](docs/render-manifest.md)
- [docs/image-release-gates.md](docs/image-release-gates.md)
- [docs/department-guides.md](docs/department-guides.md)
- [docs/release-process.md](docs/release-process.md)
- [docs/data-model.md](docs/data-model.md)
- [docs/operator-runbook.md](docs/operator-runbook.md)
- [docs/storage-and-retention.md](docs/storage-and-retention.md)
- [docs/troubleshooting.md](docs/troubleshooting.md)
