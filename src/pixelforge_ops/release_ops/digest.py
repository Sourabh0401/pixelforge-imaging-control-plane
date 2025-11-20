from __future__ import annotations

import hashlib
import json


def manifest_digest(payload: dict[str, object]) -> str:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_release_id(channel: str, train_id: str, ordinal: int) -> str:
    return f"{channel}-{train_id}-{ordinal:03d}"


def digest_label(digest: str) -> str:
    return digest[:12]
