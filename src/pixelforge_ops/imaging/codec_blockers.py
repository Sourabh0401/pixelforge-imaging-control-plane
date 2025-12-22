from __future__ import annotations

"""
Codec-family blocker classification.

`codec_profile` tells us how each codec lane looks in isolation. This module
goes one step further and frames the result the way release owners talk about
it: which family is blocking, which is degraded but still potentially shippable
in watch mode, and which families are safe to keep moving in a partial rollout.
"""

from collections import defaultdict
from typing import Iterable, Mapping


def normalize_codec_result(row: Mapping[str, object]) -> dict[str, object]:
    return {
        "lane": str(row.get("lane", "unknown") or "unknown"),
        "codec": str(row.get("codec", "unknown") or "unknown").lower(),
        "status": str(row.get("status", "ok") or "ok").lower(),
        "psnr": float(row.get("psnr", 0.0) or 0.0),
        "runtime_ms": int(row.get("runtime_ms", 0) or 0),
        "decode_ok": bool(row.get("decode_ok", row.get("status") != "fail")),
        "encode_ok": bool(row.get("encode_ok", True)),
        "regressed": bool(row.get("regressed", False)),
        "partner_visible": bool(row.get("partner_visible", False)),
        "family": str(row.get("family", row.get("codec", "unknown")) or "unknown").lower(),
    }


def classify_codec_blocker(row: Mapping[str, object]) -> str:
    item = normalize_codec_result(row)
    if not item["decode_ok"] or not item["encode_ok"]:
        return "hard-block"
    if str(item["status"]) == "fail":
        return "hard-block"
    if float(item["psnr"]) and float(item["psnr"]) < 33.0:
        return "hard-block"
    if bool(item["regressed"]) and bool(item["partner_visible"]):
        return "lane-block"
    if bool(item["regressed"]) or float(item["psnr"]) < 37.0:
        return "watch"
    return "clear"


def blocker_reason(row: Mapping[str, object]) -> str:
    item = normalize_codec_result(row)
    state = classify_codec_blocker(item)
    if state == "hard-block":
        if not item["decode_ok"]:
            return "decode failure"
        if not item["encode_ok"]:
            return "encode failure"
        if str(item["status"]) == "fail":
            return "explicit fail status"
        return "quality below hard floor"
    if state == "lane-block":
        return "partner-visible regression"
    if state == "watch":
        if bool(item["regressed"]):
            return "regressed compared with baseline"
        return "quality drift below watch floor"
    return "clear"


def codec_family_matrix(rows: Iterable[Mapping[str, object]]) -> dict[str, dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        item = normalize_codec_result(row)
        grouped[str(item["family"])].append(item)
    matrix = {}
    for family, items in sorted(grouped.items()):
        states = [classify_codec_blocker(item) for item in items]
        if "hard-block" in states:
            status = "hard-block"
        elif "lane-block" in states:
            status = "lane-block"
        elif "watch" in states:
            status = "watch"
        else:
            status = "clear"
        matrix[family] = {
            "status": status,
            "codecs": sorted({str(item["codec"]) for item in items}),
            "lanes": sorted({str(item["lane"]) for item in items}),
            "reasons": sorted({blocker_reason(item) for item in items if blocker_reason(item) != "clear"}),
            "partner_visible": any(bool(item["partner_visible"]) for item in items),
        }
    return matrix


def partial_rollout_candidates(rows: Iterable[Mapping[str, object]]) -> list[str]:
    candidates = []
    for family, summary in codec_family_matrix(rows).items():
        if str(summary["status"]) == "clear":
            candidates.append(family)
    return sorted(candidates)


def blocked_families(rows: Iterable[Mapping[str, object]]) -> list[str]:
    return sorted(
        family
        for family, summary in codec_family_matrix(rows).items()
        if str(summary["status"]) in {"hard-block", "lane-block"}
    )


def watch_families(rows: Iterable[Mapping[str, object]]) -> list[str]:
    return sorted(
        family for family, summary in codec_family_matrix(rows).items() if str(summary["status"]) == "watch"
    )


def codec_blocker_summary(rows: Iterable[Mapping[str, object]]) -> dict[str, object]:
    matrix = codec_family_matrix(rows)
    blocked = blocked_families(rows)
    watch = watch_families(rows)
    partial = partial_rollout_candidates(rows)
    issues = [f"codec family blocked: {family}" for family in blocked]
    issues.extend(f"codec family in watch state: {family}" for family in watch)
    status = "block" if blocked else "warn" if watch else "ok"
    return {
        "status": status,
        "severity": status,
        "passed": status != "block",
        "issue_codes": ["codec-blocker"] if issues else [],
        "issues": issues,
        "blocked_families": blocked,
        "watch_families": watch,
        "partial_rollout_candidates": partial,
        "family_matrix": matrix,
    }
