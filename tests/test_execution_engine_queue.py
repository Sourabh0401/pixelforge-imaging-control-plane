from __future__ import annotations

import unittest

from pixelforge_ops.execution_engine import batch_queue


class BatchQueueTests(unittest.TestCase):
    def test_entry_for_uses_hidden_case_count(self) -> None:
        entry = batch_queue.entry_for("run-1", "bundle", "codec_ops", "internal", 9)
        self.assertEqual(entry.worker_pool, "heavy")

    def test_sort_queue_orders_priority_descending(self) -> None:
        items = [
            batch_queue.entry_for("run-1", "bundle-a", "codec_ops", "internal", 2),
            batch_queue.entry_for("run-2", "bundle-b", "codec_ops", "internal", 8),
        ]
        ordered = batch_queue.sort_queue(items)
        self.assertGreaterEqual(ordered[0].priority, ordered[1].priority)

    def test_queue_summary_groups_worker_pools(self) -> None:
        items = [
            batch_queue.entry_for("run-1", "bundle-a", "codec_ops", "internal", 2),
            batch_queue.entry_for("run-2", "bundle-b", "codec_ops", "internal", 8),
        ]
        summary = batch_queue.queue_summary(items)
        self.assertEqual(summary["count"], 2)

    def test_chunk_queue_splits_evenly(self) -> None:
        items = [batch_queue.entry_for(f"run-{idx}", "bundle", "codec_ops", "internal", idx % 10) for idx in range(7)]
        chunks = batch_queue.chunk_queue(items, 3)
        self.assertEqual([len(chunk) for chunk in chunks], [3, 3, 1])

    def test_queue_entry_is_immutable_dataclass(self) -> None:
        entry = batch_queue.entry_for("run-1", "bundle", "codec_ops", "internal", 1)
        self.assertEqual(entry.owner, "codec_ops")


