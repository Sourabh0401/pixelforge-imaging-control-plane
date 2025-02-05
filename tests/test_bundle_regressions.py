from __future__ import annotations

import unittest

from engineering_challenge.execution import evaluate_attempt
from engineering_challenge.scoring import score_run
from tests.ext_helpers import attempt, bundle


BUNDLES = {
    "merchant-closeout": {"owner": "finance_ops", "tag": "finance", "phrase": "Closeout"},
    "warehouse-routing": {"owner": "logistics_ops", "tag": "logistics", "phrase": "Warehouse"},
    "claims-intake": {"owner": "support_ops", "tag": "support", "phrase": "Claims"},
    "reserve-rollforward": {"owner": "treasury_ops", "tag": "treasury", "phrase": "Reserve"},
    "identity-refresh": {"owner": "risk_ops", "tag": "risk", "phrase": "Identity"},
    "subscriber-billing": {"owner": "revops", "tag": "revops", "phrase": "Recurring"},
    "seat-allocation": {"owner": "education_ops", "tag": "education", "phrase": "Seat"},
    "fulfillment-ledger": {"owner": "platform_ops", "tag": "platform", "phrase": "Fulfillment"},
    "document-classifier": {"owner": "content_ops", "tag": "content", "phrase": "Document"},
    "vendor-settlement": {"owner": "procurement_ops", "tag": "procurement", "phrase": "Vendor"},
    "pricing-handoff": {"owner": "sales_ops", "tag": "sales", "phrase": "Pricing"},
    "returns-recovery": {"owner": "returns_ops", "tag": "returns", "phrase": "Recovery"},
}


class BundleRegressionTests(unittest.TestCase):
    def test_bundles_load_expected_metadata(self) -> None:
        for name, expected in BUNDLES.items():
            with self.subTest(bundle=name):
                item = bundle(name)
                self.assertEqual(item.bundle_id, name)
                self.assertEqual(item.owner, expected["owner"])
                self.assertIn(expected["tag"], item.tags)
                self.assertIn("release", item.tags)
                self.assertEqual(item.metadata["release_channel"], "internal")
                self.assertIn(expected["phrase"].lower(), item.title.lower())

    def test_bundles_have_hidden_and_public_cases(self) -> None:
        for name in BUNDLES:
            with self.subTest(bundle=name):
                item = bundle(name)
                self.assertTrue(item.hidden_cases())
                self.assertTrue(item.public_cases())
                self.assertGreaterEqual(len(item.sections()), 4)

    def test_strong_profiles_outperform_weak_profiles(self) -> None:
        for name in BUNDLES:
            with self.subTest(bundle=name):
                item = bundle(name)
                strong = score_run(evaluate_attempt(item, attempt(name, "strong")), item)
                weak = score_run(evaluate_attempt(item, attempt(name, "weak")), item)
                self.assertGreater(strong.percent, weak.percent)
                self.assertGreater(strong.hidden_percent, weak.hidden_percent)
                self.assertGreaterEqual(strong.percent, 88.0)

    def test_mixed_profiles_stay_blocked_for_operator_review(self) -> None:
        for name in BUNDLES:
            with self.subTest(bundle=name):
                item = bundle(name)
                mixed = score_run(evaluate_attempt(item, attempt(name, "mixed")), item)
                self.assertEqual(mixed.band, "blocked")
                self.assertIn("requires-review", mixed.policy_flags)
                self.assertGreater(mixed.public_percent, mixed.hidden_percent)

    def test_merchant_closeout_keeps_audit_section_visible(self) -> None:
        item = bundle("merchant-closeout")
        self.assertIn("audit", item.sections())
        self.assertIn("exception handling", item.metadata["notes"].lower())

    def test_warehouse_routing_mentions_repair_in_operator_notes(self) -> None:
        item = bundle("warehouse-routing")
        self.assertIn("repair", item.metadata["notes"].lower())
        self.assertIn("logistics", item.domain)

    def test_claims_intake_preserves_escalation_language(self) -> None:
        item = bundle("claims-intake")
        self.assertIn("escalation", item.metadata["notes"].lower())
        self.assertEqual(item.domain, "support_ops")

    def test_returns_recovery_uses_treasury_owner(self) -> None:
        item = bundle("returns-recovery")
        card = score_run(evaluate_attempt(item, attempt("returns-recovery", "mixed")), item)
        self.assertEqual(card.owner, "returns_ops")
        self.assertGreater(card.percent, 40.0)
