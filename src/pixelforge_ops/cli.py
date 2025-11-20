
from __future__ import annotations

import argparse
from pathlib import Path

from . import audit, catalog, storage, validator
from .execution import evaluate_attempt, run_to_dict
from .persistence import dashboard as persistence_dashboard, history_ingest, query_service, snapshots
from .release import build_release_manifest, manifest_to_dict
from .release_ops import readiness as release_readiness
from .reporting_surfaces import owner_dashboard as owner_dashboard_surface
from .scoring import score_run, scorecard_to_dict
from .utils import read_json, stable_json


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pixelforge-ops")
    sub = parser.add_subparsers(dest="command", required=True)

    summary = sub.add_parser("catalog-summary")
    summary.add_argument("root")

    validate_bundle = sub.add_parser("validate-bundle")
    validate_bundle.add_argument("bundle")

    run_attempt = sub.add_parser("run-attempt")
    run_attempt.add_argument("bundle")
    run_attempt.add_argument("attempt")
    run_attempt.add_argument("--output")

    build_scorecard = sub.add_parser("build-scorecard")
    build_scorecard.add_argument("bundle")
    build_scorecard.add_argument("attempt")

    build_release = sub.add_parser("build-release")
    build_release.add_argument("root")
    build_release.add_argument("bundles", nargs="+")
    build_release.add_argument("--release-id", default="release-local")

    build_audit = sub.add_parser("build-audit")
    build_audit.add_argument("bundle")
    build_audit.add_argument("attempt")
    build_audit.add_argument("--release-id", default="release-local")
    build_audit.add_argument("--output")

    owner_dash = sub.add_parser("owner-dashboard")
    owner_dash.add_argument("db_path")
    owner_dash.add_argument("owner")

    history_roll = sub.add_parser("history-rollup")
    history_roll.add_argument("history_jsonl")

    snapshot = sub.add_parser("snapshot-summary")
    snapshot.add_argument("sqlite_path")

    release_state = sub.add_parser("release-readiness")
    release_state.add_argument("bundle")
    release_state.add_argument("attempt")

    sync_sqlite = sub.add_parser("sync-sqlite")
    sync_sqlite.add_argument("db_path")
    sync_sqlite.add_argument("bundle")
    sync_sqlite.add_argument("attempt")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "catalog-summary":
        print(stable_json(catalog.corpus_summary(Path(args.root))), end="")
        return 0
    if args.command == "validate-bundle":
        bundle = catalog.load_bundle(Path(args.bundle))
        issues = [issue.__dict__ for issue in validator.validate_bundle(bundle)]
        print(stable_json({"bundle_id": bundle.bundle_id, "issues": issues}), end="")
        return 0
    if args.command == "run-attempt":
        bundle = catalog.load_bundle(Path(args.bundle))
        payload = read_json(Path(args.attempt))
        run = evaluate_attempt(bundle, payload)
        output = run_to_dict(run)
        if args.output:
            Path(args.output).write_text(stable_json(output), encoding="utf-8", newline="\n")
        print(stable_json(output), end="")
        return 0
    if args.command == "build-scorecard":
        bundle = catalog.load_bundle(Path(args.bundle))
        payload = read_json(Path(args.attempt))
        run = evaluate_attempt(bundle, payload)
        card = score_run(run, bundle)
        print(stable_json(scorecard_to_dict(card)), end="")
        return 0
    if args.command == "build-release":
        root = Path(args.root)
        bundles = [catalog.load_bundle(root / bundle_name if not Path(bundle_name).exists() else Path(bundle_name)) for bundle_name in args.bundles]
        manifest = build_release_manifest(args.release_id, bundles)
        print(stable_json(manifest_to_dict(manifest)), end="")
        return 0
    if args.command == "build-audit":
        bundle = catalog.load_bundle(Path(args.bundle))
        payload = read_json(Path(args.attempt))
        run = evaluate_attempt(bundle, payload)
        card = score_run(run, bundle)
        manifest = build_release_manifest(args.release_id, [bundle])
        packet = audit.build_audit_packet(bundle, run, card, manifest)
        if args.output:
            audit.write_audit_zip(Path(args.output), packet)
        print(stable_json(packet), end="")
        return 0
    if args.command == "owner-dashboard":
        payload = persistence_dashboard.dashboard_payload(Path(args.db_path))
        print(stable_json(owner_dashboard_surface.owner_dashboard(args.owner, payload)), end="")
        return 0
    if args.command == "history-rollup":
        payload = history_ingest.monthly_rollup(history_ingest.load_rows(Path(args.history_jsonl)))
        print(stable_json(payload), end="")
        return 0
    if args.command == "snapshot-summary":
        path = Path(args.sqlite_path)
        payload = {
            "tables": snapshots.snapshot_tables(path),
            "history_row_count": snapshots.history_row_count(path),
            "owner_mix": snapshots.owner_mix(path),
            "band_counts": query_service.band_counts(path),
        }
        print(stable_json(payload), end="")
        return 0
    if args.command == "release-readiness":
        bundle = catalog.load_bundle(Path(args.bundle))
        payload = read_json(Path(args.attempt))
        run = evaluate_attempt(bundle, payload)
        card = score_run(run, bundle)
        print(stable_json(release_readiness.readiness_state([card])), end="")
        return 0
    if args.command == "sync-sqlite":
        db_path = Path(args.db_path)
        bundle = catalog.load_bundle(Path(args.bundle))
        payload = read_json(Path(args.attempt))
        run = evaluate_attempt(bundle, payload)
        card = score_run(run, bundle)
        storage.record_bundle(db_path, bundle, catalog.bundle_summary(bundle))
        storage.record_run(db_path, run, card)
        print(stable_json({"recent_runs": storage.recent_runs(db_path), "owners": storage.owner_rollup(db_path)}), end="")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

