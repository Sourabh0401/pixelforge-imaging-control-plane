from __future__ import annotations

from typing import Iterable, Mapping

from .reference_data import load_reference_data


def _policies() -> list[dict[str, object]]:
    payload = load_reference_data("manifest_exception_policies.json")
    return [dict(row) for row in payload["policies"]]


def exception_policy(lane: str) -> dict[str, object]:
    for row in _policies():
        if str(row.get("lane")) == lane:
            return row
    raise KeyError(lane)


def allow_issue(lane: str, code: str, missing_codec: str | None = None, missing_field: str | None = None) -> bool:
    policy = exception_policy(lane)
    normalized = str(code)
    if normalized in set(str(value) for value in policy.get("blocked_issue_codes", [])):
        return False
    if normalized in set(str(value) for value in policy.get("allowed_issue_codes", [])):
        return True
    if missing_codec and missing_codec in set(str(value) for value in policy.get("allowed_missing_codecs", [])):
        return True
    if missing_field and missing_field in set(str(value) for value in policy.get("allowed_missing_metadata", [])):
        return True
    return False


def exception_summary(lane: str, issues: Iterable[Mapping[str, object] | str]) -> dict[str, object]:
    downgraded = []
    remaining = []
    for issue in issues:
        if isinstance(issue, Mapping):
            code = str(issue.get("code", "operator-note"))
            missing_codec = issue.get("missing_codec")
            missing_field = issue.get("missing_field")
        else:
            code = str(issue)
            missing_codec = None
            missing_field = None
        if allow_issue(lane, code, missing_codec=missing_codec, missing_field=missing_field):
            downgraded.append(code)
        else:
            remaining.append(code)
    return {
        "lane": lane,
        "downgraded_codes": sorted(downgraded),
        "remaining_blockers": sorted(remaining),
        "passed": not remaining,
        "status": "block" if remaining else "warn" if downgraded else "ok",
    }
