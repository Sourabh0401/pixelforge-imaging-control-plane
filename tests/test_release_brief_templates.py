from __future__ import annotations

import unittest

from engineering_challenge.reporting_surfaces import release_brief_templates


class ReleaseBriefTemplateTests(unittest.TestCase):
    def test_owner_list_contains_finance(self) -> None:
        self.assertIn("finance_ops", release_brief_templates.owners())

    def test_brief_for_owner_has_prompts(self) -> None:
        template = release_brief_templates.brief_for_owner("support_ops")
        self.assertIn("prompts", template)

    def test_metric_callouts_return_rows(self) -> None:
        self.assertTrue(release_brief_templates.metric_callouts("risk_ops"))

    def test_render_brief_includes_heading(self) -> None:
        text = release_brief_templates.render_brief("treasury_ops", "Treasury review", ["Hidden score fell by 6 points"])
        self.assertIn("# Treasury review", text)

    def test_brief_digest_is_stable(self) -> None:
        self.assertEqual(
            release_brief_templates.brief_digest("sales_ops"),
            release_brief_templates.brief_digest("sales_ops"),
        )
