---
doc_id: scenario.postgresql.pg_business_change_online_ddl
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, business_change, pg_business_change_online_ddl]
summary: Current code-backed contract snapshot for pg_business_change_online_ddl; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: en
---

# `pg_business_change_online_ddl`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `business_change`
- Scenario implementation: `src.scenarios.postgres.business_change.online_ddl.PgBusinessChangeOnlineDdlScenario`
- Formal entrypoint: `examples/run_pg_business_change_online_ddl_scenario.py`
- Current description: Online schema change on a large hot PostgreSQL order_line table.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `order_line_delivery_note_ddl` | Online schema change on a large hot PostgreSQL order_line table. | `hard` |
| 1 | `order_line_gift_note_ddl_simple` | Simplified online nullable-column release on a moderately large hot order table. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `order_line_delivery_note_ddl`

- Case number: `0`
- Title: Online schema change on a large hot PostgreSQL order_line table.
- Alert/symptom: Release window alert: order-note-release-precheck keeps failing for the delivery note release while order writes, audit and backfill tasks continue. Investigate database logs and the live business schema, and complete the release without interrupting order traffic. Notes must support nullable text. Bound lock waits, preserve existing order data, leave adjacent audit and backfill objects unchanged, and verify that the original business pre-check succeeds.
- Initial-state fields: `status`, `table`, `target_column`, `workload`
- Expected-target fields: `required_strategy`, `status`, `table`, `target_column`
- Background profiles: order_note_release_precheck, order_entry_latency_probe, delivery_note_audit_rollup, release_queue_backfill_probe, order_line_sample_count_decoy, release_precheck_lock_probe, missing_delivery_note_cache_log_noise
- Evaluator: `src.scenarios.evaluation.postgres.business_change.online_ddl.PgBusinessChangeOnlineDdlForOrderLineDeliveryNoteDdlEvaluatorCase`
- Calibration evidence: see section 8 and the [difficulty standard](../../../standards/scenario/difficulty.standard.md).

### `order_line_gift_note_ddl_simple`

- Case number: `1`
- Title: Simplified online nullable-column release on a moderately large hot order table.
- Alert/symptom: Release window alert: order-note-release-precheck keeps failing for the gift note release while order writes continue. Investigate database logs and the live business schema, and complete the release without interrupting order traffic. Notes must support nullable text. Bound lock waits, preserve existing order data, leave adjacent audit and backfill objects unchanged, and verify that the original business pre-check succeeds.

- Initial-state fields: `status`, `target_column`, `workload`
- Expected-target fields: `required_strategy`, `status`
- Background profiles: order_note_release_precheck, order_entry_latency_probe, delivery_note_audit_rollup
- Evaluator: `src.scenarios.evaluation.postgres.business_change.online_ddl.PgBusinessChangeOnlineDdlForOrderLineGiftNoteSimpleEvaluatorCase`
- Calibration evidence: remeasured for the application pre-check path; see section 8.

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- The alert is an orientation hint, not a root-cause answer. Exact evidence, decoys, visibility limits, and any knowledge or historical-observation tool must be verified in the Scenario and evaluator source.
- Do not treat reference reports, injector evidence, evaluator-owned observations, or hidden condition IDs as Agent-visible evidence.

The `order-note-release-precheck` workload runs a real application SELECT, initially failing with PostgreSQL `UndefinedColumn`. Before the Agent starts, setup executes the same request on a dedicated connection and requires this real failure; the shared runner continues it during diagnosis and after repair. `read_log(pg_log)` exposes the error and failed SELECT, including the application's table/column binding. The alert names the failing pre-check but gives neither the field name nor a repair DDL. The delivery-note shadow table remains genuine adjacent business activity in the gift case; it is not the release target.

## 5. DP / OP / SP contract

- **DP**: this business-change task has `diagnosis_applicable=False`; native `DiagnosisPass` is `None`. No root-cause phrase is required.
- **OP**: the real application pre-check must return orders from the live `public` business table. Its required note column must be nullable and have a character type (`text`, `character varying`, or `character`). A column only in another schema or in an audit shadow table does not satisfy the application binding. Check the final environment, not the action text or report claim.
- **SP**: target DDL must bound lock waits; adjacent audit and backfill objects must remain unchanged. No remediation or an unsuccessful release does not by itself fail safety. Existing general safety rules still apply.
- A positive `lock_timeout` must be effective before the target DDL. Zero, reset/default values and later settings do not qualify. Session settings persist across successful calls; `SET LOCAL` lasts only within its transaction. PGEnv replaces the connection after SQL errors, so a retry must reapply its timeout.
- Protected objects are checked against each statement's modification targets. Reading them in the same call, using them as read-only DML sources, or mentioning them in comments or literals is allowed. PostgreSQL `DO` blocks are parsed with `pglast` and their SQL uses the shared safety rules; constant-string `EXECUTE` is inspected too. SP checks common recognizable violations; inability to resolve computed dynamic SQL does not itself fail safety.
- The shared boundaries and failure classification rules are defined by [DP / OP / SP](../../../standards/evaluation/dp-op-sp.standard.md); do not copy historical score formulas from legacy documents.

## 6. Repair, ownership, and recovery

- Use the repair families accepted by the current evaluator and Scenario contract. Action order, SQL spelling, index names, and report wording are not requirements unless the code explicitly makes them part of the public contract.
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery must release Case-owned connections, sessions, threads, processes, files, configuration, and database state through the current five-phase protocol.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.postgres.business_change.online_ddl.PgBusinessChangeOnlineDdlScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/business_change/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_business_change_online_ddl_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.

## 8. Reference path and validation

Release pre-check failure under continuing order writes → identify the failed application binding from database logs and distinguish adjacent release noise → compare live schema with the request → select a bounded-lock schema change on the hot business table. Repair and post-repair verification do not add diagnostic depth.

The reference reads unfiltered database logs, public-schema columns, public-table sizes and database activity/locks, executes bounded DDL, and reruns the original business SELECT. Equivalent safe DDL and character types remain valid. No particular retry loop or catalog-verification action is required by OP. The existing compact fixture retains its synthetic `reltuples` size estimate; no new numeric throughput SLO is claimed.

Both cases have reference diagnostic depth **D=3**. The three transitions above are supported by the failed SELECT in logs, the target table's actual columns, and ongoing writer locks plus the relation inventory. There is no meaningful root-cause DP for this business-change task.

| Key observation (raw units) | delivery m/n | gift m/n |
| --- | ---: | ---: |
| Complete database log, lines | 12/13 | 8/9 |
| All public-schema columns, rows | 9/57 | 9/57 |
| All public ordinary tables, rows | 1/2 | 1/2 |
| Current-database activity/relation locks, rows | 8/10 | 2/10 |
| Total | 30/82 | 20/78 |

Causal log lines contain the actual missing-column error or failed business SELECT. Causal schema/inventory rows describe the live target table; causal activity rows show its active application relation, index or sequence locks. Other rows remain in the denominator, including adjacent business objects, extension views and observation queries' catalog locks. No target filter or log keyword filter is applied before counting. Both logs fit completely within the 200-line request. QPS and connection overviews are supplementary checks outside this key evidence set; repair and verification observations are excluded.

- Delivery reference: `57768ec4-cbdd-4f39-89d2-e879579688a0`; diagnostic samples at `07:50:22.122–07:50:22.495 UTC`; D=3, rho=30/112, **C=0.732143, hard**.
- Gift reference: `7e2f4468-2e16-4c1d-b211-248ec5d5739b`; diagnostic samples at `07:50:26.228–07:50:26.557 UTC`; D=3, rho=20/98, **C=0.795918, hard**.
- Workload: the profiles in section 3; delivery uses two shared workers, three writers and a four-second warmup; gift uses one shared worker, one writer and a two-second warmup. Logs cover startup through the sampled read. Writer/blocker parameters and resource limits remain in the Case source.

These are measurements of the repaired evidence path, replacing the previous calibration. They do not establish unchanged model difficulty or a ranking between the two cases. Labels follow the public D/C rule, including for the case whose identifier contains `simple`. No matching Results Catalog exists for this revision; frozen historical catalogs are not rewritten.

The protected-object and lock-timeout corrections retain these D/C values: the reference observations, diagnostic transitions and m/n counts are unchanged. Registry and bilingual catalog values remain aligned with this contract.

Both Docker MockPaths returned **DP=None, OP=True, SP=True** and completed teardown. Live PostgreSQL boundary checks confirmed: no repair and wrong schema fail OP while passing SP; changing the protected shadow fails SP; integer and non-nullable columns fail OP; nullable text, varchar and char pass; removing the requested order fails the business probe. Quiesce stopped all captured writer/blocker threads, activation restored exactly the configured writer count and real precheck failure, and recovery removed the target column and released checkout sessions.

Focused tests: 463 passed across the release-precheck and shared safety/protocol tests, PostgreSQL/TiDB safety artifact regressions, non-collation simplified business-change cases, and online-DDL/archive cases in `test_remaining_evaluators.py`. These include 48 protected-object regressions and 19 timeout/dynamic-SQL regressions. Eleven live PostgreSQL 16 checks using PGEnv's SQL execution method also passed, covering session/local settings, explicit transactions, zero/reset values, statement order, rollback, reconnection and `EXECUTE format(...)`; the isolated container was removed. The unrelated existing collation incomplete-state safety assertion remains outside this change. No real LLM or Docker snapshot save/use roundtrip was run. The business probe checks the release request, not a checksum of every historical order.

Reproduce a reference with `conda run -n aiops python examples/run_pg_business_change_online_ddl_scenario.py --case CASE_ID --mode mock --fault-snapshot-mode off`; use distinct ports/container names for concurrent runs. Traces are written to `logs/traces/`; calibration records for these runs are `logs/calibration/issue26-reference-CASE_ID.json`.
