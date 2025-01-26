from __future__ import annotations

import json
from pathlib import Path

from engineering_challenge import catalog


ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"


def bundle(name: str):
    return catalog.load_bundle(FIXTURES / "catalog" / name)


def attempt(name: str, mode: str = "mixed") -> dict[str, object]:
    return json.loads((FIXTURES / "attempts" / f"{name}_{mode}.json").read_text(encoding="utf-8"))
