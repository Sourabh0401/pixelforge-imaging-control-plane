from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from engineering_challenge import audit, catalog, reporting
from engineering_challenge.execution import evaluate_attempt
from engineering_challenge.release import build_release_manifest, manifest_to_dict
from engineering_challenge.scoring import portfolio_rollup, score_run, scorecard_to_dict
from engineering_challenge.utils import read_json, write_json

FIXTURES = ROOT / "tests" / "fixtures"
EXAMPLES = ROOT / "examples"


def main() -> None:
    corpus_root = FIXTURES / "catalog"
    bundles = catalog.load_corpus(corpus_root)
    manifest = build_release_manifest("release-example", bundles, notes=["example export"])
    write_json(EXAMPLES / "release_manifest.json", manifest_to_dict(manifest))
    cards = []
    for bundle in bundles[:6]:
        attempt_path = FIXTURES / "attempts" / f"{bundle.bundle_id}_mixed.json"
        payload = read_json(attempt_path)
        run = evaluate_attempt(bundle, payload)
        card = score_run(run, bundle)
        cards.append(card)
        write_json(EXAMPLES / "scorecards" / f"{bundle.bundle_id}.json", scorecard_to_dict(card))
        packet = audit.build_audit_packet(bundle, run, card, manifest)
        audit.write_audit_zip(EXAMPLES / "audit_packets" / f"{bundle.bundle_id}.zip", packet)
        (EXAMPLES / "markdown").mkdir(parents=True, exist_ok=True)
        (EXAMPLES / "markdown" / f"{bundle.bundle_id}.md").write_text(
            reporting.scorecard_markdown(card), encoding="utf-8", newline="\n"
        )
    write_json(EXAMPLES / "portfolio_rollup.json", portfolio_rollup(cards))


if __name__ == "__main__":
    main()
