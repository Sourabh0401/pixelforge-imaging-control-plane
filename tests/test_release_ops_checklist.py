from __future__ import annotations

import unittest

from engineering_challenge.release_ops import checklist


class ReleaseChecklistTests(unittest.TestCase):
    def test_checklist_items_filter_by_channel(self) -> None:
        items = checklist.checklist_items("internal")
        self.assertTrue(items)

    def test_blocking_items_filter_rows(self) -> None:
        items = checklist.blocking_items("internal")
        self.assertTrue(all(item["blocking"] for item in items))

    def test_group_by_phase_returns_bucketed_rows(self) -> None:
        groups = checklist.group_by_phase("internal")
        self.assertIn("bundle", groups)

    def test_required_files_collect_unique_values(self) -> None:
        files = checklist.required_files("internal")
        self.assertIn("bundle.json", files)

    def test_evaluate_checklist_marks_missing(self) -> None:
        rows = checklist.evaluate_checklist("internal", ["bundle.json"])
        self.assertTrue(any(row["missing"] for row in rows))

    def test_channel_scope_reduces_item_count_for_partner(self) -> None:
        internal = len(checklist.checklist_items("internal"))
        partner = len(checklist.checklist_items("partner"))
        self.assertLessEqual(partner, internal)

    def test_evaluate_checklist_can_pass_when_all_files_present(self) -> None:
        files = checklist.required_files("internal")
        rows = checklist.evaluate_checklist("internal", files)
        self.assertTrue(all(row["passed"] for row in rows))

    def test_codes_are_unique(self) -> None:
        codes = [item["code"] for item in checklist.checklist_items("internal")]
        self.assertEqual(len(codes), len(set(codes)))
