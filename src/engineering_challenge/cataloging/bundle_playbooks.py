from __future__ import annotations

from engineering_challenge.utils import json_digest


PLAYBOOKS: dict[str, dict[str, object]] = {
    "merchant-closeout": {
        "handoff_owner": "finance_ops",
        "watch_sections": ["validation", "execution", "audit"],
        "audit_focus": "Closeout bundles get reviewed for release-note accuracy, evidence completeness, and whether hidden exception cases still mirror the current month-end workflow.",
        "release_questions": [
            "Did the hidden cases move more than the public cases after the latest closeout policy update?",
            "Does the audit packet include the exact release note text finance shared with treasury?",
            "Are exception-handling prompts still aligned with the ledger shape used in current close review?",
        ],
        "failure_patterns": [
            "Late-result penalties hide a runtime regression and make the score drop look like a comparator problem.",
            "A bundle version changes without the review note being refreshed, which creates an audit mismatch later.",
            "The public-hidden gap widens after a policy change that only touched reconciliation edge cases.",
        ],
        "operator_steps": [
            "Validate bundle metadata before looking at score movement.",
            "Compare mixed and strong runs to see whether the gap is quality or capacity related.",
            "Check owner capacity and treasury handoff notes before scheduling a partner-facing release.",
        ],
        "escalation_order": ["finance_ops", "treasury_ops", "risk_ops"],
    },
    "warehouse-routing": {
        "handoff_owner": "logistics_ops",
        "watch_sections": ["catalog", "execution", "scoring"],
        "audit_focus": "Routing bundles are checked for exception-repair language, warehouse-capacity assumptions, and the way blackout weeks interact with release timing.",
        "release_questions": [
            "Did any recent route or zone changes invalidate hidden cases without changing the public walkthroughs?",
            "Are operator notes clear about whether failures came from stale routing assumptions or runtime behavior?",
            "Does the release manifest call out the train week if the owning warehouse group is partially blacked out?",
        ],
        "failure_patterns": [
            "A valid routing answer mismatches only because case fixtures still point at a retired facility code.",
            "Support notes describe the repair path differently from the bundle metadata, which makes remediation noisy.",
            "Owner capacity is technically available but the selected week is blacked out for one of the required approvers.",
        ],
        "operator_steps": [
            "Review route coverage notes before comparing percent deltas.",
            "Open the owner dashboard if warehouse latency increased during the same period.",
            "Treat blackout weeks as release blockers even if quota remains.",
        ],
        "escalation_order": ["logistics_ops", "support_ops", "platform_ops"],
    },
    "claims-intake": {
        "handoff_owner": "support_ops",
        "watch_sections": ["validation", "catalog", "execution"],
        "audit_focus": "Claims intake bundles are reviewed for escalation language, normalization rules, and whether runtime errors are masking taxonomy drift.",
        "release_questions": [
            "Did a new claims category change the expected answer tokens for hidden cases only?",
            "Are escalation notes still written in the vocabulary that support agents actually use in production?",
            "Does the bundle still separate malformed input handling from normal low-confidence review behavior?",
        ],
        "failure_patterns": [
            "An escalation wording update lands in the notes but not in the expected answer set.",
            "Comparator failures cluster in one section and look like scoring drift when they are really authoring drift.",
            "A support bundle is ready overall but still needs owner review because hidden case language moved abruptly.",
        ],
        "operator_steps": [
            "Read metadata notes before interpreting a blocked score.",
            "Check whether the weak run failed on normalization or on escalation output.",
            "Escalate to risk only when a comparator or evidence contract changed, not for ordinary wording noise.",
        ],
        "escalation_order": ["support_ops", "risk_ops", "content_ops"],
    },
    "reserve-rollforward": {
        "handoff_owner": "treasury_ops",
        "watch_sections": ["audit", "scoring", "validation"],
        "audit_focus": "Reserve bundles are close-sensitive, so the packet and release notes need to explain whether changes affect payout timing, gating, or exception remediation.",
        "release_questions": [
            "Did reserve thresholds move in a way that requires treasury signoff before the next train?",
            "Does the hidden score drop line up with known payout-edge cases or with something broader?",
            "Are the release notes explicit about any rollforward or close-window assumptions?",
        ],
        "failure_patterns": [
            "A hidden-case regression is misread as a general quality problem when it is isolated to reserve timing logic.",
            "Treasury notes reference a prior release id, which later breaks audit review.",
            "A bundle is kept active too long even though the replacement version is already available.",
        ],
        "operator_steps": [
            "Confirm release note freshness against the manifest digest.",
            "Review partner versus internal retention impact before pruning any raw runs.",
            "Schedule treasury review ahead of finance only when reserve gating changed materially.",
        ],
        "escalation_order": ["treasury_ops", "finance_ops", "risk_ops"],
    },
    "identity-refresh": {
        "handoff_owner": "risk_ops",
        "watch_sections": ["execution", "audit", "validation"],
        "audit_focus": "Identity bundles lean on runtime stability and evidence coverage because small payload changes can create long-tail review problems.",
        "release_questions": [
            "Did watchlist verification rules move without the hidden cases being refreshed?",
            "Are execution errors concentrated in one payload shape or spread across the whole bundle?",
            "Does the audit packet still map all required identity review artifacts into the expected path set?",
        ],
        "failure_patterns": [
            "A runtime timeout looks like content drift until the case-level transcript is inspected.",
            "An evidence field is dropped from the packet payload but the release still looks healthy at a high level.",
            "The owner dashboard remains flat while one hidden section collapses under new identity payloads.",
        ],
        "operator_steps": [
            "Inspect execution timing before touching score thresholds.",
            "Check required field coverage for every packet source.",
            "Use the schema diff helpers before blaming snapshot or dashboard output.",
        ],
        "escalation_order": ["risk_ops", "platform_ops", "support_ops"],
    },
    "subscriber-billing": {
        "handoff_owner": "revops",
        "watch_sections": ["catalog", "scoring", "audit"],
        "audit_focus": "Recurring billing bundles are tracked for entitlement wording, remission policy hints, and score drift between rehearsal and internal channels.",
        "release_questions": [
            "Did any hidden billing edge cases start failing after the most recent entitlement policy edit?",
            "Is the owner dashboard showing a long-running decline rather than a one-off bad attempt?",
            "Do the release notes name the exact policy delta instead of only saying 'billing changes'?",
        ],
        "failure_patterns": [
            "Hidden cases remain stale while the public walkthrough receives all the updates.",
            "A release note is accurate but too vague for the downstream owner to correlate with the score change.",
            "Audit evidence is present but missing the fields needed for a replayable entitlement review.",
        ],
        "operator_steps": [
            "Review the last two release notes before approving a new train.",
            "Compare hidden score movement with risk flags, not only with the blended percent.",
            "Escalate to finance when billing bundles start tripping the same review flag as closeout bundles.",
        ],
        "escalation_order": ["revops", "finance_ops", "procurement_ops"],
    },
    "seat-allocation": {
        "handoff_owner": "education_ops",
        "watch_sections": ["validation", "scoring", "release"],
        "audit_focus": "Seat allocation bundles are fairness-sensitive and need explicit notes when a policy or timing rule affects hidden cases differently from public ones.",
        "release_questions": [
            "Did the roster timing rules change in the hidden cases only?",
            "Are partner reviewers likely to see a different remediation path after this release?",
            "Does the current train line up with owner availability and fairness-review expectations?",
        ],
        "failure_patterns": [
            "A fairness regression hides behind a still-acceptable blended percent.",
            "Review notes mention roster timing, but the bundle title and release notes do not.",
            "The same owner hits capacity limits across multiple education bundles in one train.",
        ],
        "operator_steps": [
            "Look at hidden-case movement before using the total percent as a decision shortcut.",
            "Confirm partner-facing narrative text is in the release note before shipping.",
            "Use rollout gate notes when the calendar is the blocker, not the score.",
        ],
        "escalation_order": ["education_ops", "risk_ops", "support_ops"],
    },
    "fulfillment-ledger": {
        "handoff_owner": "platform_ops",
        "watch_sections": ["execution", "catalog", "audit"],
        "audit_focus": "Fulfillment bundles sit between runtime normalization and operator review, so the main question is whether the sequence and adjustment logic still reflects reality.",
        "release_questions": [
            "Did event sequencing or adjustment wording change without a corresponding bundle note?",
            "Are runtime errors clustered in one batch or distributed across case families?",
            "Does the packet still preserve the fields needed to replay an adjustment dispute?",
        ],
        "failure_patterns": [
            "A sequence bug appears as a content mismatch because the transcript is not reviewed first.",
            "A hidden-case regression is caused by stale ledger examples rather than runtime behavior.",
            "Release manifests drift because the operator rebuilt the packet from a different bundle version.",
        ],
        "operator_steps": [
            "Inspect transcripts for the failing cases first.",
            "Check whether the manifest digest changed before rebuilding evidence by hand.",
            "Escalate to revops only after runtime normalization has been ruled out.",
        ],
        "escalation_order": ["platform_ops", "revops", "risk_ops"],
    },
    "document-classifier": {
        "handoff_owner": "content_ops",
        "watch_sections": ["catalog", "audit", "validation"],
        "audit_focus": "Classifier bundles depend on prompt wording, extraction rules, and field coverage. The audit path needs to preserve enough context to explain why a routing decision changed.",
        "release_questions": [
            "Did prompt wording move in a way that affects hidden cases more than public walkthroughs?",
            "Are required extraction fields still present in the archived packet payload?",
            "Did a partner-control or review label change require a risk signoff?",
        ],
        "failure_patterns": [
            "Public examples get refreshed while hidden extraction cases still reflect an older routing taxonomy.",
            "An extraction field disappears from evidence and turns a replayable packet into a decorative archive.",
            "Risk is pulled in too late because the release note hides a partner-facing wording change.",
        ],
        "operator_steps": [
            "Review field coverage before scorecard detail when packet integrity is in doubt.",
            "Confirm that notes, tags, and title all describe the same routing intent.",
            "Escalate to risk for partner-control changes even if the percent improved.",
        ],
        "escalation_order": ["content_ops", "risk_ops", "support_ops"],
    },
    "vendor-settlement": {
        "handoff_owner": "procurement_ops",
        "watch_sections": ["scoring", "audit", "release"],
        "audit_focus": "Vendor settlement bundles are judged by clarity of dispute handling, settlement exceptions, and whether review notes are actionable by procurement and support.",
        "release_questions": [
            "Did a settlement exception rule change without an explicit note in the release record?",
            "Are procurement and support using the same remediation vocabulary?",
            "Does the partner or internal retention horizon change because of this release?",
        ],
        "failure_patterns": [
            "Settlement terminology drifts between bundle metadata and release notes.",
            "Review flags accumulate because vendor-specific hidden cases were not refreshed after a workflow change.",
            "The bundle is technically valid but still not supportable by downstream reviewers.",
        ],
        "operator_steps": [
            "Compare remediation language across notes, bundle metadata, and audit evidence.",
            "Review retention implications when partner exports are involved.",
            "Escalate to sales only when the workflow change affects vendor-facing communication.",
        ],
        "escalation_order": ["procurement_ops", "support_ops", "sales_ops"],
    },
    "pricing-handoff": {
        "handoff_owner": "sales_ops",
        "watch_sections": ["validation", "release", "audit"],
        "audit_focus": "Pricing bundles need precise release notes because downstream users read them as policy statements rather than purely technical summaries.",
        "release_questions": [
            "Did the discount validation cases move in lockstep with the release note language?",
            "Are the hidden cases still exercising the same handoff assumptions used by sales reviewers?",
            "Will the next train create confusion if the change is not called out clearly in the brief?",
        ],
        "failure_patterns": [
            "A pricing policy shift is real, but only the title changes and the operator brief stays vague.",
            "Hidden cases lag behind a discount-rule change and create a misleading public-hidden gap.",
            "Release digests change because bundle summaries were rebuilt without updated notes.",
        ],
        "operator_steps": [
            "Start with release notes and title alignment before drilling into case-level failures.",
            "Use audit evidence to confirm what policy text was actually frozen.",
            "Escalate to finance if the pricing handoff starts matching closeout failure shapes.",
        ],
        "escalation_order": ["sales_ops", "finance_ops", "support_ops"],
    },
    "returns-recovery": {
        "handoff_owner": "returns_ops",
        "watch_sections": ["execution", "audit", "scoring"],
        "audit_focus": "Returns bundles are operationally messy. The playbook focuses on whether the recovery path, disposition rules, and support expectations still line up.",
        "release_questions": [
            "Did the recovery workflow change in the hidden cases without a matching release note update?",
            "Are long-tail timeout cases causing the same review pattern as true answer mismatches?",
            "Do the retained artifacts still give support enough context to reproduce a failed recovery review?",
        ],
        "failure_patterns": [
            "A timeout-heavy weak run looks like content drift until runtime is inspected.",
            "Disposition language changes in one place and leaves the recovery notes stale.",
            "A release gets scheduled in a week where the returns owner still has quota but lacks reviewer coverage.",
        ],
        "operator_steps": [
            "Check retry summaries when the weak run collapses more than expected.",
            "Confirm that returns release notes mention any disposition or queue changes.",
            "Use the owner dashboard before assuming the latest run is a one-off event.",
        ],
        "escalation_order": ["returns_ops", "support_ops", "finance_ops"],
    },
}


def playbook(bundle_id: str) -> dict[str, object]:
    return dict(PLAYBOOKS[bundle_id])


def watch_sections(bundle_id: str) -> list[str]:
    return list(PLAYBOOKS[bundle_id]["watch_sections"])


def release_questions(bundle_id: str) -> list[str]:
    return list(PLAYBOOKS[bundle_id]["release_questions"])


def failure_patterns(bundle_id: str) -> list[str]:
    return list(PLAYBOOKS[bundle_id]["failure_patterns"])


def operator_steps(bundle_id: str) -> list[str]:
    return list(PLAYBOOKS[bundle_id]["operator_steps"])


def escalation_chain(bundle_id: str) -> list[str]:
    return list(PLAYBOOKS[bundle_id]["escalation_order"])


def playbook_digest(bundle_id: str) -> str:
    return json_digest(PLAYBOOKS[bundle_id])


def render_markdown(bundle_id: str) -> str:
    item = PLAYBOOKS[bundle_id]
    lines = [f"# {bundle_id} playbook", "", f"- handoff owner: {item['handoff_owner']}", ""]
    lines.append("## Watch sections")
    lines.extend(f"- {section}" for section in item["watch_sections"])
    lines.extend(["", "## Audit focus", item["audit_focus"], "", "## Release questions"])
    lines.extend(f"- {question}" for question in item["release_questions"])
    lines.extend(["", "## Failure patterns"])
    lines.extend(f"- {pattern}" for pattern in item["failure_patterns"])
    lines.extend(["", "## Operator steps"])
    lines.extend(f"- {step}" for step in item["operator_steps"])
    lines.extend(["", "## Escalation order"])
    lines.extend(f"- {owner}" for owner in item["escalation_order"])
    return "\n".join(lines) + "\n"
