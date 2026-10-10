---
doc_id: scenario.tidb.tidb_business_change_x86_arm64_migration
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, business_change, tidb_business_change_x86_arm64_migration]
summary: Current code-backed contract snapshot for tidb_business_change_x86_arm64_migration; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
---

# `tidb_business_change_x86_arm64_migration`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `tidb`
- Category: `business_change`
- Scenario implementation: `src.scenarios.tidb.business_change.x86_arm64_migration.TidbBusinessChangeX86Arm64MigrationScenario`
- Formal entrypoint: `examples/run_tidb_business_change_x86_arm64_migration_scenario.py`
- Current description: Runs an offline x86-to-arm64 migration control plane with real TiDB business workload, component sequencing, monitoring retention, and rollback validation.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `offline_x86_to_arm64_online_migration` | Offline x86 to arm64 online migration with staged component replacement, business consistency, and rollback readiness. | `hard` |
| 1 | `offline_x86_to_arm64_billing_migration` | Offline x86 to arm64 billing migration with staged component replacement, payment consistency, and rollback readiness. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `offline_x86_to_arm64_online_migration`

- Case number: `0`
- Title: Offline x86 to arm64 online migration with staged component replacement, business consistency, and rollback readiness.
- Alert/symptom: [CHANGE] 订单集群必须在无互联网的维护窗口内完成从 x86 到 arm64 的在线迁移。业务不能停写，目标架构只能使用现场离线包；请先核对离线镜像目录、版本兼容性、TiUP 集群元数据备份和监控历史保留，再按监控、PD、TiKV、TiDB 的顺序分批迁移。PD 成员一次只能处理一个，TiKV 必须观察 Region/leader 均衡后才能退役旧节点，切流前必须保留可回退点。提交前用真实业务查询验证原有订单没有变化、在线请求没有丢失、查询 p95 不超过 250ms、监控历史仍可查，并确认所有 x86 节点已安全退役。环境含有旧版本镜像、历史监控、归档元数据和在线订单查询噪声；不能访问互联网，不能直接停止节点、修改业务数据或跳过一致性校验。
- Initial-state fields: `active_architecture`, `internet_access`, `monitoring_history`, `offline_bundle`, `online_writes`, `pd_members`, `tidb_nodes`, `tikv_nodes`
- Expected-target fields: `active_architecture`, `business_checksum_preserved`, `monitoring_history_preserved`, `rollback_ready`, `rpo`, `source_nodes`, `target_nodes`
- Background profiles: checkout_intent_writer, checkout_recent_lookup, checkout_reconciliation_rollup, migration_state_dashboard, offline_artifact_inventory_decoy, component_architecture_inventory_decoy, prometheus_history_retention_probe, business_checksum_probe, historical_release_manifest_decoy
- Evaluator: `src.scenarios.evaluation.tidb.business_change.x86_arm64_migration.TidbBusinessChangeX86Arm64MigrationEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.
- Calibration evidence (tool m/n): not declared in code

### `offline_x86_to_arm64_billing_migration`

- Case number: `1`
- Title: Offline x86 to arm64 billing migration with staged component replacement, payment consistency, and rollback readiness.
- Alert/symptom: [CHANGE] 结算集群必须在无互联网的维护窗口内完成从 x86 到 arm64 的在线迁移。billing-api 不能停写，目标架构只能使用现场离线包；请先核对离线镜像目录、版本兼容性、TiUP 集群元数据备份和监控历史保留，再按监控、PD、TiKV、TiDB 的顺序分批迁移。PD 成员一次只能处理一个，TiKV 必须观察 Region/leader 均衡后才能退役旧节点，切流前必须保留可回退点。提交前用真实支付查询验证原有账单没有变化、在线请求没有丢失、查询 p95 不超过 250ms、监控历史仍可查，并确认所有 x86 节点已安全退役。环境含有旧版本镜像、历史监控、归档元数据和在线支付查询噪声；不能访问互联网，不能直接停止节点、修改业务数据或跳过一致性校验。
- Initial-state fields: `active_architecture`, `internet_access`, `monitoring_history`, `offline_bundle`, `online_writes`, `pd_members`, `tidb_nodes`, `tikv_nodes`
- Expected-target fields: `active_architecture`, `business_checksum_preserved`, `monitoring_history_preserved`, `rollback_ready`, `rpo`, `source_nodes`, `target_nodes`
- Background profiles: billing_intent_writer, billing_recent_lookup, billing_reconciliation_rollup, migration_state_dashboard, offline_artifact_inventory_decoy, component_architecture_inventory_decoy, prometheus_history_retention_probe, business_checksum_probe, historical_release_manifest_decoy
- Evaluator: `src.scenarios.evaluation.tidb.business_change.x86_arm64_migration.TidbBusinessChangeX86Arm64MigrationForBillingEvaluatorCase`
- Calibration evidence (tool m/n): query_metrics=93/0; execute_sql=121/0; node_and_component_state=8/0

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

- Scenario and Case source: `src.scenarios.tidb.business_change.x86_arm64_migration.TidbBusinessChangeX86Arm64MigrationScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/tidb/business_change/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_tidb_business_change_x86_arm64_migration_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
