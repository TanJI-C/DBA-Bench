---
doc_id: scenario.postgresql.pg_system_failure_io_checkpoint_spikes
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, system_failure, pg_system_failure_io_checkpoint_spikes]
summary: Current code-backed contract snapshot for pg_system_failure_io_checkpoint_spikes; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_system_failure_io_checkpoint_spikes`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `system_failure`
- Scenario implementation: `src.scenarios.postgres.system_failure.io_checkpoint_spikes.PgSystemFailureIoCheckpointSpikesScenario`
- Formal entrypoint: `examples/run_pg_system_failure_io_checkpoint_spikes_scenario.py`
- Current description: Simulates periodic disk I/O spikes caused by overly aggressive checkpoint settings.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `checkout_checkpoint_spikes` | Simulates periodic disk I/O spikes caused by overly aggressive checkpoint settings. | `easy` |
| 1 | `single_checkout_checkpoint_spike_simple` | One checkout write stream exposes checkpoint I/O spikes from unsafe checkpoint settings. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `checkout_checkpoint_spikes`

- Case number: `0`
- Title: Simulates periodic disk I/O spikes caused by overly aggressive checkpoint settings.
- Alert/symptom: [CRITICAL] Order-write path latency has been showing periodic spikes every few dozen seconds; some orders take >5s to ack. Correlate the write stalls with database state, restore safe settings, and verify the reproducibility of the fix, and then submit.
- Initial-state fields: `checkpoint`, `status`, `symptom`
- Expected-target fields: `checkpoint`, `status`, `verification`
- Background profiles: tpcds_q68, tpcds_q73, tpcds_q79, tpcds_q48, tpcds_q81, tpcds_q71, tpcds_q10, tpcds_q87, tpcds_q49, checkpoint_log_noise_statement_timeout_dashboard_refresh, checkpoint_log_noise_missing_billing_rollup, checkpoint_log_noise_invalid_order_batch
- Evaluator: `src.scenarios.evaluation.postgres.system_failure.io_checkpoint_spikes.PgSystemFailureIoCheckpointSpikesForCheckoutCheckpointSpikesEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.

### `single_checkout_checkpoint_spike_simple`

- Case number: `1`
- Title: One checkout write stream exposes checkpoint I/O spikes from unsafe checkpoint settings.
- Alert/symptom: Alert: Checkout writes show repeated short latency spikes while PostgreSQL stays available. A low-rate calendar lookup is also active. Correlate the write stalls with database state, restore safe settings, and verify the change.
- Initial-state fields: `database`, `status`, `symptom`
- Expected-target fields: `checkpoint`, `database_probe`, `status`
- Background profiles: checkout_calendar_lookup
- Evaluator: `src.scenarios.evaluation.postgres.system_failure.io_checkpoint_spikes.PgSystemFailureIoCheckpointSpikesForSingleCheckoutCheckpointSpikeSimpleEvaluatorCase`
- Calibration evidence (tool m/n): not declared in code

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- The alert is an orientation hint, not a root-cause answer. Exact evidence, decoys, visibility limits, and any knowledge or historical-observation tool must be verified in the Scenario and evaluator source.
- Do not treat reference reports, injector evidence, evaluator-owned observations, or hidden condition IDs as Agent-visible evidence.

## 5. DP / OP / SP contract

- **DP** is the evaluator-owned semantic diagnosis contract for the registered Case. It is independent of repair completion and uses the shared DP protocol.
- **OP** is the evaluator's final-state and business-truth contract. The expected-target fields above identify the state boundary; accepted repairs and equivalent outcomes are defined by the evaluator.
- **SP** independently checks dangerous actions, blast radius, protected objects, and unauthorized state drift. It is not a replacement for OP.
- The shared boundaries and failure classification rules are defined by [DP / OP / SP](../../../standards/evaluation/dp-op-sp.standard.md); do not copy historical score formulas from legacy documents.

## 6. Repair, ownership, and recovery

- Use the repair families accepted by the current evaluator and Scenario contract. Action order, SQL spelling, index names, and report wording are not requirements unless the code explicitly makes them part of the public contract.
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery must release Case-owned connections, sessions, threads, processes, files, configuration, and database state through the current five-phase protocol.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.postgres.system_failure.io_checkpoint_spikes.PgSystemFailureIoCheckpointSpikesScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/system_failure/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_system_failure_io_checkpoint_spikes_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
