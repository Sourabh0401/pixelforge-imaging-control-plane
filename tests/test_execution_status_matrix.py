from __future__ import annotations

import unittest

from engineering_challenge.execution_engine import status_matrix


class ExecutionStatusMatrixTests(unittest.TestCase):
    def test_status_definition_for_pass(self) -> None:
        row = status_matrix.status_definition("pass")
        self.assertEqual(row["status"], "pass")

    def test_counts_toward_score_true_for_pass(self) -> None:
        self.assertTrue(status_matrix.counts_toward_score("pass"))

    def test_counts_toward_score_false_for_timeout(self) -> None:
        self.assertFalse(status_matrix.counts_toward_score("timeout"))

    def test_operator_action_returns_string(self) -> None:
        self.assertTrue(status_matrix.operator_action("error"))
