from __future__ import annotations

from engineering_challenge.utils import json_digest


BRIEF_TEMPLATES = {
    "content_ops": {
        "headline": "Classifier and content brief",
        "intro": "Use this brief when content reviewers need a quick view of routing language, extraction drift, and whether audit evidence is still replayable.",
        "metric_callouts": [
            "public-hidden gap by bundle",
            "field-coverage warnings",
            "watch-band bundle count",
            "owner dashboard trend",
        ],
        "prompts": [
            "Which classifier bundles changed wording without a matching release note update?",
            "Did any packet validation issues land after the last content review?",
            "Are hidden extraction cases still harder than public walkthroughs in a useful way?",
        ],
        "closing": "Content teams should attach the release note excerpt and packet digest when the bundle enters a manual review lane.",
    },
    "education_ops": {
        "headline": "Seat allocation brief",
        "intro": "Education reviewers care about fairness, roster timing, and whether partner-facing notes explain the operational change without making the score harder to interpret.",
        "metric_callouts": [
            "hidden-score drift",
            "watch-band partner bundles",
            "release train capacity",
            "public-hidden variance",
        ],
        "prompts": [
            "Did any seat-allocation bundle become partner-facing without a fairness note?",
            "Which owners are close to their weekly capacity ceiling for the next train?",
            "Are hidden cases still the leading indicator for roster-timing problems?",
        ],
        "closing": "If partner-facing wording changed, include the escalation path in the brief, not only in the audit packet.",
    },
    "finance_ops": {
        "headline": "Closeout and billing brief",
        "intro": "Finance uses the brief to connect score movement with release risk, audit readiness, and close-window sensitivity.",
        "metric_callouts": [
            "ready-band holdouts",
            "closeout public-hidden gap",
            "audit export freshness",
            "retention plan pressure",
        ],
        "prompts": [
            "What changed between the last ready closeout bundle and the current watch or blocked bundle?",
            "Did any retention or audit rule become the real blocker instead of the score?",
            "Are reserve or billing bundles following the same failure pattern as closeout bundles?",
        ],
        "closing": "Include both scorecard movement and release-note context so treasury does not have to infer the reason for a hold.",
    },
    "logistics_ops": {
        "headline": "Warehouse routing brief",
        "intro": "Routing briefs are built for operators who need to separate stale warehouse assumptions from runtime queue pressure.",
        "metric_callouts": [
            "route-capacity blockers",
            "queue-latency spikes",
            "owner blackout conflicts",
            "exception-repair mismatch count",
        ],
        "prompts": [
            "Which blocked rows are really content issues and which are calendar issues?",
            "Did warehouse blackouts reduce schedule options even though quota remained?",
            "Are repair instructions staying consistent across notes, tags, and hidden cases?",
        ],
        "closing": "Routing owners should add a sentence about facility or zone changes whenever the brief is used for release approval.",
    },
    "platform_ops": {
        "headline": "Runtime and fulfillment brief",
        "intro": "Platform looks for runtime normalization problems, worker-version drift, and packet field coverage that could make a failure expensive to debug later.",
        "metric_callouts": [
            "worker-version shift",
            "queue-latency outliers",
            "execution timeout clusters",
            "manifest digest drift",
        ],
        "prompts": [
            "Did the latest failures line up with a worker-version change?",
            "Are replay artifacts still sufficient to reproduce the slow or failing path?",
            "Would a release-note update clarify the operational change without code spelunking?",
        ],
        "closing": "When platform signs off, the brief should say whether the issue was runtime, content, or policy.",
    },
    "procurement_ops": {
        "headline": "Vendor settlement brief",
        "intro": "Procurement uses the brief to understand dispute handling, settlement exception trends, and whether the support handoff is clear enough for release week.",
        "metric_callouts": [
            "vendor exception rate",
            "blocked dispute cases",
            "partner retention impact",
            "support review queue",
        ],
        "prompts": [
            "Which settlement failures need a content fix and which need a release-note fix?",
            "Did procurement and support use the same dispute terms in the last two releases?",
            "Is the packet complete enough to replay a partner escalation if needed?",
        ],
        "closing": "If a partner export exists, the brief should mention the retention horizon explicitly.",
    },
    "returns_ops": {
        "headline": "Returns recovery brief",
        "intro": "Returns owners watch runtime noise, recovery wording, and whether the queue or the content is the real reason a bundle is slipping.",
        "metric_callouts": [
            "retryable timeout count",
            "returns hidden drift",
            "review-state balance",
            "owner capacity pressure",
        ],
        "prompts": [
            "Did the bundle slow down because of runtime, or did the expected answer set drift?",
            "Are returns notes and release artifacts saying the same thing about the current workflow?",
            "Would the next train be safer after a reviewer capacity shift rather than a code change?",
        ],
        "closing": "Returns briefs should always include the retry horizon when runtime is part of the story.",
    },
    "revops": {
        "headline": "Recurring billing and ledger brief",
        "intro": "Revops needs to see entitlement drift, audit export quality, and whether the same patterns are showing up in billing and ledger bundles.",
        "metric_callouts": [
            "owner bundle matrix",
            "digest drift summary",
            "hidden-case spread",
            "audit queue latency",
        ],
        "prompts": [
            "Did the release note explain the change as clearly as the scorecard did?",
            "Are the billing bundles slowly decaying or did one release create the spike?",
            "Which issue belongs to revops and which one needs finance or platform review?",
        ],
        "closing": "Attach the relevant manifest digest and owner-average trend whenever the brief leads to a hold decision.",
    },
    "risk_ops": {
        "headline": "Identity and controls brief",
        "intro": "Risk cares about hidden-case decay, partner-control wording, and evidence completeness. The brief should make it obvious when the score is not the main problem anymore.",
        "metric_callouts": [
            "hidden-gap watchlist",
            "field coverage warnings",
            "partner channel mix",
            "audit review latency",
        ],
        "prompts": [
            "Which risk bundles are blocked by evidence instead of by score?",
            "Did partner-control wording change without a matching review note?",
            "Are hidden cases still acting as the leading signal for risk drift?",
        ],
        "closing": "Risk briefs should call out the difference between acceptable watch-band noise and true control regressions.",
    },
    "sales_ops": {
        "headline": "Pricing handoff brief",
        "intro": "Sales uses the brief to see whether pricing policy, release notes, and validation behavior all moved together or whether one piece lagged behind.",
        "metric_callouts": [
            "validation mismatch rate",
            "public-hidden pricing gap",
            "release digest movement",
            "holdout bundle count",
        ],
        "prompts": [
            "Did discount-rule wording shift more than the expected answers did?",
            "Would a release-note rewrite unblock review faster than a score threshold change?",
            "Are pricing bundles starting to resemble finance bundles in their failure pattern?",
        ],
        "closing": "Include the policy text that changed, not only a summary label, when the brief is used for approval.",
    },
    "support_ops": {
        "headline": "Claims intake brief",
        "intro": "Support needs to separate taxonomy drift from escalation drift and keep a steady view of which bundles are consuming review time.",
        "metric_callouts": [
            "review-state owner matrix",
            "support queue latency",
            "blocked escalation bundles",
            "owner average percent",
        ],
        "prompts": [
            "Did an escalation wording change land without updated hidden cases?",
            "Which blocked bundles actually belong in a content review lane instead of support review?",
            "Did queue pressure make the score movement look worse than it is?",
        ],
        "closing": "Support briefs should name the owner handoff path so reviewers know whether to route issues to risk, content, or release ops.",
    },
    "treasury_ops": {
        "headline": "Reserve and treasury brief",
        "intro": "Treasury uses the brief when reserve and payout-gate bundles affect close timing or require a retention decision before cleanup.",
        "metric_callouts": [
            "reserve hidden drift",
            "archive versus prune candidates",
            "closeout adjacency",
            "audit packet age",
        ],
        "prompts": [
            "Did reserve behavior drift without a matching update in the payout gate notes?",
            "Are we trying to prune rows that still need to be held for audit?",
            "Which blocked bundles need finance review before the next close train?",
        ],
        "closing": "Always include the retention action summary when the brief is used in a close or payout review.",
    },
}


def owners() -> list[str]:
    return sorted(BRIEF_TEMPLATES)


def brief_for_owner(owner: str) -> dict[str, object]:
    return dict(BRIEF_TEMPLATES[owner])


def owner_prompt_cards(owner: str) -> list[str]:
    return list(BRIEF_TEMPLATES[owner]["prompts"])


def metric_callouts(owner: str) -> list[str]:
    return list(BRIEF_TEMPLATES[owner]["metric_callouts"])


def brief_digest(owner: str) -> str:
    return json_digest(BRIEF_TEMPLATES[owner])


def render_brief(owner: str, title: str, summary_lines: list[str]) -> str:
    template = BRIEF_TEMPLATES[owner]
    lines = [f"# {title}", "", template["intro"], "", "## Metric callouts"]
    lines.extend(f"- {item}" for item in template["metric_callouts"])
    lines.extend(["", "## Summary"])
    lines.extend(f"- {line}" for line in summary_lines)
    lines.extend(["", "## Review prompts"])
    lines.extend(f"- {item}" for item in template["prompts"])
    lines.extend(["", template["closing"]])
    return "\n".join(lines) + "\n"
