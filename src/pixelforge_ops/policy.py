from __future__ import annotations

from dataclasses import dataclass


DIFFICULTY_WEIGHTS = {
    "intro": 1.0,
    "core": 1.35,
    "advanced": 1.8,
    "edge": 2.2,
}

BAND_THRESHOLDS = [
    ("ready", 88.0),
    ("watch", 70.0),
    ("risk", 52.0),
    ("blocked", 0.0),
]


@dataclass(frozen=True)
class PolicyCheck:
    name: str
    message: str


def difficulty_weight(name: str) -> float:
    return DIFFICULTY_WEIGHTS.get(name, 1.0)


def band_for_percent(percent: float) -> str:
    for band, floor in BAND_THRESHOLDS:
        if percent >= floor:
            return band
    return "blocked"


def remediation_flags(public_percent: float, hidden_percent: float, percent: float) -> tuple[str, ...]:
    flags: list[str] = []
    if public_percent >= 90 and hidden_percent < 70:
        flags.append("hidden-case-regression")
    if percent < 60:
        flags.append("requires-review")
    if public_percent - hidden_percent >= 25:
        flags.append("public-hidden-gap")
    return tuple(flags)
