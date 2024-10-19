from __future__ import annotations

from engineering_challenge.utils import json_digest


QUERY_SPECS = (
    {
        "query_id": "owner-trend-rollup",
        "title": "Owner trend rollup",
        "tables": ("history_import",),
        "parameters": ("owner", "since", "until"),
        "owner": "release_ops",
        "description": "Monthly owner trend with blended, public, and hidden percentages so release leads can see whether a support issue is localized or systemic.",
        "sql": """
select
  owner,
  substr(started_at, 1, 7) as month_bucket,
  count(*) as run_count,
  round(avg(percent), 2) as average_percent,
  round(avg(hidden_percent), 2) as average_hidden_percent,
  round(avg(json_extract(payload_json, '$.public_percent')), 2) as average_public_percent
from history_import
where owner = :owner
  and started_at >= :since
  and started_at < :until
group by owner, month_bucket
order by month_bucket desc
""".strip(),
    },
    {
        "query_id": "channel-band-mix",
        "title": "Channel band mix",
        "tables": ("history_import",),
        "parameters": ("release_channel", "since"),
        "owner": "release_ops",
        "description": "Breakdown of ready, watch, and blocked rows by channel so a release manager can see whether one rollout path is carrying unusual operational risk.",
        "sql": """
select
  release_channel,
  band,
  count(*) as row_count,
  round(avg(percent), 2) as average_percent
from history_import
where release_channel = :release_channel
  and started_at >= :since
group by release_channel, band
order by release_channel, band
""".strip(),
    },
    {
        "query_id": "hidden-gap-watchlist",
        "title": "Hidden gap watchlist",
        "tables": ("history_import",),
        "parameters": ("gap_floor", "since"),
        "owner": "risk_ops",
        "description": "Rows where the public-hidden gap is large enough to require a manual read even if the total score is still above the nominal release threshold.",
        "sql": """
select
  history_id,
  bundle_id,
  owner,
  percent,
  hidden_percent,
  json_extract(payload_json, '$.public_percent') as public_percent,
  round(json_extract(payload_json, '$.public_percent') - hidden_percent, 2) as gap
from history_import
where started_at >= :since
  and (json_extract(payload_json, '$.public_percent') - hidden_percent) >= :gap_floor
order by gap desc, started_at desc
""".strip(),
    },
    {
        "query_id": "queue-latency-outliers",
        "title": "Queue latency outliers",
        "tables": ("history_import",),
        "parameters": ("latency_floor",),
        "owner": "platform_ops",
        "description": "Slow review rows grouped with owner and release channel so the platform team can separate runtime pressure from content drift.",
        "sql": """
select
  history_id,
  owner,
  bundle_id,
  release_channel,
  json_extract(payload_json, '$.queue_latency_ms') as queue_latency_ms,
  started_at
from history_import
where json_extract(payload_json, '$.queue_latency_ms') >= :latency_floor
order by queue_latency_ms desc, started_at desc
""".strip(),
    },
    {
        "query_id": "owner-capacity-pressure",
        "title": "Owner capacity pressure",
        "tables": ("history_import",),
        "parameters": ("owner", "since"),
        "owner": "content_ops",
        "description": "Counts how many blocked and watch rows piled up for one owner in the recent window to support weekly staffing and blackout decisions.",
        "sql": """
select
  owner,
  band,
  count(*) as row_count,
  round(avg(percent), 2) as average_percent,
  min(started_at) as first_seen,
  max(started_at) as last_seen
from history_import
where owner = :owner
  and started_at >= :since
group by owner, band
order by row_count desc, band
""".strip(),
    },
    {
        "query_id": "bundle-digest-drift",
        "title": "Bundle digest drift",
        "tables": ("history_import",),
        "parameters": ("bundle_id",),
        "owner": "audit_ops",
        "description": "Shows the digest history for a bundle so auditors can tell whether packet or release changes coincide with scoring movement.",
        "sql": """
select
  bundle_id,
  json_extract(payload_json, '$.artifact_digest') as artifact_digest,
  count(*) as row_count,
  min(started_at) as first_seen,
  max(started_at) as last_seen
from history_import
where bundle_id = :bundle_id
group by bundle_id, artifact_digest
order by last_seen desc
""".strip(),
    },
    {
        "query_id": "review-state-balance",
        "title": "Review state balance",
        "tables": ("history_import",),
        "parameters": ("since",),
        "owner": "support_ops",
        "description": "Summarizes auto, owner, support, and audit review states by owner to show where human review effort is actually landing.",
        "sql": """
select
  owner,
  json_extract(payload_json, '$.review_state') as review_state,
  count(*) as row_count,
  round(avg(percent), 2) as average_percent
from history_import
where started_at >= :since
group by owner, review_state
order by owner, review_state
""".strip(),
    },
    {
        "query_id": "worker-version-shift",
        "title": "Worker version shift",
        "tables": ("history_import",),
        "parameters": ("since",),
        "owner": "platform_ops",
        "description": "Compares worker versions against score movement to help isolate operational shifts from content changes.",
        "sql": """
select
  json_extract(payload_json, '$.worker_version') as worker_version,
  count(*) as row_count,
  round(avg(percent), 2) as average_percent,
  round(avg(hidden_percent), 2) as average_hidden_percent
from history_import
where started_at >= :since
group by worker_version
order by worker_version
""".strip(),
    },
    {
        "query_id": "ready-band-holdouts",
        "title": "Ready band holdouts",
        "tables": ("history_import",),
        "parameters": ("owner", "since"),
        "owner": "release_ops",
        "description": "Rows that are close to ready but still blocked by policy or hidden-gap conditions. Useful when a release train is almost full and owners want to know what is one step away.",
        "sql": """
select
  history_id,
  bundle_id,
  owner,
  percent,
  hidden_percent,
  band,
  started_at
from history_import
where owner = :owner
  and started_at >= :since
  and band in ('watch', 'blocked')
  and percent >= 80.0
order by percent desc, started_at desc
""".strip(),
    },
    {
        "query_id": "owner-bundle-matrix",
        "title": "Owner bundle matrix",
        "tables": ("history_import",),
        "parameters": ("since",),
        "owner": "reporting_ops",
        "description": "Owner and bundle level averages for portfolio summaries and release briefs.",
        "sql": """
select
  owner,
  bundle_id,
  count(*) as run_count,
  round(avg(percent), 2) as average_percent,
  round(avg(hidden_percent), 2) as average_hidden_percent
from history_import
where started_at >= :since
group by owner, bundle_id
order by owner, bundle_id
""".strip(),
    },
    {
        "query_id": "policy-flag-frequency",
        "title": "Policy flag frequency",
        "tables": ("history_import",),
        "parameters": ("since",),
        "owner": "risk_ops",
        "description": "A rough inventory of rows carrying policy flags so owners can see whether review friction is a one-off or a pattern.",
        "sql": """
select
  owner,
  case
    when payload_json like '%requires-review%' then 'requires-review'
    when payload_json like '%public-hidden-gap%' then 'public-hidden-gap'
    else 'none'
  end as flag_group,
  count(*) as row_count
from history_import
where started_at >= :since
group by owner, flag_group
order by owner, flag_group
""".strip(),
    },
    {
        "query_id": "bundle-release-channel-mix",
        "title": "Bundle release channel mix",
        "tables": ("history_import",),
        "parameters": ("bundle_id",),
        "owner": "release_ops",
        "description": "Shows how one bundle moved through channels over time. Useful for validating whether a partner release is really new or simply the latest stop in a longer path.",
        "sql": """
select
  bundle_id,
  release_channel,
  count(*) as row_count,
  min(started_at) as first_seen,
  max(started_at) as last_seen
from history_import
where bundle_id = :bundle_id
group by bundle_id, release_channel
order by last_seen desc
""".strip(),
    },
    {
        "query_id": "support-review-latency",
        "title": "Support review latency",
        "tables": ("history_import",),
        "parameters": ("since",),
        "owner": "support_ops",
        "description": "Focuses on rows that landed in support review and correlates their latency with owner and bundle.",
        "sql": """
select
  owner,
  bundle_id,
  json_extract(payload_json, '$.queue_latency_ms') as queue_latency_ms,
  started_at
from history_import
where started_at >= :since
  and json_extract(payload_json, '$.review_state') = 'support'
order by queue_latency_ms desc, started_at desc
""".strip(),
    },
    {
        "query_id": "audit-review-latency",
        "title": "Audit review latency",
        "tables": ("history_import",),
        "parameters": ("since",),
        "owner": "risk_ops",
        "description": "Captures the audit-side queue so the team can separate evidence problems from general review backlog.",
        "sql": """
select
  owner,
  bundle_id,
  json_extract(payload_json, '$.queue_latency_ms') as queue_latency_ms,
  started_at
from history_import
where started_at >= :since
  and json_extract(payload_json, '$.review_state') = 'audit'
order by queue_latency_ms desc, started_at desc
""".strip(),
    },
    {
        "query_id": "owner-score-volatility",
        "title": "Owner score volatility",
        "tables": ("history_import",),
        "parameters": ("owner", "since"),
        "owner": "reporting_ops",
        "description": "Min/max spread for one owner over a time window. Helps explain why an average can look calm when the underlying runs are not.",
        "sql": """
select
  owner,
  min(percent) as min_percent,
  max(percent) as max_percent,
  round(max(percent) - min(percent), 2) as spread
from history_import
where owner = :owner
  and started_at >= :since
group by owner
""".strip(),
    },
    {
        "query_id": "bundle-hidden-drift",
        "title": "Bundle hidden drift",
        "tables": ("history_import",),
        "parameters": ("bundle_id", "since"),
        "owner": "risk_ops",
        "description": "Hidden score movement for a single bundle over time, grouped by month. This is the quickest way to confirm whether a bundle is decaying quietly.",
        "sql": """
select
  bundle_id,
  substr(started_at, 1, 7) as month_bucket,
  round(avg(hidden_percent), 2) as average_hidden_percent,
  round(avg(percent), 2) as average_percent
from history_import
where bundle_id = :bundle_id
  and started_at >= :since
group by bundle_id, month_bucket
order by month_bucket desc
""".strip(),
    },
    {
        "query_id": "review-state-owner-matrix",
        "title": "Review state owner matrix",
        "tables": ("history_import",),
        "parameters": ("since",),
        "owner": "support_ops",
        "description": "Cross-owner view of review states, intended for staffing and handoff conversations.",
        "sql": """
select
  owner,
  json_extract(payload_json, '$.review_state') as review_state,
  count(*) as row_count
from history_import
where started_at >= :since
group by owner, review_state
order by review_state, owner
""".strip(),
    },
    {
        "query_id": "owner-band-latency-cross",
        "title": "Owner band latency cross",
        "tables": ("history_import",),
        "parameters": ("since",),
        "owner": "platform_ops",
        "description": "Correlates queue latency with score band for each owner. Useful when a release train slowed down and the team wants to know whether quality or capacity drove it.",
        "sql": """
select
  owner,
  band,
  round(avg(json_extract(payload_json, '$.queue_latency_ms')), 2) as average_queue_latency_ms,
  count(*) as row_count
from history_import
where started_at >= :since
group by owner, band
order by owner, band
""".strip(),
    },
)


def queries() -> list[dict[str, object]]:
    return [dict(spec) for spec in QUERY_SPECS]


def query_spec(query_id: str) -> dict[str, object]:
    for spec in QUERY_SPECS:
        if spec["query_id"] == query_id:
            return dict(spec)
    raise KeyError(query_id)


def render_sql(query_id: str) -> str:
    return str(query_spec(query_id)["sql"]) + "\n"


def parameter_names(query_id: str) -> tuple[str, ...]:
    return tuple(query_spec(query_id)["parameters"])


def requires_tables(query_id: str) -> tuple[str, ...]:
    return tuple(query_spec(query_id)["tables"])


def queries_for_owner(owner: str) -> list[dict[str, object]]:
    return [dict(spec) for spec in QUERY_SPECS if spec["owner"] == owner]


def digest(query_id: str) -> str:
    return json_digest(query_spec(query_id))


def markdown_catalog() -> str:
    lines = ["# Saved query catalog", ""]
    for spec in QUERY_SPECS:
        lines.append(f"## {spec['title']}")
        lines.append(f"- id: `{spec['query_id']}`")
        lines.append(f"- owner: `{spec['owner']}`")
        lines.append(f"- tables: {', '.join(spec['tables'])}")
        lines.append(f"- parameters: {', '.join(spec['parameters']) or 'none'}")
        lines.append(f"- description: {spec['description']}")
        lines.append("")
    return "\n".join(lines) + "\n"
