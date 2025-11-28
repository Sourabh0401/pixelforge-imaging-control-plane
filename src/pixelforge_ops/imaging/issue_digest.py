from __future__ import annotations

from typing import Iterable, Mapping

from pixelforge_ops.utils import json_digest


def normalize_issue(issue: Mapping[str, object]) -> dict[str, object]:
    return {
        "severity": str(issue.get("severity", issue.get("status", "warn")) or "warn"),
        "code": str(issue.get("code", "imaging-issue") or "imaging-issue"),
        "lane": str(issue.get("lane", "unknown") or "unknown"),
        "kind": str(issue.get("kind", "generic") or "generic"),
        "message": str(issue.get("message", "") or ""),
        "details": dict(issue.get("details", {}) or {}),
    }


def normalized_issues(issues: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    rows = [normalize_issue(issue) for issue in issues]
    rows.sort(key=lambda row: (str(row["severity"]), str(row["lane"]), str(row["kind"]), str(row["code"]), str(row["message"])))
    return rows


def severity_counts(issues: Iterable[Mapping[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for issue in normalized_issues(issues):
        severity = str(issue["severity"])
        counts[severity] = counts.get(severity, 0) + 1
    return dict(sorted(counts.items()))


def lane_counts(issues: Iterable[Mapping[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for issue in normalized_issues(issues):
        lane = str(issue["lane"])
        counts[lane] = counts.get(lane, 0) + 1
    return dict(sorted(counts.items()))


def digest_issues(issues: Iterable[Mapping[str, object]]) -> str:
    return json_digest({"issues": normalized_issues(issues)})


def render_issue_lines(issues: Iterable[Mapping[str, object]]) -> list[str]:
    lines = []
    for issue in normalized_issues(issues):
        lines.append(f"[{issue['severity']}] {issue['lane']} {issue['kind']}: {issue['message']}")
    return lines

