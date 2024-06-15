from __future__ import annotations

import math
import re


def exact(answer, expected) -> bool:
    return answer == expected


def unordered_list(answer, expected) -> bool:
    return sorted(answer or []) == sorted(expected or [])


def numeric_range(answer, expected) -> bool:
    if answer is None:
        return False
    return float(expected["min"]) <= float(answer) <= float(expected["max"])


def mapping_subset(answer, expected) -> bool:
    if not isinstance(answer, dict):
        return False
    return all(answer.get(key) == value for key, value in expected.items())


def contains_tokens(answer, expected) -> bool:
    haystack = str(answer or "")
    return all(token in haystack for token in expected)


def rounded_number(answer, expected) -> bool:
    return round(float(answer), int(expected["places"])) == round(float(expected["value"]), int(expected["places"]))


def ordered_pairs(answer, expected) -> bool:
    return list(answer or []) == list(expected or [])


def regex_groups(answer, expected) -> bool:
    match = re.search(expected["pattern"], str(answer or ""))
    if not match:
        return False
    return match.groupdict() == expected["groups"]


def event_log(answer, expected) -> bool:
    if not isinstance(answer, list):
        return False
    return [item.get("event") for item in answer] == list(expected)


def csv_rows(answer, expected) -> bool:
    return [tuple(row) for row in answer] == [tuple(row) for row in expected]


def artifact_manifest(answer, expected) -> bool:
    if not isinstance(answer, dict):
        return False
    return answer.get("digest") == expected.get("digest") and sorted(answer.get("files", [])) == sorted(expected.get("files", []))


COMPARATORS = {
    "exact": exact,
    "unordered_list": unordered_list,
    "range": numeric_range,
    "mapping_subset": mapping_subset,
    "contains_tokens": contains_tokens,
    "rounded_number": rounded_number,
    "ordered_pairs": ordered_pairs,
    "regex_groups": regex_groups,
    "event_log": event_log,
    "csv_rows": csv_rows,
    "artifact_manifest": artifact_manifest,
}


def compare(name: str, answer, expected) -> bool:
    return COMPARATORS[name](answer, expected)
