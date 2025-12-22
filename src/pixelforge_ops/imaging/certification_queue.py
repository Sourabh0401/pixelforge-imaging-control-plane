from __future__ import annotations

"""
Prioritize imaging lane work for certification and release follow-up.

The repo already has the raw ingredients for prioritization: gate status,
partner exposure, owner groups, rollout state, and issue families. This module
turns those ingredients into a deterministic queue so the release team can see
what to touch first when multiple lanes are noisy at once.
"""

from typing import Iterable, Mapping


STATUS_WEIGHT = {"block": 100, "warn": 60, "ok": 10}
CHANNEL_WEIGHT = {"partner": 30, "pilot": 20, "internal": 10}


def queue_priority(row: Mapping[str, object]) -> int:
    status = str(row.get("status", "ok"))
    release_channel = str(row.get("release_channel", "internal"))
    partner_visible = bool(row.get("partner_visible", False))
    blocked_codecs = len(row.get("blocked_codecs", []))
    issue_count = int(row.get("issue_count", len(row.get("issues", []))) or 0)
    score = STATUS_WEIGHT.get(status, 0)
    score += CHANNEL_WEIGHT.get(release_channel, 0)
    if partner_visible:
        score += 15
    score += blocked_codecs * 5
    score += min(issue_count, 10)
    return score


def normalize_queue_row(row: Mapping[str, object]) -> dict[str, object]:
    return {
        "lane": str(row.get("lane", "unknown")),
        "status": str(row.get("status", "ok")),
        "release_channel": str(row.get("release_channel", "internal")),
        "owner_group": str(row.get("owner_group", "unknown")),
        "partner_visible": bool(row.get("partner_visible", False)),
        "blocked_codecs": sorted(str(value) for value in row.get("blocked_codecs", [])),
        "watch_codecs": sorted(str(value) for value in row.get("watch_codecs", [])),
        "issues": [str(value) for value in row.get("issues", [])],
        "issue_count": int(row.get("issue_count", len(row.get("issues", []))) or 0),
    }


def certification_queue(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    items = [normalize_queue_row(row) for row in rows]
    for item in items:
        item["priority"] = queue_priority(item)
    items.sort(
        key=lambda row: (
            -int(row["priority"]),
            str(row["release_channel"]),
            str(row["lane"]),
            str(row["owner_group"]),
        )
    )
    return items


def owner_load(queue: Iterable[Mapping[str, object]]) -> dict[str, dict[str, object]]:
    load: dict[str, dict[str, object]] = {}
    for row in certification_queue(queue):
        owner = str(row["owner_group"])
        if owner not in load:
            load[owner] = {"count": 0, "blocked": 0, "warn": 0, "lanes": []}
        load[owner]["count"] += 1
        load[owner]["blocked"] += 1 if str(row["status"]) == "block" else 0
        load[owner]["warn"] += 1 if str(row["status"]) == "warn" else 0
        load[owner]["lanes"].append(str(row["lane"]))
    for owner in load:
        load[owner]["lanes"] = sorted(load[owner]["lanes"])
    return dict(sorted(load.items()))


def queue_summary(rows: Iterable[Mapping[str, object]]) -> dict[str, object]:
    queue = certification_queue(rows)
    blocked = [row for row in queue if str(row["status"]) == "block"]
    warn = [row for row in queue if str(row["status"]) == "warn"]
    return {
        "queue": queue,
        "blocked_count": len(blocked),
        "warn_count": len(warn),
        "owner_load": owner_load(queue),
        "next_lane": queue[0]["lane"] if queue else None,
    }
