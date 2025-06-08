from __future__ import annotations

import unittest

from engineering_challenge.cataloging import workflow_contracts
from tests.ext_helpers import bundle


class WorkflowContractTests(unittest.TestCase):
    def test_workflow_steps_exist_for_bundle_domain(self) -> None:
        item = bundle("merchant-closeout")
        self.assertTrue(workflow_contracts.workflow_steps(item.domain))

    def test_required_artifacts_include_bundle_and_release_files(self) -> None:
        artifacts = workflow_contracts.required_artifacts("finance_ops")
        self.assertIn("bundle.json", artifacts)
        self.assertIn("release_notes.md", artifacts)

    def test_validate_bundle_contract_accepts_fixture_bundle(self) -> None:
        item = bundle("warehouse-routing")
        self.assertEqual(workflow_contracts.validate_bundle_contract(item), [])

    def test_contract_digest_is_stable(self) -> None:
        self.assertEqual(
            workflow_contracts.contract_digest("support_ops"),
            workflow_contracts.contract_digest("support_ops"),
        )

    def test_missing_artifacts_reports_gap(self) -> None:
        missing = workflow_contracts.missing_artifacts("risk_ops", ["bundle.json"])
        self.assertIn("audit_packet.json", missing)

    def test_phase_summary_groups_steps(self) -> None:
        summary = workflow_contracts.phase_summary("education_ops")
        self.assertIn("release", summary)

    def test_render_contract_markdown_mentions_steps(self) -> None:
        text = workflow_contracts.render_contract_markdown("platform_ops")
        self.assertIn("platform-runtime-review", text)
