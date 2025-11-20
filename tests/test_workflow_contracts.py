from __future__ import annotations

import unittest

from pixelforge_ops.cataloging import workflow_contracts
from tests.ext_helpers import bundle


class WorkflowContractTests(unittest.TestCase):
    def test_workflow_steps_exist_for_bundle_domain(self) -> None:
        item = bundle("jpeg-codec-fidelity")
        self.assertTrue(workflow_contracts.workflow_steps(item.domain))

    def test_required_artifacts_include_bundle_and_release_files(self) -> None:
        artifacts = workflow_contracts.required_artifacts("codec_ops")
        self.assertIn("bundle.json", artifacts)
        self.assertIn("release_notes.md", artifacts)

    def test_validate_bundle_contract_accepts_fixture_bundle(self) -> None:
        item = bundle("raster-transform-tiling")
        self.assertEqual(workflow_contracts.validate_bundle_contract(item), [])

    def test_contract_digest_is_stable(self) -> None:
        self.assertEqual(
            workflow_contracts.contract_digest("partner_ops"),
            workflow_contracts.contract_digest("partner_ops"),
        )

    def test_missing_artifacts_reports_gap(self) -> None:
        missing = workflow_contracts.missing_artifacts("image_quality_ops", ["bundle.json"])
        self.assertIn("audit_packet.json", missing)

    def test_phase_summary_groups_steps(self) -> None:
        summary = workflow_contracts.phase_summary("color_ops")
        self.assertIn("release", summary)

    def test_render_contract_markdown_mentions_steps(self) -> None:
        text = workflow_contracts.render_contract_markdown("pipeline_ops")
        self.assertIn("platform-runtime-review", text)


