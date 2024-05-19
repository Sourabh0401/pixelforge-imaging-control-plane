from __future__ import annotations

from engineering_challenge.utils import json_digest


OWNER_HANDOFF_GUIDES = {
    "content_ops": {
        "purpose": "Guide for handing classifier and extraction bundles between content review, risk review, and release operations.",
        "signals": [
            "Prompt wording drift between release note text and hidden case expectations.",
            "Audit packet field coverage slipping even though the bundle score remains stable.",
            "A rising gap between public walkthrough scores and hidden extraction checks.",
        ],
        "questions": [
            "What changed in authoring, and what changed only in release explanation?",
            "Can a downstream reviewer replay the issue from the packet without asking the original author?",
            "Did the classifier vocabulary move in one owner-facing artifact but not the others?",
        ],
        "handoff_notes": [
            "Content sends release-ready bundles to risk whenever partner wording changes.",
            "Support joins when remediation or escalation phrasing shifts enough to affect queue handling.",
            "Release ops is added only after evidence completeness and title-note alignment are confirmed.",
        ],
    },
    "education_ops": {
        "purpose": "Guide for seat allocation bundles where fairness, partner timing, and reviewer availability all matter.",
        "signals": [
            "Hidden sections regressing while public score stays flat.",
            "Fairness review notes disagreeing with release notes on the scope of a change.",
            "Owner capacity pressure building across more than one education bundle in the same train.",
        ],
        "questions": [
            "Is this a real assessment change or a scheduling issue masked as a score change?",
            "Would the partner reviewer read the release note and understand the fairness caveat?",
            "Are hidden seat-allocation cases still the right stress test for current workflows?",
        ],
        "handoff_notes": [
            "Education keeps the first pass, risk validates fairness-sensitive wording, and support reviews queue impact.",
            "If a change is train-bound rather than content-bound, release ops should own the next action.",
            "When partner-facing behavior changed, the brief must include the escalation route explicitly.",
        ],
    },
    "finance_ops": {
        "purpose": "Guide for closeout, reserve, and adjacent scoring reviews where release readiness is tied to real money movement.",
        "signals": [
            "Closeout or reserve bundles moving from ready to watch without a new audit note.",
            "Hidden-case movement exceeding public movement by a wide margin.",
            "Retention plans or packet age becoming the real blocker rather than the score itself.",
        ],
        "questions": [
            "Which exact policy or workflow change explains the movement?",
            "Is treasury being asked to infer missing context from a scorecard alone?",
            "Did a release note update happen without bundle metadata or packet changes?",
        ],
        "handoff_notes": [
            "Finance is the first reviewer for close-sensitive bundles.",
            "Treasury joins before partner release when payout or reserve behavior changed.",
            "Risk is pulled in when audit evidence or control language becomes the main concern.",
        ],
    },
    "logistics_ops": {
        "purpose": "Guide for warehouse routing bundles that mix route assumptions, facility calendars, and reviewer availability.",
        "signals": [
            "Blocked bundles with healthy scores but impossible scheduling windows.",
            "Repair instructions diverging across notes, hidden cases, and support feedback.",
            "Runtime latency rising at the same time route coverage changes.",
        ],
        "questions": [
            "Are we dealing with stale content or with the wrong release week?",
            "Do repair notes still match the route taxonomy in the current fixtures?",
            "Would a warehouse reviewer understand why the bundle is blocked from the brief alone?",
        ],
        "handoff_notes": [
            "Logistics owns the route assumptions, support owns remediation wording, and platform owns runtime anomalies.",
            "Release ops should only step in after blackout and quota checks are explicit.",
            "A partner-facing routing change needs both note clarity and audit completeness.",
        ],
    },
    "platform_ops": {
        "purpose": "Guide for runtime-sensitive bundles where worker-version shifts, retry windows, and transcript quality matter as much as the final score.",
        "signals": [
            "A cluster of timeout or error states after a worker or queue-policy change.",
            "Manifest digests changing while bundle content appears unchanged.",
            "Owner dashboards staying flat while transcripts tell a very different story.",
        ],
        "questions": [
            "What part of the failure is runtime, and what part is content or scoring?",
            "Can the packet still reproduce the operational path we need to inspect?",
            "Did the release note describe the runtime policy shift in plain language?",
        ],
        "handoff_notes": [
            "Platform reviews execution shape first and only escalates to revops or risk after ruling out runtime drift.",
            "When packet fidelity is weak, audit and persistence owners should be pulled in before any release decision.",
            "A rollback recommendation should include the queue or worker signal that triggered it.",
        ],
    },
    "procurement_ops": {
        "purpose": "Guide for vendor settlement bundles where dispute terms, settlement exceptions, and support vocabulary must stay aligned.",
        "signals": [
            "Settlement bundles drifting because hidden case language lagged behind workflow updates.",
            "Support review notes using different terms than procurement release notes.",
            "Partner retention expectations changing without a corresponding audit-plan note.",
        ],
        "questions": [
            "Can support reproduce the dispute path from the current packet and note set?",
            "Did the workflow change affect vendor-facing communication or only internal handling?",
            "Are the settlement exceptions still grouped in a useful way for release review?",
        ],
        "handoff_notes": [
            "Procurement owns the business language, support owns queue usability, and sales only joins for outward communication changes.",
            "When partner exports exist, retention implications should be attached to the handoff note.",
            "Repeated watch-band behavior should be framed as a workflow health issue, not only a score issue.",
        ],
    },
    "returns_ops": {
        "purpose": "Guide for recovery and returns bundles that often mix runtime noise with real workflow drift.",
        "signals": [
            "Weak runs collapsing because of timeouts more than answer mismatches.",
            "Recovery language in hidden cases diverging from what support and warehouse teams expect.",
            "Reviewer capacity looking fine on paper while the actual queue still stalls.",
        ],
        "questions": [
            "Which failures can be retried safely and which ones need a content fix?",
            "Did disposition rules move without a matching note change?",
            "Is the queue pattern new, or has the owner dashboard been warning about it for weeks?",
        ],
        "handoff_notes": [
            "Returns owns the recovery flow, support owns downstream usability, and finance joins when closeout-adjacent behavior moves.",
            "Release ops should capture the retry horizon when runtime contributes to the failure pattern.",
            "If the next action is scheduling, the note should say that plainly so the bundle is not over-fixed.",
        ],
    },
    "revops": {
        "purpose": "Guide for recurring billing bundles where entitlement logic, release narrative, and audit evidence have to line up tightly.",
        "signals": [
            "Audit packet content staying valid while the release story grows harder to follow.",
            "A slow hidden-score decline that only becomes obvious in the portfolio view.",
            "Repeated patterns across billing and ledger bundles that suggest a shared policy cause.",
        ],
        "questions": [
            "What would a release owner need to know without reopening the raw run?",
            "Did a note or metadata gap create more confusion than the score movement itself?",
            "Is the same failure mode already showing up in adjacent bundles?",
        ],
        "handoff_notes": [
            "Revops owns the first read, finance joins for threshold interpretation, and platform joins when runtime drift is involved.",
            "A release hold should include both the owner-average trend and the latest digest context.",
            "When the bundle is healthy but the packet is weak, the note should recommend an audit repair rather than a scoring change.",
        ],
    },
    "risk_ops": {
        "purpose": "Guide for identity and control-sensitive bundles where evidence quality and hidden-case behavior carry extra weight.",
        "signals": [
            "Field coverage or packet completeness becoming the main operational problem.",
            "Partner-control wording changing without a matching risk review note.",
            "A hidden-case drop that points to real control drift rather than ordinary release noise.",
        ],
        "questions": [
            "Would a downstream control owner trust the current packet?",
            "Is the hidden drift isolated to one section or spread across the whole bundle?",
            "Did partner-facing language change enough to require a different release channel or timing?",
        ],
        "handoff_notes": [
            "Risk owns control interpretation, platform owns runtime reproducibility, and content or support joins based on where the wording lives.",
            "A risk handoff should name whether the issue is evidence, content, scheduling, or runtime.",
            "If control language changed, the next reviewer should not have to infer that from score movement alone.",
        ],
    },
    "sales_ops": {
        "purpose": "Guide for pricing handoff bundles where policy language and release narrative can matter as much as the raw percent.",
        "signals": [
            "Discount-validation drift between bundle notes and release notes.",
            "A public-hidden gap opening because the hidden pricing edge cases were not updated.",
            "Cross-team confusion about whether a blocked result is a finance issue or a sales wording issue.",
        ],
        "questions": [
            "Would the current release brief tell another owner exactly what policy moved?",
            "Did hidden cases lag behind the same wording change the title already reflects?",
            "Is this bundle starting to mirror a finance failure pattern that needs joint review?",
        ],
        "handoff_notes": [
            "Sales owns the handoff language, finance owns threshold interpretation, and support helps when queue remediation is the real problem.",
            "A release note should include the changed policy text, not just a label.",
            "When the failure is primarily narrative, the handoff should say so to avoid unnecessary tuning.",
        ],
    },
    "support_ops": {
        "purpose": "Guide for claims intake bundles that spend most of their life near escalation flows, taxonomy edges, and review queue management.",
        "signals": [
            "Escalation language drifting from hidden case expectations.",
            "Review-state balance shifting sharply toward support review.",
            "A blocked result being caused by one noisy comparator instead of a broad quality issue.",
        ],
        "questions": [
            "Is this an intake taxonomy change, an escalation change, or just one broken fixture?",
            "Would the next owner know whether to look at content, risk, or release scheduling?",
            "Are queue effects making the bundle look worse than it is?",
        ],
        "handoff_notes": [
            "Support owns the queue-facing interpretation, content helps with wording, and risk joins when controls or evidence are implicated.",
            "A support handoff should make the next owner feel oriented, not buried in raw data.",
            "The note should say what not to change as clearly as what to change.",
        ],
    },
    "treasury_ops": {
        "purpose": "Guide for reserve and payout-gate bundles where retention rules, audit evidence, and close timing all matter together.",
        "signals": [
            "Rows becoming prunable while close-sensitive work is still under review.",
            "Reserve hidden scores moving without a matching release note update.",
            "Treasury being pulled into a hold with less context than finance already has.",
        ],
        "questions": [
            "What needs to be retained, archived, or pruned, and why?",
            "Did the reserve or payout note actually explain the workflow change?",
            "Would the next reviewer know whether this is a close, policy, or scheduling issue?",
        ],
        "handoff_notes": [
            "Treasury should receive both retention context and score movement context.",
            "Finance joins for close interpretation, risk joins when audit evidence is incomplete, and release ops joins for train scheduling.",
            "A treasury handoff should never depend on reopening the author’s local environment to make sense.",
        ],
    },
}


def guide(owner: str) -> dict[str, object]:
    return dict(OWNER_HANDOFF_GUIDES[owner])


def signals(owner: str) -> list[str]:
    return list(OWNER_HANDOFF_GUIDES[owner]["signals"])


def questions(owner: str) -> list[str]:
    return list(OWNER_HANDOFF_GUIDES[owner]["questions"])


def handoff_notes(owner: str) -> list[str]:
    return list(OWNER_HANDOFF_GUIDES[owner]["handoff_notes"])


def guide_digest(owner: str) -> str:
    return json_digest(OWNER_HANDOFF_GUIDES[owner])


def render_markdown(owner: str) -> str:
    item = OWNER_HANDOFF_GUIDES[owner]
    lines = [f"# {owner} handoff guide", "", item["purpose"], "", "## Signals to watch"]
    lines.extend(f"- {signal}" for signal in item["signals"])
    lines.extend(["", "## Questions to answer"])
    lines.extend(f"- {question}" for question in item["questions"])
    lines.extend(["", "## Handoff notes"])
    lines.extend(f"- {note}" for note in item["handoff_notes"])
    return "\n".join(lines) + "\n"
