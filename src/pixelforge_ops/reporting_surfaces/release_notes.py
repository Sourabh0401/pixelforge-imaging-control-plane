from __future__ import annotations

from typing import Mapping

from pixelforge_ops.models import ReleaseManifest, Scorecard


def release_notes(
    manifest: ReleaseManifest,
    scorecards: list[Scorecard],
    imaging_reviews: Mapping[str, Mapping[str, object]] | None = None,
) -> str:
    lines = [f"# Release notes: {manifest.release_id}", "", f"- created at: {manifest.created_at}", ""]
    lines.append("## Bundles")
    lines.append("")
    for scorecard in scorecards:
        lines.append(f"- `{scorecard.bundle_id}` for `{scorecard.owner}` finished in `{scorecard.band}` at `{scorecard.percent:.2f}%`.")
        if imaging_reviews and scorecard.bundle_id in imaging_reviews:
            review = imaging_reviews[scorecard.bundle_id]
            lines.append(f"  - imaging gate: `{review.get('status', 'unknown')}` with `{review.get('issue_count', 0)}` issue(s).")
    if manifest.notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in manifest.notes)
    return "\n".join(lines) + "\n"

