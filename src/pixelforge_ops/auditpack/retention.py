from __future__ import annotations


RETENTION_DAYS = {
    "internal": 45,
    "rehearsal": 30,
    "pilot": 90,
    "partner": 180,
    "ops-only": 21,
}


def retention_days(channel: str) -> int:
    return RETENTION_DAYS[channel]


def should_prune(channel: str, age_days: int, has_export: bool) -> bool:
    if not has_export:
        return False
    return age_days > retention_days(channel)
