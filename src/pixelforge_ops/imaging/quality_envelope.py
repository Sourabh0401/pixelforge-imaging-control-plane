from __future__ import annotations

"""
Compare current lane signals against saved baseline envelopes.

Threshold profiles answer “what should block or warn right now?”  Baseline
envelopes answer “is this result still shaped like the last accepted release?”
That distinction matters because a lane can pass its explicit gate while still
moving in a direction operators want to monitor.
"""

from typing import Mapping

from .threshold_profiles import comparator_thresholds, sampling_policy


def _float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def histogram_envelope_check(lane: str, histogram: Mapping[str, object]) -> dict[str, object]:
    contract = comparator_thresholds(lane, "channel_histogram")
    max_delta = _float(histogram.get("max_delta"))
    warn_delta = max(_float(contract.get("warn_threshold", 0.02)) * 0.75, 0.001)
    block_delta = max(_float(contract.get("block_threshold", 0.06)) * 0.75, warn_delta)
    status = "block" if max_delta >= block_delta else "warn" if max_delta >= warn_delta else "ok"
    return {
        "status": status,
        "metric": "histogram",
        "observed": round(max_delta, 6),
        "warn_limit": round(warn_delta, 6),
        "block_limit": round(block_delta, 6),
    }


def color_envelope_check(lane: str, color_delta: Mapping[str, object]) -> dict[str, object]:
    contract = comparator_thresholds(lane, "color_delta")
    observed_mean = _float(color_delta.get("mean_delta"))
    observed_p95 = _float(color_delta.get("p95_delta"))
    warn_mean = max(_float(contract.get("warn_threshold", 6.0)) * 0.8, 0.1)
    block_mean = max(_float(contract.get("block_threshold", 18.0)) * 0.8, warn_mean)
    warn_p95 = max(_float(contract.get("percentile_threshold", 12.0)) * 0.8, warn_mean)
    block_p95 = max(warn_p95 * 1.5, block_mean)
    block = observed_mean >= block_mean or observed_p95 >= block_p95
    warn = observed_mean >= warn_mean or observed_p95 >= warn_p95
    return {
        "status": "block" if block else "warn" if warn else "ok",
        "metric": "color_delta",
        "observed_mean": round(observed_mean, 6),
        "observed_p95": round(observed_p95, 6),
        "warn_mean": round(warn_mean, 6),
        "block_mean": round(block_mean, 6),
        "warn_p95": round(warn_p95, 6),
        "block_p95": round(block_p95, 6),
    }


def region_envelope_check(lane: str, region_summary: Mapping[str, object]) -> dict[str, object]:
    policy = sampling_policy(lane)
    required_regions = set(str(value) for value in policy.get("required_regions", []))
    observed_issues = [str(value) for value in region_summary.get("issues", [])]
    blocking = any("required" in issue or "missing" in issue for issue in observed_issues)
    watch = bool(observed_issues)
    return {
        "status": "block" if blocking else "warn" if watch else "ok",
        "metric": "region_diff",
        "required_regions": sorted(required_regions),
        "issue_count": len(observed_issues),
        "issues": observed_issues,
    }


def manifest_envelope_check(manifest_summary: Mapping[str, object], consistency_summary: Mapping[str, object] | None = None) -> dict[str, object]:
    issues = [str(value) for value in manifest_summary.get("issues", [])]
    if consistency_summary is not None:
        issues.extend(str(value) for value in consistency_summary.get("issues", []))
    blocking = any("digest" in issue or "missing" in issue or "contract" in issue for issue in issues)
    return {
        "status": "block" if blocking else "warn" if issues else "ok",
        "metric": "manifest",
        "issue_count": len(issues),
        "issues": sorted(dict.fromkeys(issues)),
    }


def quality_envelope_summary(
    lane: str,
    histogram: Mapping[str, object],
    color_delta: Mapping[str, object],
    region_summary: Mapping[str, object],
    manifest_summary: Mapping[str, object],
    consistency_summary: Mapping[str, object] | None = None,
) -> dict[str, object]:
    checks = [
        histogram_envelope_check(lane, histogram),
        color_envelope_check(lane, color_delta),
        region_envelope_check(lane, region_summary),
        manifest_envelope_check(manifest_summary, consistency_summary=consistency_summary),
    ]
    statuses = [str(check["status"]) for check in checks]
    status = "block" if "block" in statuses else "warn" if "warn" in statuses else "ok"
    return {
        "status": status,
        "severity": status,
        "passed": status != "block",
        "issue_codes": ["quality-envelope"] if status != "ok" else [],
        "issues": [f"{check['metric']} envelope status: {check['status']}" for check in checks if check["status"] != "ok"],
        "checks": checks,
    }
