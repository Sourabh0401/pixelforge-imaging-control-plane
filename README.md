# Engineering Challenge Control Plane

Engineering Challenge Control Plane is the internal service bundle we use to run a private engineering challenge program for hiring loops, partner certifications, and release-readiness drills. Operators load department bundles, replay participant submissions, compute weighted scorecards, gate bundle releases, persist monthly history, and export audit packets for downstream review. The repo is intentionally broad because the work itself crosses several teams: content operations, evaluation operations, support, and release management all touch the same bundle lifecycle.

The product has six connected surfaces:

- `cataloging` handles bundle import, metadata policy, case indexing, and operator playbooks.
- `execution_engine` normalizes submission payloads, applies comparator rules, budgets runtime, and records transcripts.
- `scoring_model` computes weighted section totals, fairness checks, drift analysis, and remediation queues.
- `release_ops` builds manifests, applies rollout calendars, enforces checklists, and evaluates release gates.
- `auditpack` assembles evidence contracts, traces, deterministic zip exports, and retention policy.
- `persistence` stores summaries and history in SQLite and powers owner dashboards.

Current bundle families cover systems-heavy tracks such as platform operations, routing, data cleanup, settlement controls, and release drills. The same product shape also supports department lanes for kernel, database, networking, compiler, graphics, distributed systems, data engineering, and financial engine tracks.

## Commands operators actually use

```bash
PYTHONPATH=src python -m engineering_challenge.cli catalog-summary tests/fixtures/catalog
PYTHONPATH=src python -m engineering_challenge.cli validate-bundle tests/fixtures/catalog/merchant-closeout
PYTHONPATH=src python -m engineering_challenge.cli run-attempt tests/fixtures/catalog/merchant-closeout tests/fixtures/attempts/merchant-closeout_mixed.json
PYTHONPATH=src python -m engineering_challenge.cli build-scorecard tests/fixtures/catalog/merchant-closeout tests/fixtures/attempts/merchant-closeout_mixed.json
PYTHONPATH=src python -m engineering_challenge.cli build-release tests/fixtures/catalog tests/fixtures/catalog/merchant-closeout tests/fixtures/catalog/warehouse-routing
PYTHONPATH=src python -m engineering_challenge.cli build-audit tests/fixtures/catalog/merchant-closeout tests/fixtures/attempts/merchant-closeout_mixed.json --output examples/audit_packets/manual.zip
PYTHONPATH=src python -m engineering_challenge.cli release-readiness tests/fixtures/catalog/merchant-closeout tests/fixtures/attempts/merchant-closeout_mixed.json
python -m unittest discover -s tests -q
```

## Fixture corpus

The repo includes:

- 12 bundle fixture directories with case catalogs and authoring notes
- mixed, strong, and weak submission payloads for each bundle
- monthly history JSONL corpora for replay and dashboard tests
- SQLite snapshot databases with imported history rows
- deterministic audit packet samples and scorecard exports

## Repository map

- [docs/architecture.md](docs/architecture.md)
- [docs/department-guides.md](docs/department-guides.md)
- [docs/release-process.md](docs/release-process.md)
- [docs/data-model.md](docs/data-model.md)
- [docs/operator-runbook.md](docs/operator-runbook.md)
- [docs/storage-and-retention.md](docs/storage-and-retention.md)
- [docs/troubleshooting.md](docs/troubleshooting.md)
