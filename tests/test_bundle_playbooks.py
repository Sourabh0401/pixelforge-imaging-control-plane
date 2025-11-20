from __future__ import annotations

import unittest

from pixelforge_ops.cataloging import bundle_playbooks


class BundlePlaybookTests(unittest.TestCase):
    def test_playbook_exists_for_known_bundle(self) -> None:
        item = bundle_playbooks.playbook("jpeg-codec-fidelity")
        self.assertIn("handoff_owner", item)

    def test_release_questions_are_present(self) -> None:
        questions = bundle_playbooks.release_questions("raster-transform-tiling")
        self.assertGreaterEqual(len(questions), 3)

    def test_render_markdown_mentions_escalation(self) -> None:
        text = bundle_playbooks.render_markdown("metadata-exif-ingest")
        self.assertIn("Escalation order", text)

    def test_playbook_digest_is_stable(self) -> None:
        self.assertEqual(
            bundle_playbooks.playbook_digest("decoder-recovery-replay"),
            bundle_playbooks.playbook_digest("decoder-recovery-replay"),
        )


