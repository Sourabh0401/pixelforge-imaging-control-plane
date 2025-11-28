from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping


def lane_dashboard_summary(rows: Iterable[Mapping[str, object]]) -> dict[str, object]:
    lane_status: dict[str, dict[str, int]] = defaultdict(lambda: {"ok": 0, "warn": 0, "block": 0})
    owner_status: dict[str, dict[str, int]] = defaultdict(lambda: {"ok": 0, "warn": 0, "block": 0})
    for row in rows:
        lane = str(row.get("lane", "unknown"))
        owner = str(row.get("owner", "unknown"))
        status = str(row.get("status", "ok"))
        lane_status[lane][status] = lane_status[lane].get(status, 0) + 1
        owner_status[owner][status] = owner_status[owner].get(status, 0) + 1
    return {
        "lane_summary": {lane: dict(sorted(statuses.items())) for lane, statuses in sorted(lane_status.items())},
        "owner_summary": {owner: dict(sorted(statuses.items())) for owner, statuses in sorted(owner_status.items())},
        "row_count": sum(sum(statuses.values()) for statuses in lane_status.values()),
    }

