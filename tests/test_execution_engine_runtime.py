from __future__ import annotations

import unittest

from engineering_challenge.execution_engine import runtime_budget


class RuntimeBudgetTests(unittest.TestCase):
    def test_budget_for_hidden_case_expands_ceiling(self) -> None:
        budget = runtime_budget.budget_for("case-1", 1000, True, "exact")
        self.assertGreater(budget.ceiling_ms, 1000)

    def test_budget_for_manifest_case_adds_cost(self) -> None:
        budget = runtime_budget.budget_for("case-1", 1000, False, "artifact_manifest")
        self.assertGreaterEqual(budget.ceiling_ms, 1200)

    def test_classify_runtime_marks_timeout(self) -> None:
        budget = runtime_budget.budget_for("case-1", 1000, False, "exact")
        self.assertEqual(runtime_budget.classify_runtime(budget.ceiling_ms + 1, budget), "timeout")

    def test_classify_runtime_marks_late(self) -> None:
        budget = runtime_budget.budget_for("case-1", 1000, False, "exact")
        self.assertEqual(runtime_budget.classify_runtime(budget.late_threshold_ms + 1, budget), "late")

    def test_classify_runtime_marks_on_time(self) -> None:
        budget = runtime_budget.budget_for("case-1", 1000, False, "exact")
        self.assertEqual(runtime_budget.classify_runtime(100, budget), "on-time")

    def test_queue_weight_marks_long_items(self) -> None:
        budget = runtime_budget.RuntimeBudget("case-1", 1000, 1600, 1200, "long")
        self.assertEqual(runtime_budget.queue_weight(budget), 3)

    def test_aggregate_runtime_sums_budgets(self) -> None:
        items = [runtime_budget.budget_for("case-1", 1000, False, "exact"), runtime_budget.budget_for("case-2", 900, True, "range")]
        summary = runtime_budget.aggregate_runtime(items)
        self.assertEqual(summary["case_count"], 2)

    def test_queue_bucket_short_for_small_ceiling(self) -> None:
        budget = runtime_budget.budget_for("case-1", 600, False, "exact")
        self.assertEqual(budget.queue_bucket, "short")
