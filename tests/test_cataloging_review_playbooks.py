from __future__ import annotations

import unittest

from engineering_challenge.cataloging import review_playbooks


class ReviewPlaybookTests(unittest.TestCase):
    def test_steps_for_section_returns_rows(self) -> None:
        rows = review_playbooks.steps_for_section("catalog")
        self.assertEqual(len(rows), 8)

    def test_blocking_steps_filter_rows(self) -> None:
        rows = review_playbooks.blocking_steps("audit")
        self.assertTrue(all(row["blocking"] for row in rows))

    def test_steps_for_owner_returns_cross_section_rows(self) -> None:
        rows = review_playbooks.steps_for_owner("finance_ops")
        self.assertTrue(rows)

    def test_step_codes_are_stable(self) -> None:
        codes = review_playbooks.step_codes("validation")
        self.assertEqual(len(codes), 8)

    def test_playbook_summary_counts_blocking_steps(self) -> None:
        summary = review_playbooks.playbook_summary("execution")
        self.assertGreater(summary["blocking_count"], 0)

    def test_owner_handoff_notes_render_strings(self) -> None:
        notes = review_playbooks.owner_handoff_notes("support_ops")
        self.assertTrue(all(isinstance(note, str) for note in notes))

    def test_unknown_section_returns_empty_list(self) -> None:
        self.assertEqual(review_playbooks.steps_for_section("missing"), [])

    def test_summary_owner_list_is_sorted(self) -> None:
        owners = review_playbooks.playbook_summary("catalog")["owners"]
        self.assertEqual(owners, sorted(owners))
