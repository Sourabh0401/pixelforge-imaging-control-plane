from __future__ import annotations

import unittest

from pixelforge_ops.imaging import issue_codes, taxonomy_entry
from pixelforge_ops.imaging.reference_data import (
    load_reference_data,
    reference_digest,
    reference_names,
    reference_summary,
    validate_codec_rollout_policies,
    validate_issue_taxonomy,
    validate_manifest_exception_policies,
    validate_partner_delivery_profiles,
    validate_release_questionnaires,
    validate_threshold_profiles,
)


class ImagingReferenceAssetsTests(unittest.TestCase):
    def test_reference_names_include_imaging_policy_assets(self) -> None:
        self.assertIn("lane_threshold_profiles.json", reference_names())
        self.assertIn("issue_taxonomy.json", reference_names())

    def test_reference_digest_is_stable(self) -> None:
        self.assertEqual(reference_digest("issue_taxonomy.json"), reference_digest("issue_taxonomy.json"))

    def test_reference_summary_lists_every_asset(self) -> None:
        summary = reference_summary()
        self.assertEqual(summary["count"], len(reference_names()))

    def test_threshold_profiles_validate(self) -> None:
        validate_threshold_profiles(load_reference_data("lane_threshold_profiles.json"))

    def test_issue_taxonomy_validate(self) -> None:
        validate_issue_taxonomy(load_reference_data("issue_taxonomy.json"))

    def test_partner_delivery_profiles_validate(self) -> None:
        validate_partner_delivery_profiles(load_reference_data("partner_delivery_profiles.json"))

    def test_codec_rollout_policies_validate(self) -> None:
        validate_codec_rollout_policies(load_reference_data("codec_rollout_policies.json"))

    def test_manifest_exception_policies_validate(self) -> None:
        validate_manifest_exception_policies(load_reference_data("manifest_exception_policies.json"))

    def test_release_questionnaires_validate(self) -> None:
        validate_release_questionnaires(load_reference_data("release_questionnaires.json"))

    def test_issue_codes_expose_manifest_and_partner_entries(self) -> None:
        self.assertIn("render-manifest", issue_codes())
        self.assertIn("partner-export", issue_codes())

    def test_taxonomy_entry_carries_owner_group(self) -> None:
        entry = taxonomy_entry("codec-profile")
        self.assertEqual(entry["owner_group"], "codec-ops")

