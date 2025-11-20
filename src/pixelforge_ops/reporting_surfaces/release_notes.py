from __future__ import annotations

from pixelforge_ops.models import ReleaseManifest, Scorecard


def release_notes(manifest: ReleaseManifest, scorecards: list[Scorecard]) -> str:
    lines = [f"# Release notes: {manifest.release_id}", "", f"- created at: {manifest.created_at}", ""]
    lines.append("## Bundles")
    lines.append("")
    for scorecard in scorecards:
        lines.append(f"- `{scorecard.bundle_id}` for `{scorecard.owner}` finished in `{scorecard.band}` at `{scorecard.percent:.2f}%`.")
    if manifest.notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in manifest.notes)
    return "\n".join(lines) + "\n"


