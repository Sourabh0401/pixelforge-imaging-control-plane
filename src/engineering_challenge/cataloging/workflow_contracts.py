from __future__ import annotations

from dataclasses import dataclass

from engineering_challenge.models import ExerciseBundle
from engineering_challenge.utils import json_digest


@dataclass(frozen=True)
class WorkflowStep:
    code: str
    phase: str
    owner_role: str
    required: bool
    artifacts: tuple[str, ...]
    notes: str


WORKFLOW_CONTRACTS: dict[str, dict[str, object]] = {
    "finance_ops": {
        "downstream": ("close-review", "audit-export", "treasury-handoff"),
        "channels": ("internal", "partner"),
        "steps": (
            WorkflowStep("finance-intake", "authoring", "finance_ops", True, ("bundle.json", "cases.jsonl"), "Finance authors refresh closeout inputs and confirms that release-facing examples still match the ledger shape used by current reviewers."),
            WorkflowStep("finance-thresholds", "scoring", "finance_ops", True, ("scorecard.json",), "Finance checks that hidden penalty weighting still matches the most recent review guidance before the bundle moves to a release train."),
            WorkflowStep("finance-audit-evidence", "audit", "finance_ops", True, ("audit_packet.json", "manifest.json"), "Audit evidence must be exported before raw run payloads are eligible for pruning."),
            WorkflowStep("finance-treasury-handoff", "release", "treasury_ops", True, ("release_notes.md",), "Treasury consumes the release note summary and any queue-delay caveats that could affect downstream close timing."),
        ),
    },
    "logistics_ops": {
        "downstream": ("routing-watch", "capacity-audit", "partner-ops"),
        "channels": ("internal", "pilot"),
        "steps": (
            WorkflowStep("route-intake", "authoring", "logistics_ops", True, ("bundle.json", "cases.jsonl"), "Routing owners keep zone-coverage cases current and flag whether any warehouse outages changed the expected answer set."),
            WorkflowStep("route-repair-review", "review", "support_ops", True, ("review_notes.md",), "Support reviews the exception-repair prompts because those are where routing bundles tend to drift under live queue pressure."),
            WorkflowStep("route-capacity", "release", "logistics_ops", True, ("release_manifest.json",), "Capacity checks need to happen before scheduling because blackout weeks are common in warehouse transitions."),
            WorkflowStep("route-audit", "audit", "risk_ops", False, ("audit_packet.json",), "Risk only joins when the routing bundle is headed to a partner-facing channel."),
        ),
    },
    "support_ops": {
        "downstream": ("escalation-runbook", "owner-dashboard", "release-support"),
        "channels": ("internal", "rehearsal", "ops-only"),
        "steps": (
            WorkflowStep("support-normalization", "authoring", "support_ops", True, ("bundle.json",), "Support keeps intake prompts aligned with current escalation macros so the hidden cases still exercise the real review flow."),
            WorkflowStep("support-shadow-review", "review", "risk_ops", False, ("case_review.json",), "Risk does a shadow review when a support bundle introduces a new comparator or wording pattern."),
            WorkflowStep("support-dashboard-brief", "reporting", "support_ops", True, ("owner_dashboard.json",), "Support expects a dashboard snapshot before release so slow-moving hidden score regressions are easy to spot."),
            WorkflowStep("support-release-note", "release", "support_ops", True, ("release_notes.md",), "The release note has to call out escalation policy changes explicitly because downstream runbooks are written from it."),
        ),
    },
    "platform_ops": {
        "downstream": ("identity-audit", "runtime-watch", "policy-review"),
        "channels": ("internal", "pilot"),
        "steps": (
            WorkflowStep("platform-schema-check", "authoring", "platform_ops", True, ("bundle.json", "cases.jsonl"), "Identity and runtime bundles should be checked against current payload contracts before they are scored."),
            WorkflowStep("platform-runtime-review", "execution", "platform_ops", True, ("run.json",), "Platform owns runtime normalization and timeout tuning, so replay output must be reviewed when latency shifts."),
            WorkflowStep("platform-release-signoff", "release", "platform_ops", True, ("release_manifest.json", "checklist.json"), "Platform signs off on release only after runtime and retry guidance are in the checklist payload."),
            WorkflowStep("platform-audit-retain", "audit", "platform_ops", True, ("audit_packet.json",), "Audit exports for platform bundles stay longer because identity-refresh issues are often investigated weeks later."),
        ),
    },
    "procurement_ops": {
        "downstream": ("billing-rollup", "vendor-support", "ops-review"),
        "channels": ("internal", "ops-only"),
        "steps": (
            WorkflowStep("billing-authoring", "authoring", "procurement_ops", True, ("bundle.json",), "Billing owners keep supplier exception examples current and annotate any rule-set changes in bundle metadata."),
            WorkflowStep("billing-score-compare", "scoring", "finance_ops", True, ("scorecard.json",), "Finance compares public and hidden scoring on subscriber-billing changes before the bundle can be marked ready."),
            WorkflowStep("billing-ops-note", "reporting", "procurement_ops", True, ("dashboard.json", "release_notes.md"), "Ops notes need to mention whether review latency is driven by data quality or rubric movement."),
        ),
    },
    "content_ops": {
        "downstream": ("classifier-review", "owner-dashboard", "release-brief"),
        "channels": ("internal", "ops-only"),
        "steps": (
            WorkflowStep("content-authoring", "authoring", "content_ops", True, ("bundle.json", "cases.jsonl"), "Content owners maintain routing prompts and extraction expectations used by the document-classifier bundle."),
            WorkflowStep("content-quality-review", "review", "content_ops", True, ("review_notes.md",), "Content reviewers check wording drift and confirm that hidden examples still match the live annotation flow."),
            WorkflowStep("content-audit-check", "audit", "risk_ops", False, ("audit_packet.json",), "Risk joins when extraction changes touch partner-controlled data fields."),
            WorkflowStep("content-release-note", "release", "content_ops", True, ("release_notes.md",), "Release notes summarize prompt wording changes and any expected shift in extraction failure patterns."),
        ),
    },
    "education_ops": {
        "downstream": ("seat-fairness", "partner-review", "support-queue"),
        "channels": ("internal", "partner", "pilot"),
        "steps": (
            WorkflowStep("seat-authoring", "authoring", "education_ops", True, ("bundle.json", "cases.jsonl"), "Seat allocation bundles are audited for fairness language and partner-policy compliance together."),
            WorkflowStep("seat-hidden-review", "review", "education_ops", True, ("review_notes.md",), "Hidden cases should reflect the current exception path rather than a simplified demo path."),
            WorkflowStep("seat-fairness-check", "scoring", "risk_ops", True, ("scorecard.json",), "Risk reviews hidden/public gap movement because those bundles are sensitive to rubric drift."),
            WorkflowStep("seat-release-note", "release", "education_ops", True, ("release_notes.md",), "Release notes need to say whether partner reviewers should expect any new remediation flow."),
        ),
    },
    "revops": {
        "downstream": ("ledger-close", "finance-audit", "owner-summary"),
        "channels": ("internal", "rehearsal", "partner"),
        "steps": (
            WorkflowStep("ledger-authoring", "authoring", "revops", True, ("bundle.json", "cases.jsonl"), "Ledger bundle authors confirm the score impact of every new exception case before release week."),
            WorkflowStep("ledger-score-review", "scoring", "finance_ops", True, ("scorecard.json",), "Finance checks that fulfillment-ledger scoring still tracks the closeout bundle expectations."),
            WorkflowStep("ledger-audit-export", "audit", "revops", True, ("audit_packet.json", "manifest.json"), "Ledger bundles require audit export on every train because their artifacts are frequently compared across quarters."),
            WorkflowStep("ledger-owner-brief", "reporting", "revops", True, ("owner_dashboard.json",), "The owner brief is the first place operators look when a ledger bundle starts failing hidden checks."),
        ),
    },
    "risk_ops": {
        "downstream": ("classifier-review", "partner-controls", "release-watch"),
        "channels": ("internal", "partner", "ops-only"),
        "steps": (
            WorkflowStep("risk-authoring", "authoring", "risk_ops", True, ("bundle.json",), "Risk owns classifier wording, partner-control metadata, and audit-field expectations."),
            WorkflowStep("risk-evidence-check", "audit", "risk_ops", True, ("audit_packet.json", "trace.json"), "Evidence completeness matters more than raw percent for some partner-facing risk bundles."),
            WorkflowStep("risk-release-gate", "release", "risk_ops", True, ("release_manifest.json",), "Risk bundles do not ship when owner capacity is available but required field coverage still falls short."),
        ),
    },
    "sales_ops": {
        "downstream": ("vendor-triage", "partner-sales", "ops-summary"),
        "channels": ("internal", "partner"),
        "steps": (
            WorkflowStep("vendor-authoring", "authoring", "sales_ops", True, ("bundle.json", "cases.jsonl"), "Vendor settlement bundles reflect the latest sales-ops dispute flow and payment exception language."),
            WorkflowStep("vendor-support-review", "review", "support_ops", False, ("review_notes.md",), "Support reviews new remediation language when the vendor workflow changes materially."),
            WorkflowStep("vendor-release-note", "release", "sales_ops", True, ("release_notes.md",), "Release notes must call out partner-facing changes in terminology and remediation expectations."),
        ),
    },
    "treasury_ops": {
        "downstream": ("returns-audit", "finance-close", "ops-watch"),
        "channels": ("internal", "rehearsal"),
        "steps": (
            WorkflowStep("returns-authoring", "authoring", "treasury_ops", True, ("bundle.json",), "Treasury keeps recovery assumptions aligned with the return-clearing process used in the close window."),
            WorkflowStep("returns-close-compare", "scoring", "finance_ops", True, ("scorecard.json",), "Treasury and finance compare returns-recovery hidden scores during close rehearsals."),
            WorkflowStep("returns-audit-packet", "audit", "treasury_ops", True, ("audit_packet.json",), "Audit packets for treasury bundles stay attached to the release record until the close window expires."),
        ),
    },
    "returns_ops": {
        "downstream": ("returns-audit", "owner-watch", "queue-repair"),
        "channels": ("internal", "rehearsal", "pilot"),
        "steps": (
            WorkflowStep("returns-authoring", "authoring", "returns_ops", True, ("bundle.json", "cases.jsonl"), "Returns owners keep disposition and recovery examples aligned with the current queue handling workflow."),
            WorkflowStep("returns-runtime-review", "execution", "returns_ops", True, ("run.json",), "Execution output is reviewed for long-tail case timing because late results are common in returns remediation bundles."),
            WorkflowStep("returns-score-review", "scoring", "finance_ops", False, ("scorecard.json",), "Finance reviews blended score movement when the recovery policy changes affect downstream close handling."),
            WorkflowStep("returns-release-note", "release", "returns_ops", True, ("release_notes.md",), "Release notes call out any recovery-path changes that support or warehouse teams will feel immediately."),
        ),
    },
}


def workflow_steps(domain: str) -> tuple[WorkflowStep, ...]:
    return tuple(WORKFLOW_CONTRACTS[domain]["steps"])


def required_artifacts(domain: str) -> tuple[str, ...]:
    artifacts: set[str] = set()
    for step in workflow_steps(domain):
        artifacts.update(step.artifacts)
    return tuple(sorted(artifacts))


def required_owner_roles(domain: str) -> tuple[str, ...]:
    return tuple(sorted({step.owner_role for step in workflow_steps(domain) if step.required}))


def allowed_channels(domain: str) -> tuple[str, ...]:
    return tuple(WORKFLOW_CONTRACTS[domain]["channels"])


def downstream_consumers(domain: str) -> tuple[str, ...]:
    return tuple(WORKFLOW_CONTRACTS[domain]["downstream"])


def step_index(domain: str) -> dict[str, WorkflowStep]:
    return {step.code: step for step in workflow_steps(domain)}


def missing_artifacts(domain: str, present: list[str]) -> list[str]:
    required = set(required_artifacts(domain))
    return sorted(required - set(present))


def phase_summary(domain: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for step in workflow_steps(domain):
        counts[step.phase] = counts.get(step.phase, 0) + 1
    return dict(sorted(counts.items()))


def validate_bundle_contract(bundle: ExerciseBundle) -> list[str]:
    issues: list[str] = []
    if bundle.domain not in WORKFLOW_CONTRACTS:
        issues.append(f"no workflow contract for domain {bundle.domain}")
        return issues
    contract = WORKFLOW_CONTRACTS[bundle.domain]
    if bundle.owner not in required_owner_roles(bundle.domain):
        issues.append(f"owner {bundle.owner} is not listed in required workflow roles")
    if bundle.metadata.get("release_channel") not in contract["channels"]:
        issues.append(f"release channel {bundle.metadata.get('release_channel')} is not approved for domain {bundle.domain}")
    if "author" not in bundle.metadata:
        issues.append("bundle metadata missing author")
    if not bundle.metadata.get("notes"):
        issues.append("bundle metadata missing release notes")
    if not bundle.hidden_cases():
        issues.append("bundle has no hidden cases")
    return issues


def contract_digest(domain: str) -> str:
    payload = {
        "domain": domain,
        "channels": list(allowed_channels(domain)),
        "downstream": list(downstream_consumers(domain)),
        "steps": [
            {
                "code": step.code,
                "phase": step.phase,
                "owner_role": step.owner_role,
                "required": step.required,
                "artifacts": list(step.artifacts),
                "notes": step.notes,
            }
            for step in workflow_steps(domain)
        ],
    }
    return json_digest(payload)


def render_contract_markdown(domain: str) -> str:
    lines = [f"# Workflow contract: {domain}", "", "## Channels"]
    lines.extend(f"- {channel}" for channel in allowed_channels(domain))
    lines.extend(["", "## Downstream consumers"])
    lines.extend(f"- {consumer}" for consumer in downstream_consumers(domain))
    lines.extend(["", "## Steps"])
    for step in workflow_steps(domain):
        marker = "required" if step.required else "optional"
        lines.append(f"- `{step.code}` [{step.phase}] {step.owner_role}, {marker}")
        lines.append(f"  - artifacts: {', '.join(step.artifacts)}")
        lines.append(f"  - notes: {step.notes}")
    return "\n".join(lines) + "\n"
