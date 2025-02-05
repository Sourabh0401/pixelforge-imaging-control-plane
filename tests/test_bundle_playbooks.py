from __future__ import annotations

import unittest

from engineering_challenge.cataloging import bundle_playbooks


class BundlePlaybookTests(unittest.TestCase):
    def test_playbook_exists_for_known_bundle(self) -> None:
        item = bundle_playbooks.playbook("merchant-closeout")
        self.assertIn("handoff_owner", item)

    def test_release_questions_are_present(self) -> None:
        questions = bundle_playbooks.release_questions("warehouse-routing")
        self.assertGreaterEqual(len(questions), 3)

    def test_render_markdown_mentions_escalation(self) -> None:
        text = bundle_playbooks.render_markdown("claims-intake")
        self.assertIn("Escalation order", text)

    def test_playbook_digest_is_stable(self) -> None:
        self.assertEqual(
            bundle_playbooks.playbook_digest("returns-recovery"),
            bundle_playbooks.playbook_digest("returns-recovery"),
        )
