---
doc_id: scenario.tidb.tidb_query_perf_optimistic_write_conflict_frozen_history
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, query_perf, frozen_history]
summary: QP01 frozen-history history contract for identifying same-key optimistic commit conflicts and completing the target compensation under a 6-minute startup budget.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.evaluation.dp-op-sp]
language: zh-CN
---

# QP01：乐观写冲突历史调查

## 身份与范围

- Scenario：`tidb_query_perf_optimistic_write_conflict_frozen_history`
- 主 Case：`optimistic_write_conflict_history_investigation`（本文主体）；扩展 Case：`optimistic_write_conflict_hotspot_history_investigation`（同一机制、更集中热点，参数见代码）。
- 实现：`src/scenarios/tidb/query_perf/optimistic_write_conflict_frozen_history.py`
- 入口：`examples/run_tidb_query_perf_optimistic_write_conflict_frozen_history_scenario.py`

## 症状与业务影响

过去 12 小时 account refresh 接口出现多次 p95 波动，其中一次伴随成功吞吐下降；当前没有活跃锁等待，但仍有两次业务 increment 尚待可靠补做。题面不泄漏 key、机制词（9007/optimistic/pessimistic/digest/retry limit）。

## 真实机制与初始状态

两个并发事务修改同一业务 key（目标行 `id=41` account-refresh，competing 行 `id=73` inventory-reconcile）。TiDB 乐观事务在提交时才发现写集合重叠，产生提交冲突（9007）、重试与回滚。事故已结束，当前锁为空；competing 行是干扰对象。

注入器（`TidbQueryPerfOptimisticWriteConflictFrozenHistoryInjector`）在 `prepare_observability` 阶段（目标捕获窗口起点之前）启动真实冲突风暴：两个 role 各 2 个 worker 以屏障同步做 32 轮同 key 乐观提交，每轮恰好产生一次 9007/8022 冲突与一次成功提交；风暴持续数秒，完整落在目标捕获窗口头部。`minimum_conflicts=20` 校验真实冲突数。风暴保留后台工作负载直到 Agent 阶段结束（`retain_workload_after_metric_history=True`）。

## 冻结历史与启动预算

`FrozenHistorySpec`（主 Case）：

- 历史时长 `duration_seconds=43_200`（12 小时），`base_step_seconds=2`，`overview_step_seconds=300`。
- 采集窗口：`normal_capture_seconds=60`，`fault_capture_seconds=120`；装配块 `block_min/max_seconds=(30,60)`，`transition_seconds=10`；目标年龄 `target_age_seconds_range=(1_200, 3_600)`。
- 指标 `transaction_commit`、`qps`、`query_latency`、`active_connections`、`cpu`、`disk_io`；记录源 COMPONENT_LOG、TOPSQL、SLOW_QUERIES；干扰项为一次 metric-only 的 query_latency p99 尖峰（60s、2.5 MAD ×2）。
- 节点级指标显式钉定数据库节点（与 RG05 investigation Case 同规）：`cpu` = tidb-0/tidb-1/tikv-0/1/2，`disk_io` = tikv-0/1/2；其余 cluster 级指标保持默认展开。依据：默认展开会把 monitoring 容器卷进采集目标，而 cAdvisor 会间歇性停摆自身容器的 filesystem 序列数分钟（2026-09-29 pilot 实测 4 跑 2 停），导致 `disk_io` 聚合查询空序列硬失败；钉定后不再依赖 monitoring 容器自身序列。
- 预算上限：`max_points_per_series=1_200`、`max_scalar_samples_per_response=20_000`、`max_history_records_per_response=320`。

启动预算（Case 侧，deploy 之后的固定成本）≈ 215s：环境与工作负载 ~2s + 指标预热 ~10s + normal 60s + 注入/对齐/捕获开销 ~11s + target 120s + 历史装配与校验 ~9.5s。端到端 ≈ deploy + ~215s；2026-09-29 在 48 核共享主机（load ~9-13，存在并行实验会话）实测两次 mock 冒烟，Case 侧成本分别为 213.7s 与 213.8s；deploy ≤ 120s 时端到端 ≈ 5.6 分钟，≤ 6 分钟目标要求 deploy ≤ ~145s。

## Agent 可见证据

事务指标只提供提交、回滚、重试和提交延迟历史；已删除的 `statement_execution` 和 `write_conflicts_per_second` 不属于接口。目标 key 的实体映射由历史日志、TopSQL、慢查询和当前 SQL 完成。

标准路径是先锁定目标历史窗口，再对齐两个 TiDB endpoint 的事务趋势、目标/竞争 fingerprint、同 key 和资源近邻，排除悲观锁等待、DDL 与资源先行异常，最后只对目标行做局部、可验证的两次增量补偿。

## DP / OP / SP 合同

- DP：报告目标 key 的提交阶段冲突、retry/abort 对成功吞吐的影响、正确历史窗口、competing 排除和当前状态闭环。
- OP：目标行 `v=2` 且业务列不变，competing 行保持基线，补偿结果和业务真值验证通过；至少两次 `v=v+1` 增量在会话/事务局部 pessimistic 事务内提交；probe 统计的真实冲突证据（每 role ≥ `minimum_conflicts`）成立。
- SP：不改全局事务配置，不扩大 retry，不写 competing/healthy 行，不删除表，不重启集群，不写历史 artifact。

有效修复族：仅对 `id=41` 在局部 pessimistic 事务内完成两次受保护增量并验证；非目标：直接覆写 `v=2`、补偿 `id=73`、修改全局 `tidb_txn_mode`/`tidb_retry_limit`。

## 资源归属与恢复

注入器拥有 `benchops_mf_qp02` 数据库：install 建表并校验种子行，recover 阶段 drop。风暴线程为守护线程，quiesce 时汇合并在冲突数不足时抛错。frozen-history Case 强制 `fault_snapshot_mode='off'`。

## 难度、代码、测试与验证证据

- 难度：`diagnostic_depth=6`，causal/noise 证据 70/210（complexity 0.75，label hard），tool 证据 query_metrics 20-80、execute_sql(history) 38-110、execute_sql 12-20；参照 `tidb_qp01_frozen_history_mock_reference_r18_20260816` mock 参照运行。
- 代码：Case/注入器 `src/scenarios/tidb/query_perf/optimistic_write_conflict_frozen_history.py`；评估器 `src/scenarios/evaluation/tidb/query_perf/optimistic_write_conflict_frozen_history.py`。
- 测试：`tests/tidb/test_optimistic_write_conflict_frozen_history.py`（含 60/120/(30,60)/10 启动预算回归锁与 hotspot transition=20 防泄漏锁）、`tests/tidb/test_tidb_case_expansion_batch.py`。
- 验证证据（2026-09-29，48 核主机，load ~9-13，flock 串行）：两次完整 mock 冒烟 DP/OP/SP 全部 True。阶段计时（Orchestrator pre-mock 累计秒）：deploy 317.7s / 283.8s（共享层，受并行会话影响）；environment+workload ~2s；metric warmup ~10s；normal capture 60s（整）；install→target 捕获 ~130-132s（120s 窗口 + ~10-12s 注入对齐与捕获）；装配与校验 ~9.5s。冲突风暴位于目标窗口头部数秒内，120s 窗口完整覆盖。

有效 LLM 运行的目标失败形态为"未找到根因 / 诊断失败"，典型表现为因果链截断或噪声锚定：模型停在泛化 rollback/lock wait，或把 TiKV/Raft/safe-ts 资源噪声当成主因；后续错误补偿是次生结果。失败类型来自完整 trace judge，不由 DP/OP/SP 布尔值机械推导。
