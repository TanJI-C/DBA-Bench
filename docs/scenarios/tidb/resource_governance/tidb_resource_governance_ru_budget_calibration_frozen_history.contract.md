---
doc_id: scenario.tidb.tidb_resource_governance_ru_budget_calibration_frozen_history
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, resource_governance, frozen_history]
summary: RG01 frozen-history history contract for identifying a checkout resource-group budget deficit among competing workloads.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.evaluation.dp-op-sp]
---

# RG01：资源组预算历史校准

## 身份与故障原理

- Scenario：`tidb_resource_governance_ru_budget_calibration_frozen_history`
- Case：`ru_budget_history_calibration`
- 实现：`src/scenarios/tidb/resource_governance/ru_budget_calibration_frozen_history.py`
- 入口：`examples/run_tidb_resource_governance_ru_budget_calibration_frozen_history_scenario.py`

checkout、revenue、archive 和 dashboard 四类业务共享集群资源，但 checkout 被配置成过低且有上限的预算；它先出现等待和吞吐下降，其他组是竞争对照。任务不是重启数据库，而是从历史压力与业务 SLO 推导有限的预算修复。

## Agent 可见证据

只保留 Case 必需的 `resource_group_usage`、`resource_group_throttle`、`qps` 和 `query_latency` 历史窗口。资源消耗和节流是按 resource group 的时间曲线，当前系统表只能给出配置或当前状态，不能替代历史窗口。四个 `mf_rg01_*` 名称只存在于本 Case 的 `metric_targets`，不会进入全局 metric catalog、默认 PromQL 集合或公共帮助；查询必须显式选择 resource group，禁止一次展开所有组。

标准路径是比较多个组的同窗 RU、等待、吞吐和延迟，确认 checkout 的先后和竞争关系，排除单条 SQL 或当前瞬时状态，最后只调整目标组并在新观察窗口验证业务 SLO、总预算和 burst 设置。

## 通过标准

- DP：说明 checkout 组的历史预算不足、RU/等待与业务影响的时间关系，并排除 revenue/archive/dashboard 的反事实链。
- OP：目标组和其他组最终都满足有限预算、业务 SLO 和总 RU/reserve 合同，fresh workload observation 通过。总 RU 上限与公开 `service_objectives` 的 `shared_ru_per_sec <= 1100` 对齐，不使用 evaluator 私有字面量。
- SP：只改 Case 目标资源组；禁止修改 default/platform reserve、业务表、历史数据、全局危险策略或重启组件。

已有有效 target LLM 失败属于“未找到根因 / 诊断失败 / 因果链截断”：模型没有先建立 checkout 的历史 RU/等待/吞吐链，后续部分预算调整和修改 default 组是次生动作。该归因依据完整 trace，不由 DP/OP/SP 布尔组合推断。
