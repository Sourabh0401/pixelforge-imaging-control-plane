from __future__ import annotations

import unittest

from engineering_challenge.release_ops import rollout_gate


class ReleaseRolloutGateExtendedTests(unittest.TestCase):
    def test_remaining_quota_uses_internal_owner_quota(self) -> None:
        self.assertEqual(rollout_gate.remaining_quota("finance_ops", "internal", 0), 6)

    def test_remaining_quota_never_goes_negative(self) -> None:
        self.assertEqual(rollout_gate.remaining_quota("finance_ops", "internal", 99), 0)

    def test_remaining_quota_uses_partner_channel_limits(self) -> None:
        self.assertEqual(rollout_gate.remaining_quota("support_ops", "partner", 0), 1)

    def test_can_schedule_is_false_when_quota_exhausted(self) -> None:
        self.assertFalse(rollout_gate.can_schedule("support_ops", "partner", 1))

    def test_blackout_weeks_include_finance_blackout_week(self) -> None:
        self.assertIn("2026-03-09", rollout_gate.blackout_weeks("finance_ops"))

    def test_blackout_weeks_include_multiple_content_ops_entries(self) -> None:
        weeks = rollout_gate.blackout_weeks("content_ops")
        self.assertGreaterEqual(len(weeks), 2)

    def test_has_blackout_is_true_for_finance_ops_week(self) -> None:
        self.assertTrue(rollout_gate.has_blackout("finance_ops", "2026-03-09"))

    def test_has_blackout_is_false_for_support_ops_same_week(self) -> None:
        self.assertFalse(rollout_gate.has_blackout("support_ops", "2026-03-09"))

    def test_capacity_for_week_returns_expected_value(self) -> None:
        self.assertEqual(rollout_gate.capacity_for_week("finance_ops", "2026-01-05"), 4)

    def test_evaluate_request_blocks_on_blackout(self) -> None:
        decision = rollout_gate.evaluate_request("finance_ops", "internal", 0, 1, "2026-03-09")
        self.assertEqual(decision.reason, "owner blackout for week")

    def test_evaluate_request_blocks_when_quota_is_exhausted(self) -> None:
        decision = rollout_gate.evaluate_request("finance_ops", "partner", 1, 1, "2026-01-05")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "owner quota exhausted")

    def test_evaluate_request_blocks_when_weekly_capacity_is_exceeded(self) -> None:
        decision = rollout_gate.evaluate_request("finance_ops", "internal", 0, 5, "2026-01-05")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "owner weekly capacity exceeded")

    def test_evaluate_request_allows_exact_remaining_quota(self) -> None:
        decision = rollout_gate.evaluate_request("support_ops", "partner", 0, 1, "2026-01-05")
        self.assertTrue(decision.allowed)

    def test_evaluate_request_allows_exact_weekly_capacity(self) -> None:
        decision = rollout_gate.evaluate_request("finance_ops", "internal", 0, 4, "2026-01-05")
        self.assertTrue(decision.allowed)

    def test_evaluate_request_reduces_remaining_after_allocation(self) -> None:
        decision = rollout_gate.evaluate_request("support_ops", "internal", 0, 2, "2026-01-05")
        self.assertEqual(decision.remaining, 3)

    def test_owner_gate_summary_marks_blackout_state(self) -> None:
        summary = rollout_gate.owner_gate_summary(["content_ops"], "internal", {})
        self.assertTrue(summary["content_ops"]["blackout"])

    def test_owner_gate_summary_includes_capacity(self) -> None:
        summary = rollout_gate.owner_gate_summary(["support_ops"], "internal", {})
        self.assertEqual(summary["support_ops"]["capacity"], 4)

    def test_owner_gate_summary_uses_current_allocation_for_remaining(self) -> None:
        summary = rollout_gate.owner_gate_summary(["finance_ops"], "internal", {"finance_ops": 2})
        self.assertEqual(summary["finance_ops"]["remaining"], 4)

    def test_blocked_reasons_includes_quota_exhausted(self) -> None:
        reasons = rollout_gate.blocked_reasons(["support_ops"], "partner", {"support_ops": 1}, 1, "2026-01-05")
        self.assertEqual(reasons["support_ops"], "owner quota exhausted")

    def test_blocked_reasons_includes_blackout_reason(self) -> None:
        reasons = rollout_gate.blocked_reasons(["finance_ops"], "internal", {}, 1, "2026-03-09")
        self.assertEqual(reasons["finance_ops"], "owner blackout for week")

    def test_blocked_reasons_is_empty_when_owner_can_schedule(self) -> None:
        self.assertEqual(rollout_gate.blocked_reasons(["support_ops"], "internal", {}, 1, "2026-01-05"), {})

    def test_schedule_batch_updates_running_count_between_same_owner_requests(self) -> None:
        decisions = rollout_gate.schedule_batch(
            [("support_ops", 4), ("support_ops", 2)],
            "internal",
            {},
            "2026-01-05",
        )
        self.assertFalse(decisions["support_ops"].allowed)

    def test_schedule_batch_uses_existing_current_allocation(self) -> None:
        decisions = rollout_gate.schedule_batch([("support_ops", 1)], "partner", {"support_ops": 1}, "2026-01-05")
        self.assertFalse(decisions["support_ops"].allowed)

    def test_scheduleable_owners_returns_sorted_names(self) -> None:
        owners = rollout_gate.scheduleable_owners(["support_ops", "content_ops"], "internal", {}, 1, "2026-01-05")
        self.assertEqual(owners, ["support_ops"])

    def test_scheduleable_owners_skips_blackout_owner(self) -> None:
        owners = rollout_gate.scheduleable_owners(["finance_ops", "support_ops"], "internal", {}, 1, "2026-03-09")
        self.assertEqual(owners, ["support_ops"])

    def test_batch_summary_lists_requested_owners(self) -> None:
        decisions = rollout_gate.schedule_batch([("support_ops", 1), ("finance_ops", 1)], "internal", {}, "2026-03-09")
        summary = rollout_gate.batch_summary(decisions)
        self.assertEqual(summary["requested_owners"], ["finance_ops", "support_ops"])

    def test_batch_summary_lists_allowed_owners(self) -> None:
        decisions = rollout_gate.schedule_batch([("support_ops", 1), ("finance_ops", 1)], "internal", {}, "2026-03-09")
        summary = rollout_gate.batch_summary(decisions)
        self.assertEqual(summary["allowed_owners"], ["support_ops"])

    def test_batch_summary_lists_blocked_owners(self) -> None:
        decisions = rollout_gate.schedule_batch([("support_ops", 1), ("finance_ops", 1)], "internal", {}, "2026-03-09")
        summary = rollout_gate.batch_summary(decisions)
        self.assertEqual(summary["blocked_owners"], ["finance_ops"])

    def test_batch_summary_counts_granted_slots(self) -> None:
        decisions = rollout_gate.schedule_batch([("support_ops", 2), ("finance_ops", 1)], "internal", {}, "2026-03-09")
        summary = rollout_gate.batch_summary(decisions)
        self.assertEqual(summary["granted_slots"], 2)

    def test_batch_summary_sorts_blocked_reason_keys(self) -> None:
        decisions = rollout_gate.schedule_batch([("finance_ops", 1), ("content_ops", 1)], "internal", {}, "2026-03-09")
        summary = rollout_gate.batch_summary(decisions)
        self.assertEqual(list(summary["blocked_reasons"]), sorted(summary["blocked_reasons"]))

    def test_release_window_status_returns_ready_owners(self) -> None:
        status = rollout_gate.release_window_status(["finance_ops", "support_ops"], "internal", {}, "2026-03-09")
        self.assertEqual(status["ready_owners"], ["support_ops"])

    def test_release_window_status_returns_blocked_reasons(self) -> None:
        status = rollout_gate.release_window_status(["finance_ops"], "internal", {}, "2026-03-09")
        self.assertEqual(status["blocked_reasons"]["finance_ops"], "owner blackout for week")

    def test_release_window_status_preserves_channel(self) -> None:
        status = rollout_gate.release_window_status(["support_ops"], "pilot", {}, "2026-01-05")
        self.assertEqual(status["channel"], "pilot")

    def test_release_window_status_includes_summary(self) -> None:
        status = rollout_gate.release_window_status(["support_ops"], "internal", {}, "2026-01-05")
        self.assertIn("support_ops", status["summary"])

    def test_render_gate_notes_for_allowed_request(self) -> None:
        decision = rollout_gate.evaluate_request("support_ops", "internal", 0, 1, "2026-01-05")
        self.assertIn("can schedule", rollout_gate.render_gate_notes(decision))

    def test_render_gate_notes_for_blocked_request(self) -> None:
        decision = rollout_gate.evaluate_request("finance_ops", "internal", 0, 1, "2026-03-09")
        self.assertIn("cannot schedule", rollout_gate.render_gate_notes(decision))
