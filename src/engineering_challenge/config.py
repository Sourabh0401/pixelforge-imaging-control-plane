from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RuntimeProfile:
    name: str = "default"
    timeout_multiplier: float = 1.0
    hidden_case_multiplier: float = 1.25
    public_case_multiplier: float = 1.0
    late_result_penalty: float = 0.2
    max_bundle_cases: int = 80
    required_public_case_floor: int = 6
    required_hidden_case_floor: int = 4


@dataclass(frozen=True)
class AppPaths:
    root: Path
    fixtures: Path
    examples: Path
    docs: Path
    sqlite_path: Path = field(default_factory=lambda: Path("runtime") / "engineering_challenge.sqlite3")

    @classmethod
    def from_root(cls, root: Path) -> "AppPaths":
        return cls(
            root=root,
            fixtures=root / "tests" / "fixtures",
            examples=root / "examples",
            docs=root / "docs",
            sqlite_path=root / "runtime" / "engineering_challenge.sqlite3",
        )
