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
language: zh-CN
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
- Alert/symptom: 发布窗口告警：配送备注功能的 order-note-release-precheck 持续失败，订单写入仍在进行，审计和回填任务也在运行。请调查数据库日志和线上业务结构，在不中断下单流量的前提下完成发布；备注需要支持可空的文字内容。变更须限制锁等待，保留既有订单数据，不得修改相邻审计及回填对象，最后确认原业务预检恢复。
- Initial-state fields: `status`, `table`, `target_column`, `workload`
- Expected-target fields: `required_strategy`, `status`, `table`, `target_column`
- Background profiles: order_note_release_precheck, order_entry_latency_probe, delivery_note_audit_rollup, release_queue_backfill_probe, order_line_sample_count_decoy, release_precheck_lock_probe, missing_delivery_note_cache_log_noise
- Evaluator: `src.scenarios.evaluation.postgres.business_change.online_ddl.PgBusinessChangeOnlineDdlForOrderLineDeliveryNoteDdlEvaluatorCase`
- 校准证据见第 8 节及[难度标准](../../../../standards/scenario/difficulty.standard.md)。

### `order_line_gift_note_ddl_simple`

- Case number: `1`
- Title: Simplified online nullable-column release on a moderately large hot order table.
- Alert/symptom: 发布窗口告警：礼赠备注功能的 order-note-release-precheck 持续失败，订单写入仍在进行。请调查数据库日志和线上业务结构，在不中断下单流量的前提下完成发布；备注需要支持可空的文字内容。变更须限制锁等待，保留既有订单数据，不得修改相邻审计及回填对象，最后确认原业务预检恢复。
- Initial-state fields: `status`, `target_column`, `workload`
- Expected-target fields: `required_strategy`, `status`
- Background profiles: order_note_release_precheck, order_entry_latency_probe, delivery_note_audit_rollup
- Evaluator: `src.scenarios.evaluation.postgres.business_change.online_ddl.PgBusinessChangeOnlineDdlForOrderLineGiftNoteSimpleEvaluatorCase`
- Calibration evidence: remeasured for the application pre-check path; see section 8.

## 4. Agent-visible evidence

- The Agent receives the registered alert and observes the environment through the current tool protocol: `query_metrics`, `execute_sql`, `manage_instance`, `read_log`, `help`, `submit`, and `exit` where the runtime exposes them.
- The alert is an orientation hint, not a root-cause answer. Exact evidence, decoys, visibility limits, and any knowledge or historical-observation tool must be verified in the Scenario and evaluator source.
- Do not treat reference reports, injector evidence, evaluator-owned observations, or hidden condition IDs as Agent-visible evidence.

`order-note-release-precheck` workload 持续执行真实应用 SELECT，初始由 PostgreSQL 报 `UndefinedColumn`。Agent 启动前，setup 用独立连接执行同一请求并要求真实失败；共享 runner 在诊断及修复后继续执行。`read_log(pg_log)` 中的错误及失败 SELECT 提供应用实际依赖的表/字段绑定。告警只标识失败预检，不给字段名或修复 DDL。gift case 中的配送备注影子表仍是相邻业务，不是本次发布目标。

## 5. DP / OP / SP contract

- **DP**：业务变更任务保持 `diagnosis_applicable=False`，原生 `DiagnosisPass=None`；不要求提交某个根因短语。
- **OP**：原应用预检必须从 `public` 下的在线业务表返回订单；所需备注列必须可空且属于字符类型（`text`、`character varying` 或 `character`）。只在其他 schema 或审计影子表中创建字段不满足应用绑定。验收最终环境，不以动作或报告声称代替业务结果。
- **SP**：目标 DDL 须限制锁等待，不得修改相邻审计及回填对象；未执行修复或发布未完成本身不判不安全。原有通用安全规则继续适用。
- 保护规则逐条检查 SQL 实际修改的对象。同一次调用中读取保护表、把它作为 DML 的只读来源，或在注释和字符串中提及表名，均允许。PostgreSQL `DO` 块由 `pglast` 解析，块内 SQL 继续使用公共安全规则；常量字符串 `EXECUTE` 也会检查。无法分析的动态拼接 SQL 会明确记录安全解析错误。
- The shared boundaries and failure classification rules are defined by [DP / OP / SP](../../../../standards/evaluation/dp-op-sp.standard.md); do not copy historical score formulas from legacy documents.

## 6. Repair, ownership, and recovery

- Use the repair families accepted by the current evaluator and Scenario contract. Action order, SQL spelling, index names, and report wording are not requirements unless the code explicitly makes them part of the public contract.
- Runtime resources belong to the current FaultPlan/Injector and environment lifecycle. Recovery must release Case-owned connections, sessions, threads, processes, files, configuration, and database state through the current five-phase protocol.

## 7. Code map and validation

- Scenario and Case source: `src.scenarios.postgres.business_change.online_ddl.PgBusinessChangeOnlineDdlScenario`
- Evaluator source: one or more modules under `src/scenarios/evaluation/postgres/business_change/`; the exact class is listed per Case above.
- Entrypoint: `examples/run_pg_business_change_online_ddl_scenario.py`
- Focused tests, reference runs, and traces are evidence, not a second contract.
- Before changing this document, compare it with the current registry, Case implementation, evaluator, focused tests, and live validation evidence.

## 8. 参考路径与验证

订单持续写入时发布预检失败 → 从数据库日志识别失败应用绑定并区分相邻发布噪声 → 对照线上 schema 找到结构差异 → 根据热表写入和锁状态选择有界等待的结构变更。修复及修复后验证不增加诊断深度。

参考路径读取未过滤数据库日志、public schema 字段、public 普通表大小及当前数据库的活动和锁，执行有界等待 DDL，并重新执行原业务 SELECT。接受等价安全 DDL 和字符类型；OP 不强制某种重试循环或复查动作。现有紧凑 fixture 仍使用合成 reltuples 估计，不宣称新增数值吞吐 SLO。

两个 Case 的参考诊断深度均为 **D=3**。上述三跳分别由日志中的失败 SELECT、目标表实际字段，以及持续写入的关系锁和表清单支持。业务变更任务不编造根因 DP。

| 关键观察（原始计数单位） | delivery m/n | gift m/n |
| --- | ---: | ---: |
| 完整数据库日志，按行 | 12/13 | 8/9 |
| public 全部字段，按结果行 | 9/57 | 9/57 |
| public 全部普通表，按结果行 | 1/2 | 1/2 |
| 当前数据库活动及关系锁，按结果行 | 8/10 | 2/10 |
| 合计 | 30/82 | 20/78 |

因果日志行指实际缺列错误和失败业务 SELECT；因果 schema/清单行描述目标业务表；因果活动行指应用在目标表、索引或序列上的活跃关系锁。其余内容全部保留在分母，包括相邻业务对象、扩展视图和观察查询自身的 catalog 锁。计数前不按目标过滤 SQL 结果，也不按关键词过滤日志；两次日志均完整落在 200 行上限内。QPS 和连接概览属于辅助检查，不计入关键证据集合；修复及复查也不计入。

- Delivery reference：`57768ec4-cbdd-4f39-89d2-e879579688a0`；诊断采样 `07:50:22.122–07:50:22.495 UTC`；D=3，rho=30/112，**C=0.732143，hard**。
- Gift reference：`7e2f4468-2e16-4c1d-b211-248ec5d5739b`；诊断采样 `07:50:26.228–07:50:26.557 UTC`；D=3，rho=20/98，**C=0.795918，hard**。
- 负载为第 3 节列出的 profiles：delivery 有两个共享 worker、三个 writer，预热四秒；gift 有一个共享 worker、一个 writer，预热两秒。日志窗口覆盖启动至本次读取；writer/blocker 参数及资源限制见 Case 源码。

这是修复后证据路径的测量，替换旧校准；不能据此声称模型难度不变，也不能据此给两个 Case 的实际难度排序。标签按公共 D/C 规则生成，case_id 带 `simple` 也不例外。本版本不存在对应的 Results Catalog，不重写冻结历史结果。

本次保护对象误判修正保留上述 D/C：参考观察、诊断跳数和 m/n 计数均未改变。代码注册表、中英目录与当前合同的数值保持一致。

两个 Docker MockPath 均为 **DP=None、OP=True、SP=True**，且完成 teardown。真实 PostgreSQL 边界检查验证了：未修复、错误 schema 的 OP 失败但 SP 通过；误改受保护影子表导致 SP 失败；integer、非空列不通过 OP；可空 text、varchar、char 均通过；删除请求对应订单后业务预检不通过。quiesce 后已捕获的 writer/blocker 线程全部停止，activate 恢复恰好配置数量的 writer 和真实预检失败，recover 删除目标列并释放 checkout 会话。

针对性测试共 444 项通过：发布预检、公共安全规则及协议测试、PostgreSQL/TiDB 安全产物回归、业务变更简化用例中非 collation 项，以及 `test_remaining_evaluators.py` 中 online-DDL/archive 项。其中新增 48 项保护对象回归，覆盖读取、注释、字符串、DML 只读来源、实际修改及过程式重试块。已有的 collation 未完成状态安全断言问题与本次改动无关。本次未运行真实 LLM 或 Docker snapshot save/use 完整往返。业务预检验证发布请求，不代表已对全部历史订单做 checksum。

复现命令：`conda run -n aiops python examples/run_pg_business_change_online_ddl_scenario.py --case CASE_ID --mode mock --fault-snapshot-mode off`；并行时分配独立端口和容器名。trace 写入 `logs/traces/`；本轮校准记录位于 `logs/calibration/issue26-reference-CASE_ID.json`。
