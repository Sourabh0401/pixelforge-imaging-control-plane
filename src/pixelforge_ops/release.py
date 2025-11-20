from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from .catalog import bundle_summary
from .models import ExerciseBundle, ReleaseManifest
from .utils import json_digest, utcnow_text


def build_release_manifest(
    release_id: str,
    bundles: Iterable[ExerciseBundle],
    notes: Iterable[str] = (),
    created_at: str | None = None,
) -> ReleaseManifest:
    bundle_list = sorted(bundles, key=lambda bundle: bundle.bundle_id)
    stats = {bundle.bundle_id: bundle_summary(bundle) for bundle in bundle_list}
    payload = {
        "release_id": release_id,
        "created_at": created_at or utcnow_text(),
        "bundle_ids": [bundle.bundle_id for bundle in bundle_list],
        "bundle_stats": stats,
        "notes": list(notes),
    }
    digest = json_digest(payload)
    return ReleaseManifest(
        release_id=release_id,
        created_at=payload["created_at"],
        bundle_ids=tuple(payload["bundle_ids"]),
        bundle_stats=payload["bundle_stats"],
        digest=digest,
        notes=tuple(payload["notes"]),
    )


def manifest_to_dict(manifest: ReleaseManifest) -> dict[str, object]:
    return {
        "release_id": manifest.release_id,
        "created_at": manifest.created_at,
        "bundle_ids": list(manifest.bundle_ids),
        "bundle_stats": manifest.bundle_stats,
        "digest": manifest.digest,
        "notes": list(manifest.notes),
    }


def release_delta(previous: ReleaseManifest, current: ReleaseManifest) -> dict[str, object]:
    before = set(previous.bundle_ids)
    after = set(current.bundle_ids)
    return {
        "added": sorted(after - before),
        "removed": sorted(before - after),
        "digest_changed": previous.digest != current.digest,
    }
