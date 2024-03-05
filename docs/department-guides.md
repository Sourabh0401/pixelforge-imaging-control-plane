# Department Guides

The challenge program is organized around department lanes rather than one flat queue of bundles. That keeps expectations honest. Kernel drills have very different review signals from finance drills, and the release path should reflect that.

## Current lane model

The control plane supports the following department families:

- kernel and systems runtime
- database internals and data recovery
- networking and protocol handling
- compiler and parser tooling
- cryptography and secure transport
- graphics and rendering pipelines
- distributed systems and coordination
- QA, fuzzing, and failure analysis
- data engineering and schema evolution
- financial engines and exact arithmetic
- platform integration and cross-lane drills

Each lane still uses the same durable artifacts:

1. A bundle with metadata, case rows, review expectations, and release notes.
2. Submission payloads that can be replayed into a stable execution transcript.
3. A scorecard with public, hidden, and section-level signals.
4. A release manifest and audit packet for downstream review.

## What lane ownership changes

Lane ownership affects more than dashboard grouping.

- section weights differ by owner and by release channel
- operator playbooks call out different evidence requirements
- rollout quotas are not shared evenly across every lane
- audit repair routing goes to different owner groups
- history rollups need to preserve lane context for trend analysis

That is why the code keeps catalog policy, scoring, release gates, and evidence routing as separate modules instead of flattening everything into one report generator.

## Example mapping

In the current fixture corpus, bundle ids still use legacy internal names such as `merchant-closeout`, `warehouse-routing`, and `fulfillment-ledger`. In production, those map to broader lane families:

- `merchant-closeout` and `vendor-settlement` fit the financial engine lane
- `warehouse-routing` and `seat-allocation` fit platform and systems routing lanes
- `document-classifier` and `claims-intake` fit data engineering and review automation lanes
- `fulfillment-ledger` and `reserve-rollforward` fit cross-team release and audit lanes

That legacy naming is intentional. It gives us realistic data with durable history, while the control plane itself stays general enough to handle a wider department program.
