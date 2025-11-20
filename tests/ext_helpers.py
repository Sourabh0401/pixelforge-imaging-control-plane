from __future__ import annotations

import json
from pathlib import Path

from pixelforge_ops import catalog
from pixelforge_ops.execution import evaluate_attempt
from pixelforge_ops.scoring import score_run

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"


def bundle(name: str):
    return catalog.load_bundle(FIXTURES / "catalog" / name)


def attempt(name: str, mode: str = "mixed") -> dict[str, object]:
    return json.loads((FIXTURES / "attempts" / f"{name}_{mode}.json").read_text(encoding="utf-8"))


def scorecard(name: str, mode: str = "mixed"):
    item = bundle(name)
    return score_run(evaluate_attempt(item, attempt(name, mode)), item)


def history_rows(month: int) -> list[dict[str, object]]:
    path = FIXTURES / "history" / f"ops_history_2026_{month:02d}.jsonl"
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if text:
            rows.append(json.loads(text))
    return rows


