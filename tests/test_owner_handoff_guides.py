from __future__ import annotations

import unittest

from pixelforge_ops.cataloging import owner_handoff_guides


class OwnerHandoffGuideTests(unittest.TestCase):
    def test_guide_contains_questions(self) -> None:
        guide = owner_handoff_guides.guide("codec_ops")
        self.assertIn("questions", guide)

    def test_render_markdown_mentions_signals(self) -> None:
        text = owner_handoff_guides.render_markdown("partner_ops")
        self.assertIn("Signals to watch", text)

    def test_digest_is_stable(self) -> None:
        self.assertEqual(
            owner_handoff_guides.guide_digest("image_quality_ops"),
            owner_handoff_guides.guide_digest("image_quality_ops"),
        )


