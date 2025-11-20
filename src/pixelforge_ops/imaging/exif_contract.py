from __future__ import annotations

from typing import Mapping, Sequence


def validate_exif_metadata(
    metadata: Mapping[str, object],
    required_fields: Sequence[str],
    forbidden_fields: Sequence[str] = (),
    numeric_ranges: Mapping[str, Mapping[str, float]] | None = None,
) -> list[str]:
    issues: list[str] = []
    for field in required_fields:
        value = metadata.get(field)
        if value in {None, ""}:
            issues.append(f"missing required field {field}")
    for field in forbidden_fields:
        if field in metadata and metadata.get(field) not in {None, ""}:
            issues.append(f"field {field} must not be present")
    for field, bounds in (numeric_ranges or {}).items():
        if field not in metadata:
            continue
        try:
            value = float(metadata[field])
        except (TypeError, ValueError):
            issues.append(f"field {field} is not numeric")
            continue
        minimum = float(bounds.get("min", value))
        maximum = float(bounds.get("max", value))
        if value < minimum or value > maximum:
            issues.append(f"field {field} outside range {minimum}..{maximum}")
    return issues


def exif_summary(
    metadata: Mapping[str, object],
    required_fields: Sequence[str],
    forbidden_fields: Sequence[str] = (),
    numeric_ranges: Mapping[str, Mapping[str, float]] | None = None,
) -> dict[str, object]:
    issues = validate_exif_metadata(
        metadata,
        required_fields=required_fields,
        forbidden_fields=forbidden_fields,
        numeric_ranges=numeric_ranges,
    )
    return {
        "passed": not issues,
        "field_count": len(metadata),
        "issues": issues,
        "present_fields": sorted(str(field) for field in metadata.keys()),
    }
