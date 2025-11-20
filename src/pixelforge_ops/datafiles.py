from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any

from .utils import read_json


DATA_ROOT = Path(__file__).resolve().parents[2] / "data"


@lru_cache(maxsize=None)
def load_json_data(*parts: str) -> Any:
    path = DATA_ROOT.joinpath(*parts)
    return read_json(path)


def clone_data(value: Any) -> Any:
    return deepcopy(value)
