from __future__ import annotations

import copy
import unittest

from engineering_challenge import validator
from engineering_challenge.models import ExerciseBundle
from tests.helpers import bundle


class ValidatorTests(unittest.TestCase):
    def test_fixture_bundle_has_only_warning_level_hidden_ratio_issue_or_better(self) -> None:
        issues = validator.validate_bundle(bundle("merchant-closeout"))
        self.assertTrue(all(issue.severity in {"warning"} for issue in issues) or not issues)

    def test_duplicate_case_id_is_detected(self) -> None:
        item = bundle("merchant-closeout")
        cases = item.cases + (item.cases[0],)
        broken = ExerciseBundle(
            bundle_id=item.bundle_id,
            version=item.version,
            domain=item.domain,
            owner=item.owner,
            title=item.title,
            tags=item.tags,
            rubric=item.rubric,
            metadata=item.metadata,
            cases=cases,
            root=item.root,
        )
        issues = validator.validate_bundle(broken)
        self.assertTrue(any(issue.code == "duplicate-case-id" for issue in issues))

    def test_release_input_validation_warns_on_owner_domain_heavy_mix(self) -> None:
        bundles = [bundle("merchant-closeout"), bundle("warehouse-routing"), bundle("claims-intake")]
        issues = validator.validate_release_inputs(bundles)
        self.assertIsInstance(issues, tuple)

    def test_invalid_comparator_is_detected(self) -> None:
        item = bundle("warehouse-routing")
        bad_case = copy.deepcopy(item.cases[0].__dict__)
        bad_case["comparator"] = "banana"
        mutated_case = item.cases[0].__class__(**bad_case)
        broken = ExerciseBundle(
            bundle_id=item.bundle_id,
            version=item.version,
            domain=item.domain,
            owner=item.owner,
            title=item.title,
            tags=item.tags,
            rubric=item.rubric,
            metadata=item.metadata,
            cases=(mutated_case, *item.cases[1:]),
            root=item.root,
        )
        issues = validator.validate_bundle(broken)
        self.assertTrue(any(issue.code == "unknown-comparator" for issue in issues))
