from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping


def summarize_codec_rows(rows: Iterable[Mapping[str, object]]) -> dict[str, dict[str, float | int]]:
    summary: dict[str, dict[str, float | int]] = {}
    grouped: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("codec", "unknown"))].append(row)
    for codec, items in sorted(grouped.items()):
        passes = sum(1 for row in items if row.get("status") == "pass")
        regressions = sum(1 for row in items if bool(row.get("regressed")) or row.get("status") == "fail")
        psnr_values = [float(row["psnr"]) for row in items if row.get("psnr") is not None]
        runtime_values = [int(row["runtime_ms"]) for row in items if row.get("runtime_ms") is not None]
        summary[codec] = {
            "rows": len(items),
            "passes": passes,
            "regressions": regressions,
            "pass_rate": round(passes / max(len(items), 1), 4),
            "average_psnr": round(sum(psnr_values) / max(len(psnr_values), 1), 4) if psnr_values else 0.0,
            "max_runtime_ms": max(runtime_values, default=0),
        }
    return summary


def regression_codecs(summary: Mapping[str, Mapping[str, float | int]]) -> list[str]:
    return sorted(codec for codec, row in summary.items() if int(row.get("regressions", 0)) > 0)


def best_codec(summary: Mapping[str, Mapping[str, float | int]]) -> str | None:
    if not summary:
        return None
    return sorted(
        summary,
        key=lambda codec: (
            -float(summary[codec].get("pass_rate", 0.0)),
            -float(summary[codec].get("average_psnr", 0.0)),
            int(summary[codec].get("max_runtime_ms", 0)),
            codec,
        ),
    )[0]
