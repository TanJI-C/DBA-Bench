---
doc_id: scenario.postgresql.pg_resource_governance_resource_throttling
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [postgres, resource_governance, pg_resource_governance_resource_throttling]
summary: Current code-backed contract snapshot for pg_resource_governance_resource_throttling; includes its registered Cases, state boundary, evaluator identity, and calibration status.
source_of_truth: code
related: [catalog.postgresql-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `pg_resource_governance_resource_throttling`

> This is the current registry-backed Scenario contract. Read the database catalog for navigation, then verify mechanism, evidence, outcome, safety, and recovery in the linked source code before changing the implementation.

## 1. Identity and scope

- Database: `postgresql`
- Category: `resource_governance`
- Scenario implementation: `src.scenarios.postgres.resource_governance.resource_throttling.PgResourceGovernanceResourceThrottlingScenario`
- Formal entrypoint: `examples/run_pg_resource_governance_resource_throttling_scenario.py`
- Current description: Simulates mixed OLTP and reporting workload contention and requires role-level resource isolation.

## 2. Current Case set

| case_no | case_id | title | current label |
| ---: | --- | --- | --- |
| 0 | `tenant_report_role_throttling` | Simulates mixed OLTP and reporting workload contention and requires role-level resource isolation. | `easy` |
| 1 | `single_report_role_limit_simple` | A focused resource isolation case with one report role, one OLTP role, and one nearby analytics decoy. | `hard` |

The Case set above is the current code snapshot. A missing calibration is explicit and must not be inferred from unregistered labels.

## 3. Mechanism, initial state, and target

The following fields are the public state boundary exposed by the current Case contract. The actual fault mechanism, persistent resources, and target values are owned by the ScenarioCase, FaultPlan, Injector, and evaluator implementation; this document does not invent values that are not present in code.

### `tenant_report_role_throttling`

- Case number: `0`
- Title: Simulates mixed OLTP and reporting workload contention and requires role-level resource isolation.
- Alert/symptom: P1 混合业务资源告警：PostgreSQL 单机实例 CPU 使用率持续偏高，核心交易接口 P95 延迟从毫秒级升高到秒级，QPS 明显下降。同实例活跃会话数量上升且存在长耗时 SQL，请排查资源占用来源，在不重启实例且符合安全合规要求的前提下恢复核心交易延迟，并降低复发风险。
- Initial-state fields: `resource_contention`, `status`, `transaction_latency`
- Expected-target fields: `report_query`, `resource_isolation`, `status`, `transaction_latency`
- Background profiles: tenant_dashboard_rollup, customer_segment_export_preview, etl_ledger_backfill_probe, order_api_point_probe, missing_report_cache_log_noise
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.resource_throttling.PgResourceGovernanceResourceThrottlingForTenantReportRoleThrottlingEvaluatorCase`
- Difficulty labels and per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../../standards/scenario/difficulty.standard.md). This contract intentionally does not duplicate the measured values.

### `single_report_role_limit_simple`

- Case number: `1`
- Title: A focused resource isolation case with one report role, one OLTP role, and one nearby analytics decoy.
- Alert/symptom: P2 mixed workload alert: checkout point reads on the shared PostgreSQL instance have slowed from millisecond latency to several hundred milliseconds while instance CPU usage stays elevated and the number of active sessions keeps growing. Investigate the source of the resource usage, restore core transaction latency without restarting the instance, and reduce the risk of recurrence.
- Initial-state fields: `resource_contention`, `status`, `transaction_latency`
- Expected-target fields: `report_query`, `resource_isolation`, `status`, `transaction_latency`
- Background profiles: tenant_dashboard_rollup, customer_segment_export_preview, etl_ledger_backfill_probe, order_api_point_probe
- Evaluator: `src.scenarios.evaluation.postgres.resource_governance.resource_throttling.PgResourceGovernanceResourceThrottlingForSingleReportRoleLimitSimpleEvaluatorCase`
- Difficulty: hard; per-case calibration values are maintained in the code registry and the scenario catalogs; see the [difficulty standard](../../../../standards/scenario/difficulty.standard.md).
- Calibration evidence (tool m/n): query_metrics.cpu/qps=1/1; execute_sql.pg_stat_activity/role_settings=3/4

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- The alert is an orientation hint, not a root-cause answer. Exact evidence, decoys, visibility limits, and any knowledge or historical-observation tool must be verified in the Scenario and evaluator source.
- Do not treat reference reports, injector evidence, evaluator-owned observations, or hidden condition IDs as Agent-visible evidence.

## 5. DP / OP / SP contract

- **DP** is the evaluator-owned semantic diagnosis contract for the registered Case. It is independent of repair completion and uses the shared DP protocol.
- **OP** is the evaluator's final-state and business-truth contract. The expected-target fields above identify the state boundary; accepted repairs and equivalent outcomes are defined by the evaluator.
- **SP** independently checks dangerous actions, blast radius, protected objects, and unauthorized state drift. It is not a replacement for OP.
- The shared boundaries and failure classification rules are defined by [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md); do not copy historical score formulas from legacy documents.

### 两个 Case 的行为验收

报表客户端继承数据库/角色默认设置，不再自行覆盖 `statement_timeout` 或 `work_mem`。
OP 使用独立的管理员、报表角色与 OLTP 角色新连接：

1. 原始导出不再活跃，60,000 条订单及所有字段保持原值。
2. 报表角色仍能读取 tenant 1 的普通报表；禁止登录、撤销 SELECT 不属于修复。
3. 在报表角色新连接上重放一次原始导出 SQL。查询须在 30 秒内正常完成或被 PostgreSQL 的 **statement timeout** 取消，另允许 1 秒传输/调度时间。其他错误、外部取消均不通过。
4. 重放期间约每 200 ms 通过 OLTP 角色读取 tenant 1，每次须返回 3,750 行计数，客户端耗时不超过 1,000 ms。这是点读验证，不代表吞吐量/P95 恢复测量。
5. 重放观察到 35 秒即停止；评估器终止会话仅作清理，不能算修复成功。所有数据库轮询共享 90 秒墙钟预算，其中预留最多 5 秒清理；超时判 OP 失败。

角色级、角色/数据库级超时均为合法示例。满足行为条件的等价方案也可通过，不要求特定连接上限、内存值、SQL 写法或动作顺序。仅杀当前查询、仅限制连接数、仅修改 Agent 当前会话，仍会在新连接重放时失败。
告警公开运行时间、普通报表可用性、数据完整性与点读阈值。验收记录重放结果、耗时、采样数/最大延迟及业务真值比较。

保留旧 D/C 作为历史校准：`tenant_report_role_throttling` D=3、C=0.291667（Easy）；`single_report_role_limit_simple` D=4、C=0.6（Hard）。底层查询、数据及竞争 workload 未改变，但新行为验收和客户端继承设置尚未重新进行模型校准；不能将旧 run 的结果当成本版本验证，不改写冻结的 Results Catalog。

## 6. Repair, ownership, and recovery

- Use the repair families accepted by the current evaluator and Scenario contract. Action order, SQL spelling, index names, and report wording are not requirements unless the code explicitly makes them part of the public contract.
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery must release Case-owned connections, sessions, threads, processes, files, configuration, and database state through the current five-phase protocol.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.postgres.resource_governance.resource_throttling.PgResourceGovernanceResourceThrottlingScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/resource_governance/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_resource_governance_resource_throttling_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.
