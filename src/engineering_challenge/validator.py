from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .config import RuntimeProfile
from .catalog import duplicate_case_ids
from .models import ExerciseBundle


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    code: str
    message: str


def validate_bundle(bundle: ExerciseBundle, profile: RuntimeProfile | None = None) -> tuple[ValidationIssue, ...]:
    profile = profile or RuntimeProfile()
    issues: list[ValidationIssue] = []
    if not bundle.owner.strip():
        issues.append(ValidationIssue("error", "owner-missing", "bundle owner is missing"))
    if len(bundle.cases) > profile.max_bundle_cases:
        issues.append(ValidationIssue("error", "bundle-too-large", "bundle exceeds case limit"))
    if len(bundle.public_cases()) < profile.required_public_case_floor:
        issues.append(ValidationIssue("error", "public-floor", "bundle needs more public cases"))
    if len(bundle.hidden_cases()) < profile.required_hidden_case_floor:
        issues.append(ValidationIssue("error", "hidden-floor", "bundle needs more hidden cases"))
    if duplicate_case_ids(bundle):
        issues.append(ValidationIssue("error", "duplicate-case-id", "bundle contains duplicate case ids"))
    seen_public = set()
    for case in bundle.cases:
        if case.time_limit_ms <= 0:
            issues.append(ValidationIssue("error", "invalid-time-limit", f"{case.case_id} has a non-positive timeout"))
        if case.weight <= 0:
            issues.append(ValidationIssue("error", "invalid-weight", f"{case.case_id} has a non-positive weight"))
        if case.case_id in seen_public and not case.hidden:
            issues.append(ValidationIssue("error", "public-duplicate", f"{case.case_id} repeats in public cases"))
        if not case.hidden:
            seen_public.add(case.case_id)
        if case.comparator not in {"exact", "unordered_list", "range", "mapping_subset", "contains_tokens"}:
            issues.append(ValidationIssue("error", "unknown-comparator", f"{case.case_id} uses unsupported comparator"))
        if case.section.strip() == "":
            issues.append(ValidationIssue("error", "blank-section", f"{case.case_id} has no section"))
    hidden_ratio = len(bundle.hidden_cases()) / max(len(bundle.cases), 1)
    if hidden_ratio < 0.30:
        issues.append(ValidationIssue("warning", "hidden-ratio-low", "bundle hidden-case ratio is below 30 percent"))
    if "release_channel" not in bundle.metadata:
        issues.append(ValidationIssue("warning", "release-channel-missing", "bundle metadata omits release channel"))
    return tuple(issues)


def validate_release_inputs(bundles: Iterable[ExerciseBundle]) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    bundle_ids = [bundle.bundle_id for bundle in bundles]
    if len(bundle_ids) != len(set(bundle_ids)):
        issues.append(ValidationIssue("error", "duplicate-bundle", "release includes duplicate bundle ids"))
    owner_domains: dict[tuple[str, str], int] = {}
    for bundle in bundles:
        key = (bundle.owner, bundle.domain)
        owner_domains[key] = owner_domains.get(key, 0) + 1
    for (owner, domain), count in owner_domains.items():
        if count > 2:
            issues.append(ValidationIssue("warning", "owner-domain-heavy", f"{owner} owns {count} bundles in {domain}"))
    return tuple(issues)
