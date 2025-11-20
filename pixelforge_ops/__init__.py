from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC_PACKAGE = _ROOT / "src" / "pixelforge_ops"
__path__ = [str(_SRC_PACKAGE)]


