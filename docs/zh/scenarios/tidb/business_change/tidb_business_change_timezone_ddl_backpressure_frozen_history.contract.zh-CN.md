---
doc_id: scenario.tidb.tidb_business_change_timezone_ddl_backpressure_frozen_history
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, business_change, frozen_history]
summary: Frozen-history contract for separating sink backlog from a later timezone-sensitive DDL failure.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.evaluation.dp-op-sp]
language: zh-CN
---

# 时区 DDL 与下游背压历史调查

## 身份与故障原理

- Scenario：`tidb_business_change_timezone_ddl_backpressure_frozen_history`
- Case：`timezone_ddl_backpressure_history_investigation`
- 实现：`src/scenarios/tidb/business_change/timezone_ddl_backpressure_frozen_history.py`
- 入口：`examples/run_tidb_business_change_timezone_ddl_backpressure_frozen_history_scenario.py`

下游写入先变慢，造成同步积压；之后上游用 UTC 语义提交的时间字段变更在下游时区语义下失败，失败提交点挡住了检查点。当前服务可能已经恢复，不能只看当前绿色状态。

## Agent 可见证据

历史指标只保留 `qps` 和 `query_latency`，因为本 Case 需要比较长窗口中的吞吐和延迟先后。历史记录来自组件日志。模型通过现有 `query_metrics`、`execute_sql`、`read_log`、`manage_cluster`、`help`、`submit`、`exit` 诊断和修复；没有新增 Agent 工具或专用根因指标。

标准路径是先找出同一目标窗口，再把 DDL 前的写入/吞吐变化、sink backlog、失败提交点和后续健康对象串起来，排除 archive 邻居及后续正常 rollout，最后从失败提交点之后安全恢复同步并验证业务写入保留。

## 通过标准

- DP：报告同时说明背压先发生、timezone-sensitive DDL 后失败、失败提交点阻塞检查点，以及两者的时间因果关系和必要排除项。
- OP：同一个 changefeed 从正确位置恢复，DDL/backlog 消失，source/downstream 业务结果和新增写入一致。
- SP：不修改历史数据，不误伤健康 changefeed、业务表或集群组件；停流、暂停和恢复都限定在目标对象。

已确认的有效 target LLM 失败属于“未找到根因 / 诊断失败 / 因果链截断”：模型停在 DDL 错误和时区不兼容，没有建立 DDL 前背压、失败提交点和后续 backlog 的完整链条。其 OP 失败是后果，不能反向推导 DP 失败；无效采样、部署或 teardown 运行不计为模型失败。
