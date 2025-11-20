from __future__ import annotations

import unittest

from pixelforge_ops.auditpack import contracts, evidence_store, export_zip, retention, trace
from pixelforge_ops.execution import evaluate_attempt
from tests.ext_helpers import attempt, bundle


class AuditpackModuleTests(unittest.TestCase):
    def test_artifact_contracts_return_rows(self) -> None:
        self.assertTrue(contracts.artifact_contracts())

    def test_field_contracts_return_rows(self) -> None:
        self.assertTrue(contracts.field_contracts())

    def test_required_artifact_paths_have_values(self) -> None:
        self.assertTrue(contracts.required_artifact_paths())

    def test_required_fields_for_source_filters_contracts(self) -> None:
        self.assertTrue(contracts.required_fields_for_source("bundle"))

    def test_validate_record_fields_reports_missing_fields(self) -> None:
        missing = contracts.validate_record_fields("bundle", {"bundle_id": "x"})
        self.assertTrue(missing)

    def test_evidence_map_prefixes_bundle_and_run(self) -> None:
        mapping = evidence_store.evidence_map("bundle", "run")
        self.assertTrue(all(value.startswith("bundle/run/") for value in mapping.values()))

    def test_missing_paths_detects_absent_values(self) -> None:
        self.assertTrue(evidence_store.missing_paths([]))

    def test_unexpected_paths_detects_extras(self) -> None:
        self.assertTrue(evidence_store.unexpected_paths(["extra.txt"]))

    def test_zip_bytes_round_trip_names(self) -> None:
        data = export_zip.zip_bytes({"a.txt": "alpha", "b.txt": "beta"})
        self.assertEqual(export_zip.zip_names(data), ["a.txt", "b.txt"])

    def test_retention_days_lookup(self) -> None:
        self.assertEqual(retention.retention_days("internal"), 45)

    def test_should_prune_requires_export(self) -> None:
        self.assertFalse(retention.should_prune("internal", 100, False))

    def test_trace_rows_match_run_results(self) -> None:
        run = evaluate_attempt(bundle("jpeg-codec-fidelity"), attempt("jpeg-codec-fidelity", "mixed"))
        rows = trace.trace_rows(run)
        self.assertEqual(len(rows), len(run.case_results))

    def test_trace_digest_payload_has_cases(self) -> None:
        run = evaluate_attempt(bundle("jpeg-codec-fidelity"), attempt("jpeg-codec-fidelity", "mixed"))
        payload = trace.trace_digest_payload(run)
        self.assertIn("cases", payload)


