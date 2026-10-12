---
doc_id: scenario.persistent-scenario.pg-continuous-ops-smoke
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: agent_safe
scope: [postgres, persistent-scenario, pg-continuous-ops]
summary: Defines the PostgreSQL Persistent Scenario smoke contract with one durable mailbox session, asynchronous events, and persistent business-state evaluation.
source_of_truth: code
related: [standard.persistent-scenario.architecture, standard.persistent-scenario.evaluation, guide.persistent-scenario.implement-persistent-scenario]
language: en
---

# `pg_continuous_ops_smoke`

This is the development configuration for the PostgreSQL long-running Persistent Scenario. A TPC-DS scale 1 environment is deployed exactly once from warmup to horizon, and two events arrive on a fixed timeline, with the later Event not waiting for the previous Event's processing to finish. The entire run creates only one persistent `session-0001` and one LLM conversation.

Visible work items are written to the mailbox after their impact is confirmed; invisible system changes are not explained directly to the Agent. The scheduler only appends ordinary routine-check tasks to the same mailbox at a fixed cadence. What the Agent perceives is database state changes and ordinary operational work; it does not know which internal mechanism a task came from. The Agent-facing Persistent Scenario control plane has a single `mailbox` tool: `read` reads pending/completed in one call, `write` completes one or more tasks in a single call and saves a structured report, and `wait` suspends the same conversation while the mailbox is empty until a new task arrives. The report of an alert task serves as input to the corresponding Diagnosis matcher; the report of a periodic task is only an audit record. The Mailbox is not responsible for verifying fixes and does not directly decide Outcome/Safety.

The two events in the current smoke YAML still explicitly use `trigger: alert`, so the existing no-agent / calibration gate semantics are unchanged. Ordinary routine-check tasks, trusted state checks, deadlines, verification, mailbox lifecycle, `active/idle/woken` states, raw/phase conversation traces, and single-session wakeup semantics are covered by the Persistent Scenario engine's focused tests.

The four business flows respectively cover the affected `customer_profile_write`, unaffected write/read control flows, and the `customer_integrity_probe` used only for correctness verification. Business SLOs are computed in fixed buckets starting from the end of warmup; Event 1 enters only the operational-risk objective, avoiding fabricating a frontend-latency event out of cleanup-horizon risk.

`calibration.status=development_provisional` only allows the development Gate and focused tests. Formal experiments must use a `validated` calibration artifact with evidence IDs; the runner will not warn and then continue.

Legacy-format traces are kept only as historical counterexamples; they cannot be read by the `persistent-scenario-v1` loader, trace reader, or aggregate.
