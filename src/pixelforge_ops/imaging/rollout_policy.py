from __future__ import annotations

"""
Codec-family rollout policy for imaging lanes.

The release gate decides whether a lane is safe. Rollout policy decides how
that safe or unsafe result maps onto canaries, partial rollouts, and codec
family isolation. The two concerns are related but not interchangeable, so the
repo keeps them separate.
"""

from typing import Iterable, Mapping

from .reference_data import load_reference_data


def _policies() -> list[dict[str, object]]:
    payload = load_reference_data("codec_rollout_policies.json")
    return [dict(row) for row in payload["policies"]]


def codec_rollout_policy(lane: str, codec: str, release_channel: str | None = None) -> dict[str, object]:
    channel = release_channel
    for row in _policies():
        if str(row.get("lane")) != lane:
            continue
        if str(row.get("codec")) != codec:
            continue
        if channel is not None and str(row.get("release_channel")) != channel:
            continue
        return row
    raise KeyError(f"{lane}:{codec}:{release_channel or '*'}")


def evaluate_rollout_row(row: Mapping[str, object], lane: str, release_channel: str) -> dict[str, object]:
    codec = str(row.get("codec", "unknown")).lower()
    policy = codec_rollout_policy(lane, codec, release_channel)
    psnr = float(row.get("psnr", 0.0) or 0.0)
    runtime_ms = int(row.get("runtime_ms", 0) or 0)
    decode_ok = bool(row.get("decode_ok", row.get("status") != "fail"))
    issues = []
    if not decode_ok and bool(policy.get("hard_block_on_decode_failure", True)):
        issues.append("decode failure blocks rollout")
    if psnr < float(policy.get("psnr_block_floor", 0.0)):
        issues.append("psnr below block floor")
    elif psnr < float(policy.get("psnr_watch_floor", 0.0)):
        issues.append("psnr below watch floor")
    if runtime_ms > int(policy.get("max_block_runtime_ms", 0) or 0):
        issues.append("runtime above block budget")
    elif runtime_ms > int(policy.get("max_warn_runtime_ms", 0) or 0):
        issues.append("runtime above watch budget")
    status = "block" if any("block" in issue or "decode" in issue for issue in issues) else "warn" if issues else "ok"
    return {
        "lane": lane,
        "codec": codec,
        "status": status,
        "issues": issues,
        "allow_partial_rollout": bool(policy.get("allow_partial_rollout", False)),
        "canary_percent": int(policy.get("canary_percent", 0) or 0),
    }


def rollout_summary(rows: Iterable[Mapping[str, object]], lane: str, release_channel: str) -> dict[str, object]:
    evaluated = [evaluate_rollout_row(row, lane, release_channel) for row in rows]
    blocked = [row for row in evaluated if row["status"] == "block"]
    warned = [row for row in evaluated if row["status"] == "warn"]
    partial = [row["codec"] for row in evaluated if row["status"] == "block" and row["allow_partial_rollout"]]
    return {
        "passed": not blocked,
        "status": "block" if blocked else "warn" if warned else "ok",
        "blocked_codecs": sorted(str(row["codec"]) for row in blocked),
        "warned_codecs": sorted(str(row["codec"]) for row in warned),
        "partial_rollout_codecs": sorted(partial),
        "rows": evaluated,
    }


def canary_plan(lane: str, codecs: Iterable[str], release_channel: str) -> list[dict[str, object]]:
    rows = []
    for codec in sorted({str(value).lower() for value in codecs}):
        policy = codec_rollout_policy(lane, codec, release_channel)
        rows.append(
            {
                "codec": codec,
                "lane": lane,
                "release_channel": release_channel,
                "canary_percent": int(policy.get("canary_percent", 0) or 0),
                "allow_partial_rollout": bool(policy.get("allow_partial_rollout", False)),
            }
        )
    return rows
