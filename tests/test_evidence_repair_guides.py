from __future__ import annotations

import unittest

from pixelforge_ops.auditpack import evidence_repair_guides


class EvidenceRepairGuideTests(unittest.TestCase):
    def test_guide_has_owner(self) -> None:
        guide = evidence_repair_guides.guide("packet_digest")
        self.assertIn("owner", guide)

    def test_symptoms_are_available(self) -> None:
        self.assertTrue(evidence_repair_guides.symptoms("trace_rows"))

    def test_render_markdown_includes_repairs(self) -> None:
        text = evidence_repair_guides.render_markdown("release_manifest")
        self.assertIn("## Repairs", text)

    def test_digest_is_stable(self) -> None:
        self.assertEqual(
            evidence_repair_guides.guide_digest("bundle"),
            evidence_repair_guides.guide_digest("bundle"),
        )


