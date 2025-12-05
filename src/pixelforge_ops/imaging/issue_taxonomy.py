from __future__ import annotations

from collections import Counter

from .reference_data import load_reference_data


def _entries() -> list[dict[str, object]]:
    payload = load_reference_data("issue_taxonomy.json")
    return [dict(row) for row in payload["issues"]]


def issue_codes() -> list[str]:
    return sorted(str(row["code"]) for row in _entries())


def taxonomy_entry(code: str) -> dict[str, object]:
    normalized = str(code).strip().lower()
    for row in _entries():
        if str(row["code"]).lower() == normalized:
            return row
    raise KeyError(code)


def issue_family(code: str) -> str:
    return str(taxonomy_entry(code)["family"])


def issue_owner(code: str) -> str:
    return str(taxonomy_entry(code)["owner_group"])


def issue_severity(code: str, status: str | None = None) -> str:
    entry = taxonomy_entry(code)
    base = str(entry["default_severity"])
    if status in {"block", "warn", "ok", "info"}:
        return str(status)
    return base


def related_modules(code: str) -> list[str]:
    return sorted(str(value) for value in taxonomy_entry(code).get("related_modules", []))


def classify_issue_messages(messages: list[str]) -> list[str]:
    results: list[str] = []
    for message in messages:
        text = str(message).lower()
        if "tile" in text:
            results.append("tile-coverage")
        elif "manifest" in text or "digest" in text:
            results.append("render-manifest")
        elif "icc" in text or "exif" in text or "metadata" in text:
            results.append("metadata-policy")
        elif "alpha" in text or "halo" in text:
            results.append("transparency-halo")
        elif "codec" in text or "psnr" in text or "decode" in text:
            results.append("codec-profile")
        elif "histogram" in text:
            results.append("histogram-drift")
        else:
            results.append("operator-note")
    return results


def issue_rollup(codes: list[str]) -> dict[str, object]:
    severity_counts = Counter()
    family_counts = Counter()
    owner_counts = Counter()
    unique_codes = []
    seen = set()
    for code in codes:
        normalized = str(code)
        if normalized in seen:
            continue
        seen.add(normalized)
        unique_codes.append(normalized)
        severity_counts[issue_severity(normalized)] += 1
        family_counts[issue_family(normalized)] += 1
        owner_counts[issue_owner(normalized)] += 1
    return {
        "issue_count": len(unique_codes),
        "codes": sorted(unique_codes),
        "severity_counts": dict(sorted(severity_counts.items())),
        "family_counts": dict(sorted(family_counts.items())),
        "owner_counts": dict(sorted(owner_counts.items())),
    }
