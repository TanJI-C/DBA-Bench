---
doc_id: scenario.postgresql.pg_resource_governance_partition_cleanup
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, pg_resource_governance_partition_cleanup]
summary: Current code-backed contract snapshot for pg_resource_governance_partition_cleanup; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `pg_resource_governance_partition_cleanup`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `resource_governance`
- Scenario implementation: `src.scenarios.postgres.resource_governance.partition_cleanup.PgResourceGovernancePartitionCleanupScenario`
- Formal entrypoint: `examples/run_pg_resource_governance_partition_cleanup_scenario.py`
- Current description: Host CPU pressure caused by real filesystem-backed partition retention cleanup.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `filesystem_cleanup_pressure` | Host CPU pressure caused by filesystem-backed retention partition cleanup. | `hard` |
| 1 | `filesystem_cleanup_pressure_simple` | Simplified filesystem partition cleanup pressure with OLTP tail latency. | `easy` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `filesystem_cleanup_pressure`

- Case number: `0`
- Title: Host CPU pressure caused by filesystem-backed retention partition cleanup.
- Alert/symptom: [FIRING: WARNING] alertname=PostgresHostCpuPressure service=oltp-orders instance=postgresql-primary severity=warning summary=Host CPU pressure and OLTP tail latency exceeded SLO description=The database host had a short CPU pressure episode while transaction tail latency rose. The episode has recovered on its own. Reports, backup, and maintenance jobs were active in the same window. An application change was rolled out on this host earlier today. (Full recovery contract and case-specific observation names are published through the runtime `help` contract; the alert intentionally carries no diagnostic hints.)
- Initial-state fields: `alert`, `status`, `visible_symptom`
- Expected-target fields: `legal_hold`, `retention`, `root_cause`, `status`
- Background profiles: pc-hard-tpcds-q14, pc-hard-tpcds-q75, pc-hard-tpcds-q95
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.partition_cleanup.PgResourceGovernancePartitionCleanupForFilesystemCleanupPressureEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Fixture: `pc_hard_retention_policy` publishes the approved legal-hold list; the catalog starts with one expired partition whose `legal_hold` flag contradicts that list; after the causal chain is admitted, a live stale-config automation session (`pc-hard-config-agent`) re-applies a stored snapshot — `retention_days=30, paused=true` — onto the cleanup job every few seconds. The re-apply runs inside the helper function `aiopsbench_retention_worker_feed`, so neither `pg_stat_activity.query` nor `pg_stat_statements` shows the out-of-range UPDATE text; the session surface shows only a neutral call. The agent exits permanently when its session is terminated (fragile-automation semantics). Recovery therefore requires correlating the observed config flip-back with the active session (or its helper function) and stopping the source before fixing the job row.
- Recovery gate note: host-wide CPU PSI (`cpu_pressure_some_avg10`) is co-tenant noise on shared hosts and is reported for observability; the blocking recovery thresholds are the filesystem-I/O and OLTP latency limits plus all final-state invariants.

#### Standard diagnosis and repair path

The alert is only a host-pressure/OLTP symptom. A reference diagnosis correlates the raw
`filesystem_io` series with `bufferio_waiters`, then checks host pressure versus PostgreSQL query CPU,
and finally joins `partition_lifecycle` with the cleanup job and OLTP victim. Reports, backup,
checkpoint, and small-partition activity are same-domain noise rather than answers.

The explanatory reference repair is to bound or pause the retention worker, preserve the legal hold,
align the catalog `legal_hold` flags with the approved `pc_hard_retention_policy` list, disable the
drift-source governance job (or bring its horizon back inside the published range), correct the
cleanup job's `retention_days` back inside that range, complete all due non-hold cleanup through the
retention workflow, restore the job to enabled/unpaused, and verify the published recovery window.
OP does not require this exact SQL, order, object name, or tool sequence; a materially equivalent
batch, scheduling, or cleanup-storage change is valid.

OutcomePass requires: one attached legal-hold partition, zero detached partitions, zero due non-hold
partitions, no dropped catalog/table mismatch, no enabled governance job with a horizon outside the
published range, job enabled and unpaused with `1 <= retention_days <= max_retention_days`, and at
least `recovery_sample_count` samples within the public filesystem-I/O and OLTP p99 limits.
The filesystem-I/O bound is 60 MB/s: it allows the longer post-cleanup decoy tail (report/backup/
compressor) while still rejecting the 100+ MB/s cleanup spikes that establish the fault.
Host-wide CPU PSI is a reported observation and does not gate recovery. It does
not inspect report wording, fixed action order, or extra
reference-only queries.

### `filesystem_cleanup_pressure_simple`

- Case number: `1`
- Title: Simplified filesystem partition cleanup pressure with OLTP tail latency.
- Alert/symptom: [FIRING: WARNING] alertname=PostgresHostCpuPressure service=checkout-api instance=postgresql-primary severity=warning summary=Host pressure and checkout tail latency crossed SLO together description=Checkout latency rose during a host pressure episode that is now clear. A small number of cleanup and reporting jobs were also active. Preserve the retention boundary and legal hold. You may use the case-specific filesystem_io, bufferio_waiters, host_pressure, and partition_lifecycle observations exposed by query_metrics. For final recovery, keep the cleanup job enabled and unpaused, preserve the legal hold, remove all due non-hold partitions through the retention cleanup workflow without detached leftovers, and verify the last 2 samples are within the published filesystem-I/O and OLTP latency limits; host CPU pressure stays a reported observation.
- Initial-state fields: `alert`, `status`, `visible_symptom`
- Expected-target fields: `legal_hold`, `retention`, `root_cause`, `status`
- Background profiles: pc-easy-tpcds-q14
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.partition_cleanup.PgResourceGovernancePartitionCleanupForFilesystemCleanupPressureSimpleEvaluatorCase`

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

- Scenario and Case source: `src.scenarios.postgres.resource_governance.partition_cleanup.PgResourceGovernancePartitionCleanupScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/resource_governance/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_resource_governance_partition_cleanup_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
