from __future__ import annotations

import io
import json
import zipfile
from dataclasses import asdict
from pathlib import Path

from .execution import run_to_dict
from .models import ExerciseBundle, ReleaseManifest, Scorecard, SubmissionRun
from .release import manifest_to_dict
from .scoring import scorecard_to_dict
from .utils import json_digest, stable_json


FIXED_TIMESTAMP = (2020, 1, 1, 0, 0, 0)


def build_audit_packet(
    bundle: ExerciseBundle,
    run: SubmissionRun,
    scorecard: Scorecard,
    manifest: ReleaseManifest,
    imaging_review: dict[str, object] | None = None,
) -> dict[str, object]:
    packet = {
        "bundle": {
            "bundle_id": bundle.bundle_id,
            "owner": bundle.owner,
            "version": bundle.version,
            "title": bundle.title,
        },
        "run": run_to_dict(run),
        "scorecard": scorecard_to_dict(scorecard),
        "release_manifest": manifest_to_dict(manifest),
    }
    if imaging_review:
        packet["imaging_review"] = dict(imaging_review)
    packet["digest"] = json_digest(packet)
    return packet


def audit_zip_bytes(packet: dict[str, object]) -> bytes:
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        manifest = {
            "files": [
                {"path": "audit_packet.json", "sha256": json_digest(packet)},
            ],
            "digest": json_digest(packet),
        }
        for name, payload in {
            "audit_packet.json": stable_json(packet),
            "manifest.json": stable_json(manifest),
        }.items():
            info = zipfile.ZipInfo(name, FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, payload)
    return mem.getvalue()


def write_audit_zip(path: Path, packet: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(audit_zip_bytes(packet))
