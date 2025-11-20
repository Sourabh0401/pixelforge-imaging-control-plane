from __future__ import annotations

import unittest

from pixelforge_ops.execution_engine import comparator


class ExecutionComparatorTests(unittest.TestCase):
    def test_exact_matches_identical_objects(self) -> None:
        self.assertTrue(comparator.exact({"a": 1}, {"a": 1}))

    def test_unordered_list_ignores_order(self) -> None:
        self.assertTrue(comparator.unordered_list([3, 1, 2], [1, 2, 3]))

    def test_numeric_range_accepts_value_inside_bounds(self) -> None:
        self.assertTrue(comparator.numeric_range(7.2, {"min": 7.0, "max": 8.0}))

    def test_mapping_subset_requires_expected_pairs(self) -> None:
        self.assertTrue(comparator.mapping_subset({"a": 1, "b": 2}, {"a": 1}))

    def test_contains_tokens_checks_all_tokens(self) -> None:
        self.assertTrue(comparator.contains_tokens("alpha beta gamma", ["alpha", "gamma"]))

    def test_rounded_number_compares_with_places(self) -> None:
        self.assertTrue(comparator.rounded_number(3.14159, {"value": 3.14, "places": 2}))

    def test_ordered_pairs_requires_exact_order(self) -> None:
        self.assertFalse(comparator.ordered_pairs([[1, 2], [3, 4]], [[3, 4], [1, 2]]))

    def test_regex_groups_returns_named_group_match(self) -> None:
        self.assertTrue(comparator.regex_groups("owner=codec_ops", {"pattern": r"owner=(?P<owner>\w+)", "groups": {"owner": "codec_ops"}}))

    def test_event_log_compares_event_sequence(self) -> None:
        answer = [{"event": "start"}, {"event": "stop"}]
        self.assertTrue(comparator.event_log(answer, ["start", "stop"]))

    def test_csv_rows_compares_row_order(self) -> None:
        self.assertTrue(comparator.csv_rows([["a", "b"], ["c", "d"]], [["a", "b"], ["c", "d"]]))

    def test_artifact_manifest_checks_digest_and_files(self) -> None:
        answer = {"digest": "abc", "files": ["x", "y"]}
        self.assertTrue(comparator.artifact_manifest(answer, {"digest": "abc", "files": ["y", "x"]}))

    def test_compare_dispatches_by_name(self) -> None:
        self.assertTrue(comparator.compare("exact", 1, 1))


