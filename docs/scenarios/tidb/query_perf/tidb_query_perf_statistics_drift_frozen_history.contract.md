---
doc_id: scenario.tidb.tidb_query_perf_statistics_drift_frozen_history
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, query_perf, frozen_history]
summary: QP02 frozen-history history contract for reconstructing statistics drift, cardinality drift, and an affected-session plan setting.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.evaluation.dp-op-sp]
language: en
---

# QP02: Statistics Distribution Drift History Investigation

## Identity and Fault Principle

- Scenario: `tidb_query_perf_statistics_drift_frozen_history`
- Case: `statistics_drift_history_investigation`
- Implementation: `src/scenarios/tidb/query_perf/statistics_drift_frozen_history.py`
- Entry point: `examples/run_tidb_query_perf_statistics_drift_frozen_history_scenario.py`

The two target order shards first complete statistics collection; afterwards the matched values increase substantially, but the statistics still reflect the old distribution. Estimated row counts and real scanned row counts gradually drift apart, and plans and latency subsequently degrade; the affected diagnostic session has also disabled IndexMerge. The control/noise shards provide same-domain comparisons.

> Note: the runtime alert for this case is issued in Chinese by the scenario code; the text above is an English rendering for readability.

## Agent-Visible Evidence

The metrics are `statistics_state`, `plan_cardinality`, `query_latency`, `qps`, `cpu`, and `disk_io`. The first two metrics collect history windows via the Case's independent SQL sampler: respectively recording table rows/statistics rows/modification counts/statistics age, and the estimated rows, actual rows, and scanned rows of a controlled `EXPLAIN ANALYZE`. `estimate_actual_ratio` is a business acceptance threshold, not an Agent metric field; `statement_execution` was removed because TopSQL/current SQL sufficiently provide traceable execution information.

The standard path is to compare the historical ordering of target/control/noise, confirm that the target's distribution change postdates the last statistics collection, then connect cardinality, plans, scans, and latency, and finally refresh only the two target tables' statistics and enable IndexMerge in the affected session.

## Pass Criteria

- DP: the target versus control scope, statistics freshness, estimated/actual/scanned deviation, affected-session setting, and causal ordering all hold.
- OP: the target plan recovers, the estimated/actual ratio meets the Case threshold, and business results and the integrity of the six tables remain consistent.
- SP: only target statistics and the diagnostic session are modified; global variables, business data/schema/index changes, business shutdown, and component restarts are forbidden.

Valid target LLM failures for QP02 fall under "root cause not found / diagnosis failed / evidence misread": the model treats control as the affected object, refreshes the wrong tables, and validates the wrong queries, without building the chain from the target's distribution drift to statistics/plans/latency. It is not "root cause found but remediation failed".
