from __future__ import annotations

LEGEND_ROWS = [
    {"token": "ready", "label": "Ready", "description": "The bundle can move through the train without added release notes."},
    {"token": "watch", "label": "Watch", "description": "The bundle can move, but the owner owes explicit notes and a close follow-up."},
    {"token": "risk", "label": "Risk", "description": "The bundle needs remediation work before it should be treated as stable release material."},
    {"token": "blocked", "label": "Blocked", "description": "The bundle stops release movement until the underlying issue is resolved."},
    {"token": "public-hidden-gap", "label": "Public Hidden Gap", "description": "Public and hidden results drifted far enough apart to deserve a manual read."},
    {"token": "hidden-case-regression", "label": "Hidden Regression", "description": "Hidden cases got worse beyond the allowed buffer."},
    {"token": "requires-review", "label": "Requires Review", "description": "A policy gate asked for human review before handoff."},
    {"token": "section-spread", "label": "Section Spread", "description": "Section scores are uneven enough to suggest local overfitting or brittle authoring."},
    {"token": "digest-drift", "label": "Digest Drift", "description": "Release or audit digests changed when the bundle inputs looked unchanged."},
]


def legend() -> list[dict[str, str]]:
    return [dict(row) for row in LEGEND_ROWS]


def description(token: str) -> str:
    for row in LEGEND_ROWS:
        if row["token"] == token:
            return row["description"]
    raise KeyError(token)


def label(token: str) -> str:
    for row in LEGEND_ROWS:
        if row["token"] == token:
            return row["label"]
    raise KeyError(token)


def tokens() -> tuple[str, ...]:
    return tuple(row["token"] for row in LEGEND_ROWS)
