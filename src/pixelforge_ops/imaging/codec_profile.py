from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping, Sequence

from .lane_contracts import required_codecs_for_lane


def normalize_codec_row(row: Mapping[str, object]) -> dict[str, object]:
    return {
        "codec": str(row.get("codec", "unknown") or "unknown").lower(),
        "lane": str(row.get("lane", "default") or "default"),
        "status": str(row.get("status", "pass") or "pass").lower(),
        "psnr": float(row.get("psnr", 0.0) or 0.0),
        "ssim": float(row.get("ssim", 0.0) or 0.0),
        "runtime_ms": int(row.get("runtime_ms", 0) or 0),
        "bytes": int(row.get("bytes", row.get("size_bytes", 0)) or 0),
        "alpha_ok": bool(row.get("alpha_ok", True)),
        "decode_ok": bool(row.get("decode_ok", True)),
        "encode_ok": bool(row.get("encode_ok", True)),
        "regressed": bool(row.get("regressed", False)),
    }


def normalized_codec_rows(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    items = [normalize_codec_row(row) for row in rows]
    items.sort(key=lambda row: (str(row["lane"]), str(row["codec"]), int(row["runtime_ms"])))
    return items


def codec_health(row: Mapping[str, object]) -> str:
    item = normalize_codec_row(row)
    if not item["decode_ok"] or not item["encode_ok"] or item["status"] == "fail":
        return "block"
    if item["regressed"] or not item["alpha_ok"] or item["psnr"] < 35.0 or item["ssim"] < 0.94:
        return "warn"
    return "ok"


def compatibility_matrix(rows: Iterable[Mapping[str, object]]) -> dict[str, dict[str, str]]:
    matrix: dict[str, dict[str, str]] = defaultdict(dict)
    for row in normalized_codec_rows(rows):
        matrix[str(row["lane"])][str(row["codec"])] = codec_health(row)
    return {lane: dict(sorted(codecs.items())) for lane, codecs in sorted(matrix.items())}


def lane_codec_decision(rows: Iterable[Mapping[str, object]], lane: str) -> dict[str, object]:
    items = [row for row in normalized_codec_rows(rows) if str(row["lane"]) == lane]
    by_codec: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in items:
        by_codec[str(row["codec"])].append(row)
    issues: list[str] = []
    summary: dict[str, dict[str, object]] = {}
    for codec, codec_rows in sorted(by_codec.items()):
        statuses = [codec_health(row) for row in codec_rows]
        worst = "block" if "block" in statuses else "warn" if "warn" in statuses else "ok"
        summary[codec] = {
            "status": worst,
            "rows": len(codec_rows),
            "best_psnr": round(max(float(row["psnr"]) for row in codec_rows), 4),
            "worst_runtime_ms": max(int(row["runtime_ms"]) for row in codec_rows),
        }
        if worst != "ok":
            issues.append(f"{codec} marked {worst} for lane {lane}")
    for codec in required_codecs_for_lane(lane):
        if codec not in summary:
            issues.append(f"required codec missing for lane {lane}: {codec}")
    status = "block" if any("block" in issue or "missing" in issue for issue in issues) else "warn" if issues else "ok"
    return {
        "lane": lane,
        "status": status,
        "severity": status,
        "issue_codes": ["codec-profile"] if issues else [],
        "issues": issues,
        "codecs": summary,
        "required_codecs": list(required_codecs_for_lane(lane)),
        "passed": status != "block",
    }


def codec_profile_summary(rows: Iterable[Mapping[str, object]]) -> dict[str, object]:
    matrix = compatibility_matrix(rows)
    issues: list[str] = []
    lane_summaries: dict[str, dict[str, object]] = {}
    for lane in matrix:
        lane_summary = lane_codec_decision(rows, lane)
        lane_summaries[lane] = lane_summary
        issues.extend(lane_summary["issues"])
    blocked_codecs = sorted(
        {
            codec
            for lane_summary in lane_summaries.values()
            for codec, details in dict(lane_summary["codecs"]).items()
            if str(details["status"]) == "block"
        }
    )
    warned_codecs = sorted(
        {
            codec
            for lane_summary in lane_summaries.values()
            for codec, details in dict(lane_summary["codecs"]).items()
            if str(details["status"]) == "warn"
        }
    )
    status = "block" if blocked_codecs else "warn" if warned_codecs or issues else "ok"
    return {
        "passed": status != "block",
        "status": status,
        "severity": status,
        "issue_codes": ["codec-profile"] if issues else [],
        "issues": sorted(dict.fromkeys(issues)),
        "blocked_codecs": blocked_codecs,
        "warned_codecs": warned_codecs,
        "lane_summaries": lane_summaries,
        "compatibility_matrix": matrix,
    }

