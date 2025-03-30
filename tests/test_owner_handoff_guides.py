from __future__ import annotations

import unittest

from engineering_challenge.cataloging import owner_handoff_guides


class OwnerHandoffGuideTests(unittest.TestCase):
    def test_guide_contains_questions(self) -> None:
        guide = owner_handoff_guides.guide("finance_ops")
        self.assertIn("questions", guide)

    def test_render_markdown_mentions_signals(self) -> None:
        text = owner_handoff_guides.render_markdown("support_ops")
        self.assertIn("Signals to watch", text)

    def test_digest_is_stable(self) -> None:
        self.assertEqual(
            owner_handoff_guides.guide_digest("risk_ops"),
            owner_handoff_guides.guide_digest("risk_ops"),
        )
