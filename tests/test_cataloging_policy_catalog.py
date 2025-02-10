from __future__ import annotations

import unittest

from engineering_challenge.cataloging import policy_catalog


class CatalogPolicyCatalogTests(unittest.TestCase):
    def test_domain_policy_contains_required_metadata(self) -> None:
        policy = policy_catalog.domain_policy("finance_ops")
        self.assertIn("release_channel", policy["required_metadata"])

    def test_release_channel_policy_accepts_internal(self) -> None:
        self.assertTrue(policy_catalog.release_channel_policy("finance_ops", "internal"))

    def test_release_channel_policy_rejects_unknown_channel(self) -> None:
        self.assertFalse(policy_catalog.release_channel_policy("finance_ops", "shadow"))

    def test_canonical_tags_normalize_known_values(self) -> None:
        tags = policy_catalog.canonical_tags(["ops", "hidden", "authoring"])
        self.assertIn("operations", tags)
        self.assertIn("hidden-cases", tags)

    def test_required_metadata_fields_are_stable(self) -> None:
        fields = policy_catalog.required_metadata_fields("support_ops")
        self.assertEqual(fields[0], "release_channel")

    def test_section_weight_returns_float(self) -> None:
        weight = policy_catalog.section_weight("finance_ops", "catalog")
        self.assertIsInstance(weight, float)

    def test_review_path_returns_two_reviewers(self) -> None:
        reviewers = policy_catalog.review_path("audit")
        self.assertGreaterEqual(len(reviewers), 2)

    def test_comparator_support_lookup(self) -> None:
        self.assertTrue(policy_catalog.comparator_supports_partial_credit("exact"))

    def test_bundle_envelope_includes_thresholds(self) -> None:
        envelope = policy_catalog.bundle_envelope("risk_ops")
        self.assertIn("risk_thresholds", envelope)

    def test_comparator_contract_exposes_runtime_bucket(self) -> None:
        contract = policy_catalog.comparator_policy("csv_rows")
        self.assertIn("runtime_bucket", contract)
