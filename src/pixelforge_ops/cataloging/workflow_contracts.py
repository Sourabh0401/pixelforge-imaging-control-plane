from __future__ import annotations

from dataclasses import dataclass

from pixelforge_ops.datafiles import load_json_data
from pixelforge_ops.models import ExerciseBundle
from pixelforge_ops.utils import json_digest


@dataclass(frozen=True)
class WorkflowStep:
    code: str
    phase: str
    owner_role: str
    required: bool
    artifacts: tuple[str, ...]
    notes: str


_RAW_CONTRACTS = load_json_data("cataloging", "workflow_contracts.json")
WORKFLOW_CONTRACTS: dict[str, dict[str, object]] = {
    domain: {
        "downstream": tuple(payload["downstream"]),
        "channels": tuple(payload["channels"]),
        "steps": tuple(
            WorkflowStep(
                code=step["code"],
                phase=step["phase"],
                owner_role=step["owner_role"],
                required=bool(step["required"]),
                artifacts=tuple(step["artifacts"]),
                notes=step["notes"],
            )
            for step in payload["steps"]
        ),
    }
    for domain, payload in _RAW_CONTRACTS.items()
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
