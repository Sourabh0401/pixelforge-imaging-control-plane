from __future__ import annotations

import unittest

from pixelforge_ops.reporting_surfaces import release_brief_templates


class ReleaseBriefTemplateTests(unittest.TestCase):
    def test_owner_list_contains_finance(self) -> None:
        self.assertIn("codec_ops", release_brief_templates.owners())

    def test_brief_for_owner_has_prompts(self) -> None:
        template = release_brief_templates.brief_for_owner("partner_ops")
        self.assertIn("prompts", template)

    def test_metric_callouts_return_rows(self) -> None:
        self.assertTrue(release_brief_templates.metric_callouts("image_quality_ops"))

    def test_render_brief_includes_heading(self) -> None:
        text = release_brief_templates.render_brief("archive_ops", "Treasury review", ["Hidden score fell by 6 points"])
        self.assertIn("# Treasury review", text)

    def test_brief_digest_is_stable(self) -> None:
        self.assertEqual(
            release_brief_templates.brief_digest("launch_ops"),
            release_brief_templates.brief_digest("launch_ops"),
        )


