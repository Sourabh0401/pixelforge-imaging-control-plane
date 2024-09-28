from __future__ import annotations

from engineering_challenge.persistence.query_service import band_counts, owner_average


def dashboard_payload(path) -> dict[str, object]:
    return {
        "bands": band_counts(path),
        "owner_average": owner_average(path),
    }


def at_risk_owners(path, floor: float = 70.0) -> list[str]:
    averages = owner_average(path)
    return [owner for owner, value in averages.items() if value < floor]
