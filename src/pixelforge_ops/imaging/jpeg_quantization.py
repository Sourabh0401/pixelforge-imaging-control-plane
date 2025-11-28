from __future__ import annotations

from typing import Sequence


def normalize_quant_table(table: Sequence[int | float]) -> list[int]:
    return [max(0, min(255, int(round(float(value))))) for value in table]


def quantization_summary(table: Sequence[int | float], max_average: float = 90.0, max_peak: int = 180) -> dict[str, object]:
    values = normalize_quant_table(table)
    average = round(sum(values) / max(len(values), 1), 6)
    peak = max(values, default=0)
    issues = []
    if average > max_average:
        issues.append("quantization average exceeded threshold")
    if peak > max_peak:
        issues.append("quantization peak exceeded threshold")
    status = "block" if issues else "ok"
    return {
        "passed": not issues,
        "status": status,
        "severity": status,
        "issue_codes": ["jpeg-quantization"] if issues else [],
        "issues": issues,
        "average": average,
        "peak": peak,
        "table_length": len(values),
    }

