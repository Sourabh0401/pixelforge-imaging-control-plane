from __future__ import annotations

from engineering_challenge.utils import json_digest


REPAIR_GUIDES = {
    "bundle": {
        "owner": "content_ops",
        "symptoms": [
            "Packet validation reports missing bundle fields.",
            "Bundle title, owner, or version in the packet does not match the release note.",
            "Audit review asks for authoring context that is not visible in the archive.",
        ],
        "likely_causes": [
            "Bundle metadata changed after the packet payload was assembled.",
            "A compatibility field was dropped while refactoring the export shape.",
            "The wrong bundle root was used during packet generation.",
        ],
        "checks": [
            "Compare packet bundle metadata with `bundle.json` from the same bundle root.",
            "Validate required bundle fields against the audit contract table before re-export.",
            "Confirm the release note excerpt references the same bundle version as the packet.",
        ],
        "repairs": [
            "Rebuild the packet from the correct bundle root.",
            "Restore required metadata fields before export.",
            "Update release notes only if the catalog metadata was actually intended to change.",
        ],
    },
    "run": {
        "owner": "platform_ops",
        "symptoms": [
            "Run rows are missing required contract fields.",
            "Case-level replay in the packet cannot be matched to the original attempt.",
            "Timestamps or runtime values look inconsistent with the stored history row.",
        ],
        "likely_causes": [
            "The CLI exported a simplified run payload instead of the full run dictionary.",
            "A retry or rerun replaced the packet payload without replacing the trace rows.",
            "Run normalization changed but the audit writer did not pick up the new fields.",
        ],
        "checks": [
            "Compare `run_to_dict` output with the packet run payload.",
            "Check that the run id matches the artifact path prefix and the trace rows.",
            "Compare runtime totals with the execution transcript when timeouts are involved.",
        ],
        "repairs": [
            "Rebuild the packet from a fresh `SubmissionRun` payload.",
            "Regenerate trace rows from the same run object.",
            "Update any packet-writing helper that strips fields needed by the contract.",
        ],
    },
    "scorecard": {
        "owner": "finance_ops",
        "symptoms": [
            "Public or hidden percentages are missing from the packet.",
            "Policy flags in the packet do not match the latest scorecard.",
            "A release decision cannot be explained from the archived scorecard alone.",
        ],
        "likely_causes": [
            "The scorecard payload was rebuilt from a different run than the trace rows.",
            "Score serialization omitted policy flags or section totals.",
            "A helper collapsed the visibility split before writing the packet.",
        ],
        "checks": [
            "Compare `scorecard_to_dict` output with the packet scorecard payload.",
            "Verify public and hidden percentages against the current scorecard object.",
            "Confirm the policy flag set still matches release-readiness expectations.",
        ],
        "repairs": [
            "Recompute the scorecard from the archived run.",
            "Restore section totals and policy flags to the serialized payload.",
            "Re-export the packet only after the scorecard payload is structurally complete.",
        ],
    },
    "release_manifest": {
        "owner": "release_ops",
        "symptoms": [
            "Manifest digest mismatch during packet validation.",
            "Bundle membership in the packet differs from the expected release train membership.",
            "Release-note context exists but the manifest digest still changed unexpectedly.",
        ],
        "likely_causes": [
            "The manifest was rebuilt after the packet was assembled.",
            "Notes or bundle stats changed without a coordinated packet rebuild.",
            "The packet used a manifest from another release id.",
        ],
        "checks": [
            "Recompute the manifest digest from the manifest payload without the digest field.",
            "Compare bundle ids and stats with the current manifest source.",
            "Confirm the release id, created-at timestamp, and notes are from the same export pass.",
        ],
        "repairs": [
            "Use a single manifest source when building the packet.",
            "Regenerate packet and manifest together if the release note or bundle list changed.",
            "Treat digest drift as real until every payload source has been compared.",
        ],
    },
    "trace_rows": {
        "owner": "platform_ops",
        "symptoms": [
            "Trace rows are missing cases present in the run.",
            "Trace rows contain case ids that do not appear in the run.",
            "Case-level replay is incomplete even though the top-level packet exists.",
        ],
        "likely_causes": [
            "Trace generation was run against a stale run payload.",
            "Filtering logic dropped one visibility class during export.",
            "A packet repair updated the run but not the trace rows.",
        ],
        "checks": [
            "Compare run case ids with trace case ids.",
            "Check whether hidden or public cases were filtered incorrectly.",
            "Verify that every failing case has a matching trace row and section label.",
        ],
        "repairs": [
            "Regenerate trace rows from the same run used for the scorecard.",
            "Remove stale trace rows before re-exporting.",
            "Add a validation check to catch case-count mismatches earlier in the flow.",
        ],
    },
    "artifact_paths": {
        "owner": "risk_ops",
        "symptoms": [
            "Packet validation reports missing or unexpected artifact paths.",
            "Operators can no longer find the expected bundle/run folder layout inside the archive.",
            "The archive looks complete but downstream tooling cannot resolve paths predictably.",
        ],
        "likely_causes": [
            "A path prefix changed without updating the evidence map helper.",
            "One artifact was renamed during export but not in the contract table.",
            "A repair script appended extra files into the archive root.",
        ],
        "checks": [
            "Compare the packet artifact path map with the expected `bundle_id/run_id` prefix.",
            "List zip entries and compare them with the required artifact path list.",
            "Verify that unexpected files are deliberate and documented.",
        ],
        "repairs": [
            "Normalize every path through the evidence map helper.",
            "Update the artifact contract only when the new path is intentional and reviewable.",
            "Remove ad hoc extra files from the packet build path.",
        ],
    },
    "packet_digest": {
        "owner": "audit_ops",
        "symptoms": [
            "Packet digest mismatch even though the archive looks complete.",
            "Repeated exports from the same logical payload do not match.",
            "Operators are unsure whether the packet changed or only the zip wrapper changed.",
        ],
        "likely_causes": [
            "The packet payload was mutated after the digest was computed.",
            "One nested field changed type or ordering before export.",
            "A repair updated artifact paths or trace rows without recomputing the packet digest.",
        ],
        "checks": [
            "Recompute the digest from the packet without the `digest` field.",
            "Compare the logical payload before checking the archive bytes.",
            "Verify that path maps and trace rows were included in the digest input.",
        ],
        "repairs": [
            "Recompute the digest after all packet fields are finalized.",
            "Stabilize nested payload ordering before export.",
            "Never treat a digest mismatch as cosmetic until the logical packet payload has been diffed.",
        ],
    },
    "retention_link": {
        "owner": "treasury_ops",
        "symptoms": [
            "A row is marked prunable while the packet still needs repair.",
            "Retention planning and packet state disagree about whether evidence is safe to archive.",
            "Operators hesitate to clean up because the packet does not clearly prove export completeness.",
        ],
        "likely_causes": [
            "Retention checks are using the wrong export marker.",
            "The packet exists but failed validation and should not count as a safe export.",
            "A release note or manifest change happened after retention was last reviewed.",
        ],
        "checks": [
            "Confirm packet validation passes before marking a row export-safe.",
            "Check that the packet belongs to the same history row or release id under review.",
            "Review retention policy for the current channel and artifact class.",
        ],
        "repairs": [
            "Delay prune actions until packet validation is green.",
            "Record validation status next to export status in operator notes.",
            "Refresh retention planning whenever a packet is rebuilt or repaired.",
        ],
    },
    "history_import": {
        "owner": "reporting_ops",
        "symptoms": [
            "History rollups and packet details disagree about what run was reviewed.",
            "Owner dashboards show a row but the archived packet appears to belong to another release moment.",
            "The same history id appears to carry conflicting digest or score details across exports.",
        ],
        "likely_causes": [
            "The wrong raw history row was associated with the audit packet during persistence sync.",
            "A repair updated the packet but not the stored history payload used for reporting.",
            "Snapshot rebuilds used a stale import feed while packet export used a newer run payload.",
        ],
        "checks": [
            "Compare history row payload fields with the packet run and scorecard payloads.",
            "Check that the history id, run id, and bundle id all point at the same export lineage.",
            "Confirm the release channel and review state are consistent across storage and packet artifacts.",
        ],
        "repairs": [
            "Resync the history row from the same run and scorecard used to build the packet.",
            "Rebuild the snapshot or reporting import if the storage layer was stale.",
            "Record the lineage mismatch in operator notes so future cleanup does not prune the wrong row.",
        ],
    },
    "owner_dashboard": {
        "owner": "support_ops",
        "symptoms": [
            "Owner dashboard summaries disagree with packet-level review state or band details.",
            "A dashboard looks calm while packet inspection shows repeated watch or blocked bundles.",
            "Operators can no longer explain how a dashboard trend relates to one concrete packet.",
        ],
        "likely_causes": [
            "Dashboard queries are reading a stale snapshot or a mismatched schema version.",
            "One packet was rebuilt but the stored row used by dashboard rollups was not refreshed.",
            "A reporting surface collapsed hidden and public signals in a way the packet did not.",
        ],
        "checks": [
            "Compare dashboard rollup fields with recent history and packet scorecard payloads.",
            "Inspect schema drift before assuming the dashboard query logic is wrong.",
            "Check whether the owner average was built from rows that still match the current packet lineage.",
        ],
        "repairs": [
            "Refresh the snapshot or rebuild the dashboard summary from current history rows.",
            "Restore packet lineage fields to the dashboard source when they were stripped or renamed.",
            "Treat public-hidden mismatches as a reporting bug until proven otherwise.",
        ],
    },
    "retention_summary": {
        "owner": "treasury_ops",
        "symptoms": [
            "Retention summaries say a row is safe to prune while packet validation still fails.",
            "Archive candidates do not match the age or channel policy operators expect.",
            "Cleanup conversations keep reopening because the summary lacks packet state context.",
        ],
        "likely_causes": [
            "Retention planning used export existence instead of export validity.",
            "Channel or artifact class was classified incorrectly from the history row.",
            "A packet repair happened after the last retention summary was generated.",
        ],
        "checks": [
            "Compare the retention summary against current packet validation status.",
            "Confirm channel and artifact class derivation from the stored row.",
            "Verify that export-safe markers were updated after any packet repair or rebuild.",
        ],
        "repairs": [
            "Regenerate retention summaries after packet validation changes.",
            "Update the artifact classification rules when a new storage shape is introduced.",
            "Attach packet health context directly to prune and archive recommendations.",
        ],
    },
    "query_snapshot": {
        "owner": "platform_ops",
        "symptoms": [
            "Saved query results shift after a snapshot refresh even though packets look unchanged.",
            "Schema diff is clean enough to pass but a query still loses one expected field or grouping.",
            "A reporting incident starts from a query pack mismatch rather than from raw history drift.",
        ],
        "likely_causes": [
            "A snapshot schema change was additive but still incompatible with one saved query assumption.",
            "A query template expects a field path that the packet or payload no longer writes.",
            "Snapshot refreshes and packet rebuilds were done from different source vintages.",
        ],
        "checks": [
            "Compare the snapshot schema signature with the assumptions baked into the saved query pack.",
            "Diff query outputs against the underlying packet and history row fields.",
            "Verify that the query owner and downstream consumers still match the artifact set being read.",
        ],
        "repairs": [
            "Patch the query pack or snapshot migration so both speak the same field vocabulary.",
            "Rebuild snapshots from the same source vintage as the packets under review.",
            "Add a compatibility note when a query changes meaning but keeps the same identifier.",
        ],
    },
}


def guide(name: str) -> dict[str, object]:
    return dict(REPAIR_GUIDES[name])


def owners() -> list[str]:
    return sorted({item["owner"] for item in REPAIR_GUIDES.values()})


def symptoms(name: str) -> list[str]:
    return list(REPAIR_GUIDES[name]["symptoms"])


def checks(name: str) -> list[str]:
    return list(REPAIR_GUIDES[name]["checks"])


def repairs(name: str) -> list[str]:
    return list(REPAIR_GUIDES[name]["repairs"])


def guide_digest(name: str) -> str:
    return json_digest(REPAIR_GUIDES[name])


def render_markdown(name: str) -> str:
    item = REPAIR_GUIDES[name]
    lines = [f"# {name} repair guide", "", f"- owner: {item['owner']}", "", "## Symptoms"]
    lines.extend(f"- {entry}" for entry in item["symptoms"])
    lines.extend(["", "## Likely causes"])
    lines.extend(f"- {entry}" for entry in item["likely_causes"])
    lines.extend(["", "## Checks"])
    lines.extend(f"- {entry}" for entry in item["checks"])
    lines.extend(["", "## Repairs"])
    lines.extend(f"- {entry}" for entry in item["repairs"])
    return "\n".join(lines) + "\n"
