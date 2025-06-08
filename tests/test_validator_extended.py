from __future__ import annotations

import unittest
from dataclasses import replace

from engineering_challenge import validator
from engineering_challenge.config import RuntimeProfile
from engineering_challenge.models import ExerciseBundle
from tests.helpers import bundle


def _bundle_with(item: ExerciseBundle, **changes: object) -> ExerciseBundle:
    return replace(item, **changes)


class ValidatorExtendedTests(unittest.TestCase):
    def test_validate_bundle_returns_tuple(self) -> None:
        self.assertIsInstance(validator.validate_bundle(bundle("merchant-closeout")), tuple)

    def test_owner_missing_adds_error(self) -> None:
        issues = validator.validate_bundle(_bundle_with(bundle("merchant-closeout"), owner=""))
        self.assertTrue(any(issue.code == "owner-missing" for issue in issues))

    def test_owner_whitespace_adds_error(self) -> None:
        issues = validator.validate_bundle(_bundle_with(bundle("merchant-closeout"), owner="   "))
        self.assertTrue(any(issue.code == "owner-missing" for issue in issues))

    def test_bundle_too_large_uses_profile_limit(self) -> None:
        profile = RuntimeProfile(max_bundle_cases=2)
        issues = validator.validate_bundle(bundle("merchant-closeout"), profile)
        self.assertTrue(any(issue.code == "bundle-too-large" for issue in issues))

    def test_public_floor_uses_profile_limit(self) -> None:
        profile = RuntimeProfile(required_public_case_floor=100)
        issues = validator.validate_bundle(bundle("merchant-closeout"), profile)
        self.assertTrue(any(issue.code == "public-floor" for issue in issues))

    def test_hidden_floor_uses_profile_limit(self) -> None:
        profile = RuntimeProfile(required_hidden_case_floor=100)
        issues = validator.validate_bundle(bundle("merchant-closeout"), profile)
        self.assertTrue(any(issue.code == "hidden-floor" for issue in issues))

    def test_duplicate_case_ids_add_error(self) -> None:
        item = bundle("merchant-closeout")
        issues = validator.validate_bundle(_bundle_with(item, cases=item.cases + (item.cases[0],)))
        self.assertTrue(any(issue.code == "duplicate-case-id" for issue in issues))

    def test_invalid_time_limit_adds_error(self) -> None:
        item = bundle("merchant-closeout")
        cases = (replace(item.cases[0], time_limit_ms=0), *item.cases[1:])
        issues = validator.validate_bundle(_bundle_with(item, cases=cases))
        self.assertTrue(any(issue.code == "invalid-time-limit" for issue in issues))

    def test_invalid_time_limit_message_mentions_case_id(self) -> None:
        item = bundle("merchant-closeout")
        cases = (replace(item.cases[0], time_limit_ms=0), *item.cases[1:])
        issues = validator.validate_bundle(_bundle_with(item, cases=cases))
        self.assertTrue(any(item.cases[0].case_id in issue.message for issue in issues if issue.code == "invalid-time-limit"))

    def test_invalid_weight_adds_error(self) -> None:
        item = bundle("merchant-closeout")
        cases = (replace(item.cases[0], weight=0), *item.cases[1:])
        issues = validator.validate_bundle(_bundle_with(item, cases=cases))
        self.assertTrue(any(issue.code == "invalid-weight" for issue in issues))

    def test_invalid_weight_message_mentions_case_id(self) -> None:
        item = bundle("merchant-closeout")
        cases = (replace(item.cases[0], weight=0), *item.cases[1:])
        issues = validator.validate_bundle(_bundle_with(item, cases=cases))
        self.assertTrue(any(item.cases[0].case_id in issue.message for issue in issues if issue.code == "invalid-weight"))

    def test_public_duplicate_adds_error(self) -> None:
        item = bundle("merchant-closeout")
        public_case = next(case for case in item.cases if not case.hidden)
        duplicated = replace(public_case, hidden=False)
        issues = validator.validate_bundle(_bundle_with(item, cases=item.cases + (duplicated,)))
        self.assertTrue(any(issue.code == "public-duplicate" for issue in issues))

    def test_hidden_duplicate_does_not_add_public_duplicate_error(self) -> None:
        item = bundle("merchant-closeout")
        public_case = next(case for case in item.cases if not case.hidden)
        hidden_copy = replace(public_case, hidden=True)
        issues = validator.validate_bundle(_bundle_with(item, cases=item.cases + (hidden_copy,)))
        self.assertFalse(any(issue.code == "public-duplicate" for issue in issues))

    def test_unknown_comparator_adds_error(self) -> None:
        item = bundle("merchant-closeout")
        cases = (replace(item.cases[0], comparator="banana"), *item.cases[1:])
        issues = validator.validate_bundle(_bundle_with(item, cases=cases))
        self.assertTrue(any(issue.code == "unknown-comparator" for issue in issues))

    def test_unknown_comparator_message_mentions_case_id(self) -> None:
        item = bundle("merchant-closeout")
        cases = (replace(item.cases[0], comparator="banana"), *item.cases[1:])
        issues = validator.validate_bundle(_bundle_with(item, cases=cases))
        self.assertTrue(any(item.cases[0].case_id in issue.message for issue in issues if issue.code == "unknown-comparator"))

    def test_blank_section_adds_error(self) -> None:
        item = bundle("merchant-closeout")
        cases = (replace(item.cases[0], section=" "), *item.cases[1:])
        issues = validator.validate_bundle(_bundle_with(item, cases=cases))
        self.assertTrue(any(issue.code == "blank-section" for issue in issues))

    def test_hidden_ratio_low_adds_warning(self) -> None:
        item = bundle("merchant-closeout")
        mostly_public = tuple(replace(case, hidden=False) for case in item.cases[:-1]) + (replace(item.cases[-1], hidden=True),)
        issues = validator.validate_bundle(_bundle_with(item, cases=mostly_public))
        self.assertTrue(any(issue.code == "hidden-ratio-low" for issue in issues))

    def test_release_channel_missing_adds_warning(self) -> None:
        item = bundle("merchant-closeout")
        metadata = dict(item.metadata)
        metadata.pop("release_channel", None)
        issues = validator.validate_bundle(_bundle_with(item, metadata=metadata))
        self.assertTrue(any(issue.code == "release-channel-missing" for issue in issues))

    def test_release_channel_present_avoids_warning(self) -> None:
        issues = validator.validate_bundle(bundle("merchant-closeout"))
        self.assertFalse(any(issue.code == "release-channel-missing" for issue in issues))

    def test_validate_release_inputs_flags_duplicate_bundle_ids(self) -> None:
        issues = validator.validate_release_inputs([bundle("merchant-closeout"), bundle("merchant-closeout")])
        self.assertTrue(any(issue.code == "duplicate-bundle" for issue in issues))

    def test_validate_release_inputs_flags_owner_domain_heavy_mix(self) -> None:
        first = bundle("merchant-closeout")
        second = _bundle_with(bundle("warehouse-routing"), bundle_id="warehouse-routing-copy", owner=first.owner, domain=first.domain)
        third = _bundle_with(bundle("claims-intake"), bundle_id="claims-intake-copy", owner=first.owner, domain=first.domain)
        issues = validator.validate_release_inputs([first, second, third])
        self.assertTrue(any(issue.code == "owner-domain-heavy" for issue in issues))

    def test_owner_domain_heavy_warning_mentions_owner(self) -> None:
        first = bundle("merchant-closeout")
        second = _bundle_with(bundle("warehouse-routing"), bundle_id="warehouse-routing-copy", owner=first.owner, domain=first.domain)
        third = _bundle_with(bundle("claims-intake"), bundle_id="claims-intake-copy", owner=first.owner, domain=first.domain)
        issues = validator.validate_release_inputs([first, second, third])
        self.assertTrue(any(first.owner in issue.message for issue in issues if issue.code == "owner-domain-heavy"))

    def test_validate_release_inputs_has_no_issues_for_unique_bundles(self) -> None:
        self.assertEqual(validator.validate_release_inputs([bundle("merchant-closeout"), bundle("warehouse-routing")]), ())

    def test_fixture_bundle_keeps_duplicate_case_issue_absent(self) -> None:
        issues = validator.validate_bundle(bundle("merchant-closeout"))
        self.assertFalse(any(issue.code == "duplicate-case-id" for issue in issues))
