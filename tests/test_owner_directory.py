from __future__ import annotations

import unittest

from pixelforge_ops.cataloging import owner_directory


class OwnerDirectoryTests(unittest.TestCase):
    def test_owner_row_returns_contacts(self) -> None:
        row = owner_directory.owner_row("codec_ops")
        self.assertIn("contacts", row)

    def test_primary_contact_returns_email(self) -> None:
        self.assertIn("@internal.example", owner_directory.primary_contact("partner_ops"))

    def test_escalation_chain_returns_multiple_steps(self) -> None:
        chain = owner_directory.escalation_chain("archive_ops")
        self.assertGreaterEqual(len(chain), 3)

    def test_owners_by_region_filters_values(self) -> None:
        rows = owner_directory.owners_by_region("amer")
        self.assertIn("codec_ops", rows)

    def test_queue_service_level_returns_targets(self) -> None:
        sla = owner_directory.queue_service_level("queue-codec-cert-release")
        self.assertIn("target_hours", sla)

    def test_weekly_digest_roles_returns_values(self) -> None:
        self.assertTrue(owner_directory.weekly_digest_roles())

    def test_owner_row_uses_imaging_team_names(self) -> None:
        row = owner_directory.owner_row("codec_ops")
        self.assertIn("Codec", row["team_name"])

