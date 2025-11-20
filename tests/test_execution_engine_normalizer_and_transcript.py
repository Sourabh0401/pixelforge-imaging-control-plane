from __future__ import annotations

import unittest

from pixelforge_ops.execution_engine import result_normalizer, transcript
from tests.ext_helpers import attempt, bundle
from pixelforge_ops.execution import evaluate_attempt


class NormalizerTranscriptTests(unittest.TestCase):
    def test_normalize_answer_trims_strings(self) -> None:
        self.assertEqual(result_normalizer.normalize_answer("  hello "), "hello")

    def test_normalize_answer_sorts_mapping_keys(self) -> None:
        normalized = result_normalizer.normalize_answer({"b": 2, "a": 1})
        self.assertEqual(list(normalized.keys()), ["a", "b"])

    def test_normalize_status_prefers_timeout(self) -> None:
        self.assertEqual(result_normalizer.normalize_status("pass", has_error=False, timed_out=True), "timeout")

    def test_normalize_status_prefers_error(self) -> None:
        self.assertEqual(result_normalizer.normalize_status("pass", has_error=True, timed_out=False), "error")

    def test_normalize_message_for_fail(self) -> None:
        self.assertEqual(result_normalizer.normalize_message("fail", None), "output mismatch")

    def test_partition_results_splits_hidden_and_public(self) -> None:
        items = [{"hidden": True, "status": "pass"}, {"hidden": False, "status": "fail"}]
        parts = result_normalizer.partition_results(items)
        self.assertEqual(len(parts["hidden"]), 1)

    def test_status_counts_groups_values(self) -> None:
        counts = result_normalizer.status_counts([{"status": "pass"}, {"status": "pass"}, {"status": "fail"}])
        self.assertEqual(counts["pass"], 2)

    def test_run_transcript_matches_case_count(self) -> None:
        run = evaluate_attempt(bundle("jpeg-codec-fidelity"), attempt("jpeg-codec-fidelity", "mixed"))
        rows = transcript.run_transcript(run)
        self.assertEqual(len(rows), len(run.case_results))

    def test_status_timeline_renders_strings(self) -> None:
        run = evaluate_attempt(bundle("jpeg-codec-fidelity"), attempt("jpeg-codec-fidelity", "mixed"))
        self.assertTrue(transcript.status_timeline(run))

    def test_slowest_cases_limit(self) -> None:
        run = evaluate_attempt(bundle("jpeg-codec-fidelity"), attempt("jpeg-codec-fidelity", "mixed"))
        rows = transcript.slowest_cases(run, limit=3)
        self.assertEqual(len(rows), 3)

    def test_transcript_markdown_has_table(self) -> None:
        run = evaluate_attempt(bundle("jpeg-codec-fidelity"), attempt("jpeg-codec-fidelity", "mixed"))
        text = transcript.transcript_markdown(run)
        self.assertIn("| Case | Status | Runtime ms | Section |", text)


