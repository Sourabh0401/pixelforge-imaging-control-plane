from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from pixelforge_ops import catalog, storage
from pixelforge_ops.execution import evaluate_attempt
from pixelforge_ops.scoring import score_run
from pixelforge_ops.utils import read_json

DB = ROOT / "runtime" / "pixelforge_ops.sqlite3"
CORPUS = ROOT / "tests" / "fixtures" / "catalog"
ATTEMPTS = ROOT / "tests" / "fixtures" / "attempts"


def main() -> None:
    for bundle in catalog.load_corpus(CORPUS):
        storage.record_bundle(DB, bundle, catalog.bundle_summary(bundle))
        payload = read_json(ATTEMPTS / f"{bundle.bundle_id}_mixed.json")
        run = evaluate_attempt(bundle, payload)
        card = score_run(run, bundle)
        storage.record_run(DB, run, card)


if __name__ == "__main__":
    main()


