from __future__ import annotations

"""
Artifact reconciliation between expected release contracts and actual outputs.

The existing inventory helper is good at counting what a manifest already has.
This module answers a different operational question: what did the lane expect
to produce, what actually showed up, what appears to be renamed rather than
missing, and which mismatches are serious enough to block release work.

Why this exists as a separate module:

- operators compare current packets with older accepted packets constantly
- partner-export lanes need file-level contract clarity, not only digest checks
- codec-family rollout logic benefits from understanding missing versus renamed
  artifacts before deciding whether the lane really regressed
- artifact inventory can say a packet is internally consistent while still
  missing a lane-specific file the release team expected to see

The functions below intentionally return stable dictionaries and ordered lists.
That keeps audit packets, release notes, queue builders, and operator briefs in
sync when they consume the same reconciliation result.
"""

from typing import Iterable, Mapping, Sequence

from pixelforge_ops.utils import json_digest


def normalize_expected_artifact(row: Mapping[str, object]) -> dict[str, object]:
    return {
        "path": str(row.get("path", "")).strip(),
        "lane": str(row.get("lane", "unknown") or "unknown"),
        "codec": str(row.get("codec", row.get("format", "unknown")) or "unknown").lower(),
        "artifact_type": str(row.get("artifact_type", "frame") or "frame"),
        "required": bool(row.get("required", True)),
        "delivery_only": bool(row.get("delivery_only", False)),
        "partner_visible": bool(row.get("partner_visible", False)),
        "group": str(row.get("group", "default") or "default"),
        "role": str(row.get("role", row.get("artifact_type", "frame")) or "frame"),
        "description": str(row.get("description", "")).strip(),
    }


def normalize_expected_artifacts(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    items = [normalize_expected_artifact(row) for row in rows]
    items.sort(
        key=lambda row: (
            str(row["lane"]),
            str(row["codec"]),
            str(row["artifact_type"]),
            str(row["group"]),
            str(row["path"]),
        )
    )
    return items


def normalize_actual_artifact(row: Mapping[str, object]) -> dict[str, object]:
    return {
        "path": str(row.get("path", "")).strip(),
        "lane": str(row.get("lane", "unknown") or "unknown"),
        "codec": str(row.get("codec", row.get("format", "unknown")) or "unknown").lower(),
        "artifact_type": str(row.get("artifact_type", "frame") or "frame"),
        "bytes": int(row.get("bytes", row.get("size_bytes", 0)) or 0),
        "digest": str(row.get("digest", "")).strip(),
        "group": str(row.get("group", "default") or "default"),
        "role": str(row.get("role", row.get("artifact_type", "frame")) or "frame"),
    }


def normalize_actual_artifacts(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    items = [normalize_actual_artifact(row) for row in rows]
    items.sort(
        key=lambda row: (
            str(row["lane"]),
            str(row["codec"]),
            str(row["artifact_type"]),
            str(row["group"]),
            str(row["path"]),
        )
    )
    return items


def artifact_identity(row: Mapping[str, object]) -> tuple[str, str, str, str]:
    return (
        str(row.get("lane", "unknown")),
        str(row.get("codec", "unknown")),
        str(row.get("artifact_type", "frame")),
        str(row.get("path", "")),
    )


def artifact_contract_key(row: Mapping[str, object]) -> tuple[str, str, str, str]:
    return (
        str(row.get("lane", "unknown")),
        str(row.get("codec", "unknown")),
        str(row.get("artifact_type", "frame")),
        str(row.get("group", "default")),
    )


def contract_signature(row: Mapping[str, object]) -> str:
    payload = {
        "lane": str(row.get("lane", "unknown")),
        "codec": str(row.get("codec", "unknown")),
        "artifact_type": str(row.get("artifact_type", "frame")),
        "path": str(row.get("path", "")),
        "group": str(row.get("group", "default")),
        "role": str(row.get("role", "frame")),
    }
    return json_digest(payload)


def expected_index(rows: Iterable[Mapping[str, object]]) -> dict[tuple[str, str, str, str], dict[str, object]]:
    return {artifact_identity(row): dict(row) for row in normalize_expected_artifacts(rows)}


def actual_index(rows: Iterable[Mapping[str, object]]) -> dict[tuple[str, str, str, str], dict[str, object]]:
    return {artifact_identity(row): dict(row) for row in normalize_actual_artifacts(rows)}


def missing_expected_artifacts(expected: Iterable[Mapping[str, object]], actual: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    actual_rows = actual_index(actual)
    missing = []
    for row in normalize_expected_artifacts(expected):
        key = artifact_identity(row)
        if key not in actual_rows:
            missing.append(row)
    return missing


def unexpected_actual_artifacts(expected: Iterable[Mapping[str, object]], actual: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    expected_rows = expected_index(expected)
    unexpected = []
    for row in normalize_actual_artifacts(actual):
        key = artifact_identity(row)
        if key not in expected_rows:
            unexpected.append(row)
    return unexpected


def _candidate_rename_pairs(
    expected: Sequence[Mapping[str, object]],
    actual: Sequence[Mapping[str, object]],
) -> list[tuple[dict[str, object], dict[str, object]]]:
    pairs = []
    used_actual: set[int] = set()
    for expected_row in expected:
        expected_key = artifact_contract_key(expected_row)
        for actual_index_value, actual_row in enumerate(actual):
            if actual_index_value in used_actual:
                continue
            actual_key = artifact_contract_key(actual_row)
            if expected_key != actual_key:
                continue
            if str(expected_row.get("path")) == str(actual_row.get("path")):
                continue
            pairs.append((dict(expected_row), dict(actual_row)))
            used_actual.add(actual_index_value)
            break
    return pairs


def renamed_artifact_candidates(expected: Iterable[Mapping[str, object]], actual: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    missing = missing_expected_artifacts(expected, actual)
    unexpected = unexpected_actual_artifacts(expected, actual)
    rows = []
    for left, right in _candidate_rename_pairs(missing, unexpected):
        rows.append(
            {
                "lane": left["lane"],
                "codec": left["codec"],
                "artifact_type": left["artifact_type"],
                "expected_path": left["path"],
                "actual_path": right["path"],
                "group": left.get("group", "default"),
                "expected_signature": contract_signature(left),
                "actual_signature": contract_signature(right),
            }
        )
    rows.sort(key=lambda row: (row["lane"], row["codec"], row["artifact_type"], row["expected_path"], row["actual_path"]))
    return rows


def lane_artifact_matrix(expected: Iterable[Mapping[str, object]], actual: Iterable[Mapping[str, object]]) -> dict[str, dict[str, object]]:
    lanes = sorted(
        {
            str(row.get("lane", "unknown"))
            for row in [*normalize_expected_artifacts(expected), *normalize_actual_artifacts(actual)]
        }
    )
    matrix: dict[str, dict[str, object]] = {}
    for lane in lanes:
        expected_rows = [row for row in normalize_expected_artifacts(expected) if str(row.get("lane")) == lane]
        actual_rows = [row for row in normalize_actual_artifacts(actual) if str(row.get("lane")) == lane]
        missing = missing_expected_artifacts(expected_rows, actual_rows)
        unexpected = unexpected_actual_artifacts(expected_rows, actual_rows)
        matrix[lane] = {
            "expected_count": len(expected_rows),
            "actual_count": len(actual_rows),
            "missing_paths": [str(row["path"]) for row in missing],
            "unexpected_paths": [str(row["path"]) for row in unexpected],
            "renamed_candidates": renamed_artifact_candidates(expected_rows, actual_rows),
        }
    return matrix


def codec_artifact_counts(actual: Iterable[Mapping[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in normalize_actual_artifacts(actual):
        codec = str(row["codec"])
        counts[codec] = counts.get(codec, 0) + 1
    return dict(sorted(counts.items()))


def required_delivery_gaps(expected: Iterable[Mapping[str, object]], actual: Iterable[Mapping[str, object]]) -> list[str]:
    missing = missing_expected_artifacts(expected, actual)
    issues = []
    for row in missing:
        if not bool(row.get("required", True)):
            continue
        if bool(row.get("delivery_only")) or bool(row.get("partner_visible")):
            issues.append(f"missing delivery artifact: {row['path']}")
    return sorted(issues)


def artifact_reconciliation_summary(
    expected: Iterable[Mapping[str, object]],
    actual: Iterable[Mapping[str, object]],
    blocked_lanes: Sequence[str] = (),
) -> dict[str, object]:
    expected_rows = normalize_expected_artifacts(expected)
    actual_rows = normalize_actual_artifacts(actual)
    missing = missing_expected_artifacts(expected_rows, actual_rows)
    unexpected = unexpected_actual_artifacts(expected_rows, actual_rows)
    renamed = renamed_artifact_candidates(expected_rows, actual_rows)
    delivery_gaps = required_delivery_gaps(expected_rows, actual_rows)
    blocked_lane_set = {str(value) for value in blocked_lanes}

    issues = []
    issues.extend(f"missing artifact: {row['path']}" for row in missing if bool(row.get("required", True)))
    issues.extend(f"unexpected artifact: {row['path']}" for row in unexpected)
    issues.extend(f"renamed artifact candidate: {row['expected_path']} -> {row['actual_path']}" for row in renamed)
    issues.extend(delivery_gaps)
    if blocked_lane_set:
        for lane in sorted(blocked_lane_set):
            lane_missing = [row for row in missing if str(row.get("lane")) == lane and bool(row.get("required", True))]
            if lane_missing:
                issues.append(f"blocked lane missing required artifacts: {lane}")

    blocking = bool(delivery_gaps) or any(bool(row.get("required", True)) for row in missing if str(row.get("lane")) in blocked_lane_set or not blocked_lane_set)
    status = "block" if blocking else "warn" if issues else "ok"
    return {
        "status": status,
        "severity": status,
        "passed": status != "block",
        "issue_codes": ["artifact-reconciliation"] if issues else [],
        "issues": sorted(dict.fromkeys(issues)),
        "expected_count": len(expected_rows),
        "actual_count": len(actual_rows),
        "missing_required": [str(row["path"]) for row in missing if bool(row.get("required", True))],
        "missing_optional": [str(row["path"]) for row in missing if not bool(row.get("required", True))],
        "unexpected_paths": [str(row["path"]) for row in unexpected],
        "renamed_candidates": renamed,
        "delivery_gaps": delivery_gaps,
        "lane_matrix": lane_artifact_matrix(expected_rows, actual_rows),
        "codec_counts": codec_artifact_counts(actual_rows),
        "digest": json_digest(
            {
                "missing_required": [str(row["path"]) for row in missing if bool(row.get("required", True))],
                "unexpected_paths": [str(row["path"]) for row in unexpected],
                "renamed_candidates": renamed,
                "delivery_gaps": delivery_gaps,
            }
        ),
    }
