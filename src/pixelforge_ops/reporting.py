from __future__ import annotations

import csv
import io
from typing import Iterable

from .models import Scorecard


def scorecard_markdown(scorecard: Scorecard) -> str:
    lines = [
        f"# Scorecard: {scorecard.bundle_id}",
        "",
        f"- run: `{scorecard.run_id}`",
        f"- owner: `{scorecard.owner}`",
        f"- percent: `{scorecard.percent:.2f}`",
        f"- band: `{scorecard.band}`",
        f"- public percent: `{scorecard.public_percent:.2f}`",
        f"- hidden percent: `{scorecard.hidden_percent:.2f}`",
        "",
        "## Section totals",
        "",
        "| Section | Earned | Possible | Percent |",
        "| --- | ---: | ---: | ---: |",
    ]
    for section, bucket in scorecard.section_totals.items():
        lines.append(
            f"| {section} | {bucket['earned']:.2f} | {bucket['possible']:.2f} | {bucket['percent']:.2f} |"
        )
    if scorecard.policy_flags:
        lines.extend(["", "## Policy flags", ""])
        for flag in scorecard.policy_flags:
            lines.append(f"- {flag}")
    return "\n".join(lines) + "\n"


def scorecards_csv(scorecards: Iterable[Scorecard]) -> str:
    out = io.StringIO()
    writer = csv.DictWriter(
        out,
        fieldnames=["run_id", "bundle_id", "owner", "percent", "band", "public_percent", "hidden_percent", "policy_flags"],
        lineterminator="\n",
    )
    writer.writeheader()
    for scorecard in scorecards:
        writer.writerow(
            {
                "run_id": scorecard.run_id,
                "bundle_id": scorecard.bundle_id,
                "owner": scorecard.owner,
                "percent": f"{scorecard.percent:.2f}",
                "band": scorecard.band,
                "public_percent": f"{scorecard.public_percent:.2f}",
                "hidden_percent": f"{scorecard.hidden_percent:.2f}",
                "policy_flags": ",".join(scorecard.policy_flags),
            }
        )
    return out.getvalue()


def remediation_markdown(items: Iterable[dict[str, object]]) -> str:
    rows = list(items)
    lines = ["# Remediation queue", ""]
    for item in rows:
        lines.append(
            f"- `{item['bundle_id']}` for `{item['owner']}`: {item['reason']} ({item['percent']:.2f}%)"
        )
    if not rows:
        lines.append("- no items")
    return "\n".join(lines) + "\n"
