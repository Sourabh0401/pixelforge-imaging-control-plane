from __future__ import annotations

import unittest

from engineering_challenge.cataloging import metadata_contracts, release_profiles


class CatalogMetadataProfilesTests(unittest.TestCase):
    def test_required_fields_include_release_channel(self) -> None:
        self.assertIn("meta_field_01", metadata_contracts.required_fields("internal"))

    def test_fields_for_section_returns_values(self) -> None:
        self.assertTrue(metadata_contracts.fields_for_section("catalog"))

    def test_contact_for_owner_returns_email(self) -> None:
        contact = metadata_contracts.contact_for_owner("finance_ops")
        self.assertIn("@internal.example", contact["email"])

    def test_profile_for_bundle_returns_bundle_id(self) -> None:
        profile = release_profiles.profile_for_bundle("merchant-closeout")
        self.assertEqual(profile["bundle_id"], "merchant-closeout")

    def test_channels_for_bundle_returns_channel_list(self) -> None:
        channels = release_profiles.channels_for_bundle("merchant-closeout")
        self.assertIn("internal", channels)

    def test_score_floor_is_positive(self) -> None:
        self.assertGreater(release_profiles.score_floor("merchant-closeout"), 0)
