from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DIR = ROOT / "src" / "pixelforge_ops" / "imaging" / "reference"
TEMPLATE_DIR = ROOT / "src" / "pixelforge_ops" / "imaging" / "templates"


LANES = [
    {
        "lane": "jpeg-codec-fidelity",
        "owner": "codec-ops",
        "channel": "internal",
        "family": "codec",
        "codecs": ["jpeg", "webp"],
        "metadata": ["width", "height", "color_profile", "orientation", "capture_timestamp"],
        "playbook": "Focus on ringing, quantization-table churn, and whether the visible drift is isolated to the JPEG lane.",
    },
    {
        "lane": "raster-transform-tiling",
        "owner": "raster-ops",
        "channel": "internal",
        "family": "tiling",
        "codecs": ["png", "webp"],
        "metadata": ["width", "height", "color_profile", "tile_origin", "transform_chain"],
        "playbook": "Check missing tiles, overlap, and seam drift before asking the renderer team for a replay.",
    },
    {
        "lane": "metadata-exif-ingest",
        "owner": "metadata-ops",
        "channel": "internal",
        "family": "metadata",
        "codecs": ["jpeg"],
        "metadata": ["width", "height", "color_profile", "camera_model", "orientation", "capture_timestamp", "lens_model"],
        "playbook": "Treat metadata loss as a first-class release problem because partner and archive tooling depend on it.",
    },
    {
        "lane": "color-profile-parity",
        "owner": "color-ops",
        "channel": "internal",
        "family": "color",
        "codecs": ["png", "avif"],
        "metadata": ["width", "height", "color_profile", "icc_profile", "transfer_function", "gamut"],
        "playbook": "Look at channel histograms, profile embedding, and required-region drift together instead of chasing one metric in isolation.",
    },
    {
        "lane": "alpha-channel-recovery",
        "owner": "alpha-ops",
        "channel": "internal",
        "family": "alpha",
        "codecs": ["png", "webp"],
        "metadata": ["width", "height", "alpha_mode", "color_profile"],
        "playbook": "Alpha regressions hide in premultiplication and halo behavior, so the brief should keep those findings separate from RGB drift.",
    },
    {
        "lane": "thumbnail-generation-stability",
        "owner": "thumbnail-ops",
        "channel": "pilot",
        "family": "thumbnail",
        "codecs": ["jpeg", "webp", "avif"],
        "metadata": ["width", "height", "crop_mode", "target_aspect_ratio", "color_profile"],
        "playbook": "Thumbnail work has real budget pressure, so include render size, runtime, and cache-key impact in every handoff.",
    },
    {
        "lane": "partner-format-compatibility",
        "owner": "partner-ops",
        "channel": "partner",
        "family": "partner",
        "codecs": ["png", "webp"],
        "metadata": ["width", "height", "color_profile", "delivery_profile", "icc_profile", "partner_contract"],
        "playbook": "Partner lanes are unforgiving. Missing metadata or sidecars should block even when the pixels still look clean.",
    },
    {
        "lane": "export-pipeline-integrity",
        "owner": "export-ops",
        "channel": "partner",
        "family": "export",
        "codecs": ["png", "jpeg", "webp"],
        "metadata": ["width", "height", "color_profile", "delivery_profile", "archive_group"],
        "playbook": "This lane proves the packaging path, so operators need file lists, checksums, and routing notes as much as image summaries.",
    },
    {
        "lane": "compression-preset-handoff",
        "owner": "compression-ops",
        "channel": "internal",
        "family": "compression",
        "codecs": ["jpeg", "avif"],
        "metadata": ["width", "height", "color_profile", "preset_name", "quality_level"],
        "playbook": "Preset changes can move quality without code motion. Keep the preset rationale next to the render evidence.",
    },
    {
        "lane": "sprite-identity-refresh",
        "owner": "sprite-ops",
        "channel": "pilot",
        "family": "sprite",
        "codecs": ["png", "webp"],
        "metadata": ["width", "height", "alpha_mode", "sprite_origin", "color_profile"],
        "playbook": "Sprite lanes care about atlas completeness, alpha integrity, and deterministic names because clients patch these incrementally.",
    },
    {
        "lane": "decoder-recovery-replay",
        "owner": "replay-ops",
        "channel": "pilot",
        "family": "replay",
        "codecs": ["jpeg", "png"],
        "metadata": ["width", "height", "color_profile", "decoder_build", "capture_timestamp"],
        "playbook": "Replay lanes should preserve manifest digest and issue codes so incident debugging stays deterministic across shifts.",
    },
    {
        "lane": "batch-render-telemetry",
        "owner": "telemetry-ops",
        "channel": "pilot",
        "family": "telemetry",
        "codecs": ["jpeg", "png"],
        "metadata": ["width", "height", "render_host", "render_job", "color_profile"],
        "playbook": "Telemetry is where budget drift gets spotted early, so every packet should carry enough context to explain the budget change.",
    },
]


ISSUES = [
    ("histogram-drift", "color-drift", "warn", "color-ops"),
    ("color-delta", "color-drift", "warn", "color-ops"),
    ("region-diff", "visual-integrity", "block", "raster-ops"),
    ("tile-coverage", "tile-topology", "block", "raster-ops"),
    ("render-manifest", "artifact-contract", "block", "release-ops"),
    ("metadata-policy", "metadata", "block", "metadata-ops"),
    ("codec-profile", "codec-health", "block", "codec-ops"),
    ("transparency-halo", "alpha-quality", "warn", "alpha-ops"),
    ("jpeg-quantization", "codec-health", "warn", "codec-ops"),
    ("render-budget", "runtime-budget", "warn", "telemetry-ops"),
    ("partner-export", "partner-delivery", "block", "partner-ops"),
    ("operator-note", "operator-guidance", "info", "release-ops"),
    ("artifact-lineage", "artifact-contract", "warn", "release-ops"),
    ("manifest-exception", "artifact-contract", "warn", "release-ops"),
    ("baseline-envelope", "baseline-analysis", "warn", "replay-ops"),
    ("release-queue", "release-coordination", "info", "release-ops"),
]


def _write_json(name: str, payload: object) -> None:
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    (REFERENCE_DIR / name).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_threshold_profiles() -> dict[str, object]:
    profiles = []
    for index, lane in enumerate(LANES, start=1):
        profiles.append(
            {
                "lane": lane["lane"],
                "owner_group": lane["owner"],
                "release_channel": lane["channel"],
                "comparators": {
                    "pixel_matrix": {"tolerance": 0 if lane["family"] == "alpha" else 2, "max_mismatched_pixels": 0 if lane["family"] == "alpha" else 8},
                    "channel_histogram": {"bins": 16, "warn_threshold": 0.01 if lane["family"] == "color" else 0.025, "block_threshold": 0.03 if lane["family"] == "color" else 0.07},
                    "color_delta": {"warn_threshold": 3.0 if lane["family"] == "color" else 6.0, "block_threshold": 9.0 if lane["family"] == "color" else 18.0},
                    "region_diff": {"required_regions": ["hero-frame", "text-overlay"], "ignore_regions": ["debug-overlay", "operator-watermark"]},
                    "render_manifest": {"required_codecs": lane["codecs"], "strict_digest": True},
                    "image_release_gate": {"blocker_codes": ["metadata-policy", "tile-coverage", "render-manifest", "codec-profile"]},
                },
                "sampling": {
                    "grid": "edge_and_center" if lane["family"] in {"tiling", "thumbnail", "sprite"} else "center_weighted",
                    "required_regions": ["hero-frame", "text-overlay"] if lane["family"] != "metadata" else ["hero-frame"],
                    "ignore_regions": ["debug-overlay", "render-stamp"],
                    "points_per_edge": 12 if lane["family"] in {"tiling", "thumbnail"} else 8,
                },
                "render_budget": {
                    "max_runtime_ms": 1400 + index * 100,
                    "warn_runtime_ms": 1100 + index * 90,
                    "max_bytes": 4_000_000 + index * 450_000,
                    "max_tiles": 12 if lane["family"] in {"tiling", "thumbnail", "sprite"} else 4,
                },
                "metadata": {
                    "required_fields": lane["metadata"],
                    "allowed_profiles": ["sRGB", "Display P3", "Rec.709"],
                    "allowed_gamuts": ["srgb", "p3"],
                    "forbidden_fields": ["debug_profile", "internal_probe"],
                },
                "watch_signals": ["histogram-drift", "color-delta", "transparency-halo", "jpeg-quantization"],
                "release_blockers": ["metadata-policy", "render-manifest", "codec-profile"] + (["tile-coverage"] if lane["family"] in {"tiling", "thumbnail", "sprite"} else []),
                "notes": [
                    lane["playbook"],
                    "Operators should compare lane-level digests and issue summaries before escalating to another team.",
                    "Partial rollouts are acceptable only when the unaffected codec family and partner packet stay explicitly green.",
                ],
            }
        )
    return {"profiles": profiles}


def build_issue_taxonomy() -> dict[str, object]:
    return {
        "issues": [
            {
                "code": code,
                "family": family,
                "default_severity": severity,
                "owner_group": owner,
                "summary": f"{code.replace('-', ' ')} finding for imaging release control.",
                "operator_action": f"Inspect the {family} evidence, compare it against the accepted packet, and route follow-up to {owner}.",
                "related_modules": ["image_release_gate", "quality_report", "operator_guidance"],
            }
            for code, family, severity, owner in ISSUES
        ]
    }


def build_partner_profiles() -> dict[str, object]:
    partners = [
        ("partner-retail-eu", "EU retail storefront exports with strict ICC handling and manifest stability checks."),
        ("partner-marketplace-us", "Marketplace exports with PNG fallback requirements and weekly compliance spot checks."),
        ("partner-social-preview", "Preview images for social surfaces where thumbnail dimensions and cache keys matter."),
        ("partner-archive-backfill", "Archive backfill jobs that care about deterministic packets and metadata completeness."),
    ]
    profiles = []
    for partner, description in partners:
        for lane in LANES:
            profiles.append(
                {
                    "partner": partner,
                    "lane": lane["lane"],
                    "description": description,
                    "required_files": ["render.json", "quality.md", "issues.json"] + (["tiles.csv"] if lane["family"] in {"tiling", "thumbnail", "sprite"} else ["image.bin"]),
                    "required_codecs": lane["codecs"],
                    "required_metadata": lane["metadata"][:5],
                    "allow_alpha": lane["family"] in {"alpha", "sprite"},
                    "strict_manifest_digest": lane["channel"] == "partner" or partner.endswith("backfill"),
                    "routing": {
                        "owner_group": lane["owner"],
                        "support_group": "support-ops",
                        "release_group": "release-ops",
                    },
                    "notes": [
                        f"{partner} expects deterministic outputs for {lane['lane']}.",
                        "If a required file or codec is missing, the export should block rather than silently fallback.",
                        "Partner packets should preserve lane-specific decisions so a healthy codec family stays visible during partial approval.",
                    ],
                }
            )
    return {"profiles": profiles}


def build_rollout_policies() -> dict[str, object]:
    policies = []
    for lane in LANES:
        for codec in sorted(set(lane["codecs"] + ["jpeg", "png", "webp", "avif"])):
            policies.append(
                {
                    "lane": lane["lane"],
                    "codec": codec,
                    "release_channel": lane["channel"],
                    "allow_partial_rollout": codec in lane["codecs"] and lane["channel"] != "partner",
                    "canary_percent": 10 if lane["channel"] == "partner" else 20 if lane["channel"] == "pilot" else 35,
                    "hard_block_on_decode_failure": True,
                    "psnr_watch_floor": 37.0 if codec in {"jpeg", "webp"} else 35.0,
                    "psnr_block_floor": 33.0 if codec in {"jpeg", "webp"} else 31.0,
                    "max_warn_runtime_ms": 1800 if codec == "avif" else 1500,
                    "max_block_runtime_ms": 2500 if codec == "avif" else 2100,
                    "notes": [
                        f"{codec.upper()} rollout in {lane['lane']} should preserve independent lane decisions.",
                        "Partner lanes use smaller canary windows because export mistakes take longer to unwind once they land.",
                    ],
                }
            )
    return {"policies": policies}


def build_manifest_exception_policies() -> dict[str, object]:
    policies = []
    for lane in LANES:
        policies.append(
            {
                "lane": lane["lane"],
                "allowed_issue_codes": ["manifest-exception", "artifact-lineage", "render-budget"] if lane["channel"] != "partner" else ["manifest-exception", "artifact-lineage"],
                "blocked_issue_codes": ["partner-export", "metadata-policy", "tile-coverage"] + (["codec-profile"] if lane["channel"] == "partner" else []),
                "allowed_missing_codecs": ["avif"] if "avif" not in lane["codecs"] else [],
                "allowed_missing_metadata": ["lens_model", "render_host"] if lane["channel"] != "partner" else ["lens_model"],
                "expiry_classes": {
                    "same_shift": ["artifact-lineage"],
                    "two_day": ["render-budget", "manifest-exception"],
                    "weekly": ["operator-note"],
                },
                "notes": [
                    f"Exceptions for {lane['lane']} exist for paperwork and routing, not to hide a visual regression.",
                    "If an exception downgrades a blocker, the packet should record the expiry class and accepting owner group.",
                ],
            }
        )
    return {"policies": policies}


def build_release_questionnaires() -> dict[str, object]:
    questionnaires = []
    for lane in LANES:
        questionnaires.append(
            {
                "lane": lane["lane"],
                "title": f"{lane['lane'].replace('-', ' ').title()} operator questionnaire",
                "questions": [
                    "Which artifact digest changed, and was the change expected for this release note?",
                    "Did a required region move from ok to warn or block, and which comparator saw it first?",
                    "Are partner-export requirements still satisfied for every required codec family?",
                    "If only one codec family failed, is a lane-limited rollout acceptable under current policy?",
                    "What should the next shift inspect first if the same lane pages again after rollout begins?",
                ],
                "handoff_template": [
                    "Current lane status:",
                    "Primary blocker or watch code:",
                    "Packet digest and manifest comparison:",
                    "Open follow-up with owner group:",
                    "Safe next action for the release owner:",
                ],
            }
        )
    return {"questionnaires": questionnaires}


def build_lane_templates() -> None:
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    (TEMPLATE_DIR / "__init__.py").write_text('"""Lane-specific operator templates for PixelForge imaging releases."""\n', encoding="utf-8")
    for lane in LANES:
        heading = lane["lane"].replace("-", " ").title()
        sections = [
            f"# {heading} operator template",
            "",
            "## What this lane protects",
            lane["playbook"],
            "",
            "## Signals that matter",
            "- Compare the lane digest, render manifest, and issue digest before you try a rerun.",
            "- Separate lane-specific blockers from broader bundle health so a single codec regression does not hide clean work elsewhere.",
            "- Keep partner-export state explicit. An apparently harmless metadata change can still break downstream validation.",
            "",
            "## First-pass triage",
            f"1. Confirm the active release channel for `{lane['lane']}` is still `{lane['channel']}` and that the packet was built from the expected bundle.",
            "2. Read the machine summary, then pull the human brief. The control plane is supposed to tell the same story in both places.",
            "3. Compare the current packet against the last accepted packet. Check digest drift, changed paths, and any lane-specific warnings.",
            "4. Decide whether the lane is blocked, watch-only, or safe to continue. Write that decision down before you hand work to another team.",
            "",
            "## Required artifacts",
            "- render manifest JSON",
            "- quality report markdown",
            "- operator brief markdown",
            "- issue digest payload",
            "- partner or archive sidecars when the lane feeds an external consumer",
            "",
            "## Questions to answer before unblocking the lane",
            "- Did the drift land in a required region or only a debug or advisory region?",
            "- Did the manifest contract change, or did the packet only reorder artifacts while staying digest-stable?",
            "- Is the regression isolated to one codec family, one partner profile, or one replay path?",
            "- If this lane can move in watch mode, what evidence proves the unaffected lanes are still green?",
            "",
            "## Handoff notes",
            "Write the handoff as if the next person will look at it at 3 AM during an incident. Keep the lane name, digest, issue codes, and safe next action in the first screenful.",
            "",
            "## Escalation map",
            f"- Lane owner group: `{lane['owner']}`",
            "- Release owner group: `release-ops`",
            "- Support owner group: `support-ops`",
            "- Partner owner group: `partner-ops` when an external packet is in play",
            "",
            "## When a warning is still allowed to ship",
            "Warnings can move forward only when the packet records why the warning is safe, the unaffected lanes remain machine-checkable, and the next operator can reproduce the same decision from the brief.",
            "",
            "## Common mistakes",
            "- Treating a lane-level watch signal as a pass without checking whether the same issue becomes a blocker for partner export.",
            "- Re-running the renderer before saving the original manifest digest and issue summary.",
            "- Collapsing multiple codec-family outcomes into one generic decision, which hides healthy lanes and slows down release work.",
            "",
            "## Longer notes",
            f"The `{lane['lane']}` lane exists because image releases fail in different ways depending on codec, metadata, transform ordering, alpha handling, and export policy. This template keeps those branches explicit. For this lane, operators should pay extra attention to {lane['playbook'].lower()}",
            "The goal is not just to say pass or fail. The goal is to leave behind enough structured evidence that the next shift can make the same decision without re-learning the lane from scratch. That is why the control plane carries manifest digests, machine summaries, owner routing, and operator prose together.",
        ]
        _write_text(TEMPLATE_DIR / f"{lane['lane'].replace('-', '_')}.md", "\n".join(sections) + "\n")


def main() -> None:
    _write_json("lane_threshold_profiles.json", build_threshold_profiles())
    _write_json("issue_taxonomy.json", build_issue_taxonomy())
    _write_json("partner_delivery_profiles.json", build_partner_profiles())
    _write_json("codec_rollout_policies.json", build_rollout_policies())
    _write_json("manifest_exception_policies.json", build_manifest_exception_policies())
    _write_json("release_questionnaires.json", build_release_questionnaires())
    _write_text(REFERENCE_DIR / "__init__.py", '"""Reference assets for imaging policy, rollout, and operator guidance."""\n')
    build_lane_templates()


if __name__ == "__main__":
    main()
