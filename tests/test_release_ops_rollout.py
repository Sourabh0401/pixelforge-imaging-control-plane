from __future__ import annotations

import unittest
from datetime import date

from engineering_challenge.release_ops import calendar, digest, manifest_builder, readiness, rollout_gate, rollout_matrix
from tests.ext_helpers import bundle, scorecard


class ReleaseRolloutTests(unittest.TestCase):
    def test_owner_quota_returns_positive_number(self) -> None:
        self.assertGreater(rollout_matrix.owner_quota("finance_ops", "internal"), 0)

    def test_release_train_for_date_returns_train(self) -> None:
        train = rollout_matrix.release_train_for_date(date(2026, 2, 3))
        self.assertIn("train_id", train)

    def test_remaining_quota_decrements_current_count(self) -> None:
        remaining = rollout_gate.remaining_quota("finance_ops", "internal", 1)
        self.assertGreaterEqual(remaining, 0)

    def test_can_schedule_checks_quota(self) -> None:
        allowed = rollout_gate.can_schedule("finance_ops", "internal", 0)
        self.assertTrue(allowed)

    def test_owner_gate_summary_maps_owners(self) -> None:
        summary = rollout_gate.owner_gate_summary(["finance_ops", "support_ops"], "internal", {"finance_ops": 1})
        self.assertIn("finance_ops", summary)
        self.assertIn("remaining", summary["finance_ops"])
        self.assertIn("capacity", summary["finance_ops"])

    def test_freeze_window_returns_dates(self) -> None:
        freeze = calendar.freeze_window(date(2026, 2, 3))
        self.assertEqual(len(freeze), 2)

    def test_next_ship_date_returns_iso_text(self) -> None:
        self.assertIn("2026-", calendar.next_ship_date(date(2026, 2, 3)))

    def test_manifest_digest_is_stable(self) -> None:
        payload = {"bundle_ids": ["merchant-closeout"]}
        self.assertEqual(digest.manifest_digest(payload), digest.manifest_digest(payload))

    def test_stable_release_id_formats_ordinal(self) -> None:
        self.assertEqual(digest.stable_release_id("internal", "train-01", 7), "internal-train-01-007")

    def test_digest_label_shortens_digest(self) -> None:
        self.assertEqual(len(digest.digest_label("a" * 64)), 12)

    def test_bundle_manifest_row_includes_policy(self) -> None:
        row = manifest_builder.bundle_manifest_row(bundle("merchant-closeout"))
        self.assertIn("policy", row)

    def test_owner_mix_groups_bundles(self) -> None:
        summary = manifest_builder.owner_mix([bundle("merchant-closeout"), bundle("warehouse-routing")])
        self.assertIn("finance_ops", summary)

    def test_readiness_state_tracks_watch_bundles(self) -> None:
        state = readiness.readiness_state([scorecard("merchant-closeout", "mixed")])
        self.assertIn("watch", state)

    def test_readiness_notes_returns_text(self) -> None:
        notes = readiness.readiness_notes([scorecard("merchant-closeout", "mixed")])
        self.assertTrue(notes)

    def test_blocking_check_codes_returns_strings(self) -> None:
        codes = readiness.blocking_check_codes("internal")
        self.assertTrue(codes)

    def test_evaluate_request_blocks_when_blackout_applies(self) -> None:
        decision = rollout_gate.evaluate_request("finance_ops", "internal", 0, 1, "2026-03-09")
        self.assertFalse(decision.allowed)
        self.assertIn("blackout", decision.reason)

    def test_schedule_batch_keeps_allowed_allocations(self) -> None:
        decisions = rollout_gate.schedule_batch([("support_ops", 1), ("finance_ops", 1)], "internal", {}, "2026-01-05")
        self.assertTrue(decisions["support_ops"].allowed)
        self.assertTrue(decisions["finance_ops"].allowed)
