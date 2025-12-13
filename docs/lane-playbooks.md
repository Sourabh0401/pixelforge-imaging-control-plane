# Lane playbooks

Lane playbooks are the human companion to the machine summaries. They tell operators what to inspect first, what a safe warning looks like, and when to stop and escalate.

## Why playbooks stay lane-specific

A JPEG fidelity lane and a partner export lane may both fail in one release week, but the right response is rarely the same. Playbooks keep the repo honest about that.

## Common playbook sections

- what the lane protects
- first-pass triage
- required artifacts
- release questions
- escalation map
- common mistakes

## What should not happen

If operators keep writing the same explanation in handoffs because the playbook is silent, the playbook needs to grow. If the playbook conflicts with the machine summary, the lane contract needs attention.
