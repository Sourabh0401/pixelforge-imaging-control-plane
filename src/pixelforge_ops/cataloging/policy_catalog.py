from __future__ import annotations

from pixelforge_ops.datafiles import clone_data, load_json_data


_DATA = load_json_data("cataloging", "policy_catalog.json")
DOMAIN_POLICIES = _DATA["domain_policies"]
COMPARATOR_CONTRACTS = _DATA["comparator_contracts"]
SECTION_POLICIES = _DATA["section_policies"]
TAG_CANONICALIZATION = _DATA["tag_canonicalization"]


def domain_policy(domain: str) -> dict[str, object]:
    return clone_data(DOMAIN_POLICIES[domain])


def comparator_policy(name: str) -> dict[str, object]:
    return clone_data(COMPARATOR_CONTRACTS[name])


def section_policy(name: str) -> dict[str, object]:
    return clone_data(SECTION_POLICIES[name])


def canonical_tags(tags: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    output = []
    for tag in tags:
        key = str(tag).strip().lower()
        output.append(TAG_CANONICALIZATION.get(key, key.replace("_", "-")))
    return tuple(dict.fromkeys(output))


def required_metadata_fields(domain: str) -> tuple[str, ...]:
    return tuple(DOMAIN_POLICIES[domain]["required_metadata"])


def review_path(section: str) -> tuple[str, ...]:
    return tuple(SECTION_POLICIES[section]["required_reviewers"])


def release_channel_policy(domain: str, channel: str) -> bool:
    return channel in DOMAIN_POLICIES[domain]["release_channels"]


def comparator_supports_partial_credit(name: str) -> bool:
    return bool(COMPARATOR_CONTRACTS[name]["supports_partial_credit"])


def section_weight(domain: str, section: str) -> float:
    return float(DOMAIN_POLICIES[domain]["section_weights"][section])


def bundle_envelope(domain: str) -> dict[str, object]:
    policy = DOMAIN_POLICIES[domain]
    return {
        "domain": domain,
        "release_channels": list(policy["release_channels"]),
        "risk_thresholds": clone_data(policy["risk_thresholds"]),
        "required_metadata": list(policy["required_metadata"]),
    }
