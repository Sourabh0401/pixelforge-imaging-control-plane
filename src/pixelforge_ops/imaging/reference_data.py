from __future__ import annotations

"""
Load package-local imaging reference assets.

These files live under ``pixelforge_ops.imaging.reference`` because they are
runtime inputs, not test fixtures. The imaging control plane uses them for
lane threshold profiles, issue taxonomy, partner delivery contracts, rollout
policies, exception rules, and operator questionnaires.

The helpers in this module keep three things consistent:

1. deterministic loading and digesting
2. shallow schema validation before a packet is built
3. copy-on-read semantics so callers cannot mutate the cached payloads
"""

from copy import deepcopy
from functools import lru_cache
from importlib import resources
from typing import Any, Iterable, Mapping, Sequence

from pixelforge_ops.utils import json_digest


REFERENCE_PACKAGE = "pixelforge_ops.imaging.reference"


REFERENCE_FILES = {
    "lane_threshold_profiles.json": "threshold profiles",
    "issue_taxonomy.json": "issue taxonomy",
    "partner_delivery_profiles.json": "partner delivery profiles",
    "codec_rollout_policies.json": "codec rollout policies",
    "manifest_exception_policies.json": "manifest exception policies",
    "release_questionnaires.json": "release questionnaires",
}


def _resource_text(name: str) -> str:
    resource = resources.files(REFERENCE_PACKAGE).joinpath(name)
    return resource.read_text(encoding="utf-8")


@lru_cache(maxsize=None)
def _resource_payload(name: str) -> Any:
    import json

    return json.loads(_resource_text(name))


def reference_names() -> list[str]:
    return sorted(REFERENCE_FILES)


def load_reference_data(name: str) -> Any:
    if name not in REFERENCE_FILES:
        raise KeyError(name)
    payload = _resource_payload(name)
    validator = _VALIDATORS.get(name)
    if validator is not None:
        validator(payload)
    return deepcopy(payload)


def reference_digest(name: str) -> str:
    return json_digest(load_reference_data(name))


def _require_mapping(payload: Any, label: str) -> Mapping[str, object]:
    if not isinstance(payload, Mapping):
        raise ValueError(f"{label} must be a mapping")
    return payload


def _require_sequence(payload: Any, label: str) -> Sequence[object]:
    if not isinstance(payload, Sequence) or isinstance(payload, (str, bytes, bytearray)):
        raise ValueError(f"{label} must be a sequence")
    return payload


def _require_text(value: Any, label: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{label} must be non-empty")
    return text


def _require_text_list(value: Any, label: str) -> list[str]:
    items = _require_sequence(value, label)
    result = []
    for index, item in enumerate(items):
        result.append(_require_text(item, f"{label}[{index}]"))
    return result


def validate_threshold_profiles(payload: Any) -> None:
    root = _require_mapping(payload, "threshold profiles")
    profiles = _require_sequence(root.get("profiles", []), "profiles")
    if not profiles:
        raise ValueError("profiles must not be empty")
    for index, row in enumerate(profiles):
        profile = _require_mapping(row, f"profiles[{index}]")
        _require_text(profile.get("lane"), f"profiles[{index}].lane")
        _require_text(profile.get("owner_group"), f"profiles[{index}].owner_group")
        _require_text(profile.get("release_channel"), f"profiles[{index}].release_channel")
        comparators = _require_mapping(profile.get("comparators", {}), f"profiles[{index}].comparators")
        for comparator in ("pixel_matrix", "channel_histogram", "color_delta", "region_diff", "render_manifest", "image_release_gate"):
            if comparator not in comparators:
                raise ValueError(f"profiles[{index}].comparators missing {comparator}")
        sampling = _require_mapping(profile.get("sampling", {}), f"profiles[{index}].sampling")
        _require_text(sampling.get("grid"), f"profiles[{index}].sampling.grid")
        _require_text_list(sampling.get("required_regions", []), f"profiles[{index}].sampling.required_regions")
        budget = _require_mapping(profile.get("render_budget", {}), f"profiles[{index}].render_budget")
        if int(budget.get("max_runtime_ms", 0) or 0) <= 0:
            raise ValueError(f"profiles[{index}].render_budget.max_runtime_ms must be positive")
        metadata = _require_mapping(profile.get("metadata", {}), f"profiles[{index}].metadata")
        _require_text_list(metadata.get("required_fields", []), f"profiles[{index}].metadata.required_fields")


def validate_issue_taxonomy(payload: Any) -> None:
    root = _require_mapping(payload, "issue taxonomy")
    issues = _require_sequence(root.get("issues", []), "issues")
    codes: set[str] = set()
    for index, row in enumerate(issues):
        issue = _require_mapping(row, f"issues[{index}]")
        code = _require_text(issue.get("code"), f"issues[{index}].code")
        if code in codes:
            raise ValueError(f"duplicate issue code: {code}")
        codes.add(code)
        _require_text(issue.get("family"), f"issues[{index}].family")
        _require_text(issue.get("default_severity"), f"issues[{index}].default_severity")
        _require_text(issue.get("owner_group"), f"issues[{index}].owner_group")
        _require_text(issue.get("summary"), f"issues[{index}].summary")
        _require_text(issue.get("operator_action"), f"issues[{index}].operator_action")


def validate_partner_delivery_profiles(payload: Any) -> None:
    root = _require_mapping(payload, "partner delivery profiles")
    profiles = _require_sequence(root.get("profiles", []), "profiles")
    for index, row in enumerate(profiles):
        profile = _require_mapping(row, f"profiles[{index}]")
        _require_text(profile.get("partner"), f"profiles[{index}].partner")
        _require_text(profile.get("lane"), f"profiles[{index}].lane")
        _require_text_list(profile.get("required_files", []), f"profiles[{index}].required_files")
        _require_text_list(profile.get("required_codecs", []), f"profiles[{index}].required_codecs")
        routing = _require_mapping(profile.get("routing", {}), f"profiles[{index}].routing")
        _require_text(routing.get("owner_group"), f"profiles[{index}].routing.owner_group")


def validate_codec_rollout_policies(payload: Any) -> None:
    root = _require_mapping(payload, "codec rollout policies")
    policies = _require_sequence(root.get("policies", []), "policies")
    for index, row in enumerate(policies):
        policy = _require_mapping(row, f"policies[{index}]")
        _require_text(policy.get("lane"), f"policies[{index}].lane")
        _require_text(policy.get("codec"), f"policies[{index}].codec")
        _require_text(policy.get("release_channel"), f"policies[{index}].release_channel")
        if int(policy.get("canary_percent", 0) or 0) < 0:
            raise ValueError(f"policies[{index}].canary_percent must be non-negative")


def validate_manifest_exception_policies(payload: Any) -> None:
    root = _require_mapping(payload, "manifest exception policies")
    policies = _require_sequence(root.get("policies", []), "policies")
    for index, row in enumerate(policies):
        policy = _require_mapping(row, f"policies[{index}]")
        _require_text(policy.get("lane"), f"policies[{index}].lane")
        _require_text_list(policy.get("allowed_issue_codes", []), f"policies[{index}].allowed_issue_codes")
        _require_text_list(policy.get("blocked_issue_codes", []), f"policies[{index}].blocked_issue_codes")
        expiry = _require_mapping(policy.get("expiry_classes", {}), f"policies[{index}].expiry_classes")
        if not expiry:
            raise ValueError(f"policies[{index}].expiry_classes must not be empty")


def validate_release_questionnaires(payload: Any) -> None:
    root = _require_mapping(payload, "release questionnaires")
    questionnaires = _require_sequence(root.get("questionnaires", []), "questionnaires")
    for index, row in enumerate(questionnaires):
        questionnaire = _require_mapping(row, f"questionnaires[{index}]")
        _require_text(questionnaire.get("lane"), f"questionnaires[{index}].lane")
        _require_text(questionnaire.get("title"), f"questionnaires[{index}].title")
        _require_text_list(questionnaire.get("questions", []), f"questionnaires[{index}].questions")
        _require_text_list(questionnaire.get("handoff_template", []), f"questionnaires[{index}].handoff_template")


def reference_summary() -> dict[str, object]:
    items = []
    for name in reference_names():
        payload = load_reference_data(name)
        label = REFERENCE_FILES[name]
        if isinstance(payload, Mapping):
            keys = sorted(str(key) for key in payload.keys())
        else:
            keys = []
        items.append({"name": name, "label": label, "keys": keys, "digest": reference_digest(name)})
    return {"count": len(items), "items": items}


_VALIDATORS = {
    "lane_threshold_profiles.json": validate_threshold_profiles,
    "issue_taxonomy.json": validate_issue_taxonomy,
    "partner_delivery_profiles.json": validate_partner_delivery_profiles,
    "codec_rollout_policies.json": validate_codec_rollout_policies,
    "manifest_exception_policies.json": validate_manifest_exception_policies,
    "release_questionnaires.json": validate_release_questionnaires,
}
