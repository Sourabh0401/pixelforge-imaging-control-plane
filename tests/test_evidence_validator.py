from __future__ import annotations

import unittest

from engineering_challenge import audit, release
from engineering_challenge.auditpack import contracts, evidence_validator
from engineering_challenge.execution import evaluate_attempt, run_to_dict
from engineering_challenge.scoring import score_run, scorecard_to_dict
from tests.ext_helpers import attempt, bundle


class EvidenceValidatorTests(unittest.TestCase):
    def _packet(self) -> dict[str, object]:
        item = bundle("merchant-closeout")
        run = evaluate_attempt(item, attempt("merchant-closeout", "mixed"))
        card = score_run(run, item)
        manifest = release.build_release_manifest("release-1", [item], notes=("internal",))
        bundle_payload = {
            "bundle_id": item.bundle_id,
            "owner": item.owner,
            "version": item.version,
            "title": item.title,
        }
        run_payload = run_to_dict(run)
        score_payload = scorecard_to_dict(card)
        for field in contracts.required_fields_for_source("bundle"):
            bundle_payload.setdefault(field, f"bundle-{field}")
        for field in contracts.required_fields_for_source("run"):
            run_payload.setdefault(field, f"run-{field}")
        for field in contracts.required_fields_for_source("scorecard"):
            score_payload.setdefault(field, f"score-{field}")
        return evidence_validator.packet_with_trace(
            bundle_payload,
            run_payload,
            score_payload,
            release.manifest_to_dict(manifest),
        )

    def test_valid_packet_has_no_issues(self) -> None:
        packet = self._packet()
        self.assertEqual(evidence_validator.validate_packet(packet), [])

    def test_missing_required_field_is_reported(self) -> None:
        packet = self._packet()
        del packet["bundle"]["field_04"]
        issues = evidence_validator.validate_packet(packet)
        self.assertTrue(any(issue.code == "missing-field" for issue in issues))

    def test_trace_mismatch_is_reported(self) -> None:
        packet = self._packet()
        packet["trace_rows"] = packet["trace_rows"][:-1]
        issues = evidence_validator.validate_packet(packet)
        self.assertTrue(any(issue.code == "missing-trace-row" for issue in issues))

    def test_issue_summary_counts_severity(self) -> None:
        packet = self._packet()
        del packet["bundle"]["owner"]
        summary = evidence_validator.issue_summary(evidence_validator.validate_packet(packet))
        self.assertIn("severity_counts", summary)

    def test_expected_paths_prefix_bundle_and_run(self) -> None:
        packet = self._packet()
        mapping = evidence_validator.expected_paths(packet["bundle"]["bundle_id"], packet["run"]["run_id"])
        self.assertTrue(all(value.startswith(f"{packet['bundle']['bundle_id']}/{packet['run']['run_id']}/") for value in mapping.values()))
