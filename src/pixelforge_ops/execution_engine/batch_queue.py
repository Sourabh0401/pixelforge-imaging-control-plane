from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QueueEntry:
    run_id: str
    bundle_id: str
    owner: str
    priority: int
    release_channel: str
    worker_pool: str


def entry_for(run_id: str, bundle_id: str, owner: str, release_channel: str, hidden_cases: int) -> QueueEntry:
    priority = 100 - hidden_cases
    worker_pool = "heavy" if hidden_cases >= 8 else "default"
    return QueueEntry(run_id, bundle_id, owner, priority, release_channel, worker_pool)


def sort_queue(entries: list[QueueEntry]) -> list[QueueEntry]:
    return sorted(entries, key=lambda item: (-item.priority, item.owner, item.bundle_id))


def queue_summary(entries: list[QueueEntry]) -> dict[str, object]:
    return {
        "count": len(entries),
        "worker_pools": {
            pool: sum(1 for item in entries if item.worker_pool == pool)
            for pool in sorted({item.worker_pool for item in entries})
        },
    }


def chunk_queue(entries: list[QueueEntry], size: int) -> list[list[QueueEntry]]:
    return [entries[index : index + size] for index in range(0, len(entries), size)]
