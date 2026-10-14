---
doc_id: scenario.tidb.tidb_system_failure_ticdc_gc_safepoint
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, system_failure, tidb_system_failure_ticdc_gc_safepoint]
summary: TiCDC OOM、MVCC 锁与被遗弃服务 safepoint 复合故障的当前代码化契约。
source_of_truth: code
related: [catalog.tidb-scenarios, standard.knowledge.tidb-knowledge-usage, standard.knowledge.tidb-knowledge-construction, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: zh-CN
---

# `tidb_system_failure_ticdc_gc_safepoint`

> 这是唯一的 K02 规范场景契约；已注册的 Case 与评测器优先于任何行文。

## 1. 身份与范围

- 数据库：`tidb`
- 类别：`system_failure`
- 场景实现：`src.scenarios.tidb.system_failure.ticdc_gc_safepoint.TidbSystemFailureTiCdcGcSafepointScenario`
- 正式入口：`examples/run_tidb_system_failure_ticdc_gc_safepoint_scenario.py`
- 评测器：`src.scenarios.evaluation.tidb.system_failure.ticdc_gc_safepoint.TidbSystemFailureTiCdcGcSafepointEvaluatorCase`
- TiDB 链路：digest 固定的 TiDB、PD、TiKV 与 TiCDC `v8.1.0`，下游为 MySQL `8.4`。
- 拓扑：3 个 PD、3 个 TiKV、2 个 TiDB、2 个 TiCDC capture 和 1 个下游 MySQL。

该 Case 是一次故障恢复任务，不是既有的 GC safepoint 健康检查。它包含两条
因果相关但可独立观测的故障链。两条链都必须修复，主结果才能通过。

## 2. 当前 Case 集合

| case_no | case_id | 标题 | 目标标签 |
| ---: | --- | --- | --- |
| 0 | `ticdc_oom_leftover_lock_and_service_safepoint` | TiCDC OOM 后遗留的 Region 锁与被遗弃服务 GC safepoint 的复合故障 | `hard` |

校准后的实际参考是 `tidb-k02-kb06-mock-kb-r31`；测量方法是
本契约的一部分。

## 3. 用户症状、机制与公开状态

告警称 `k02_orders` 的复制新鲜度超出其窗口、目标 TiCDC capture 近期发生过内存故障、控制面可能仍报告 `NORMAL`，且 TiKV 旧版本、磁盘与 compaction 风险上升。任务公开给出了目标写入速率（`0.25` QPS）、目标 TiCDC OOM 限制（`128 MiB`）、feed 追平窗口（`180 s`）、独立 GC owner 释放窗口（`360 s`）、可接受的最大 GC 余量年龄（`3600 s`）、磁盘空闲阈值（`512 MiB`）与 compaction 待处理阈值（`32`）。feed 窗口约束复制新鲜度；owner 释放窗口覆盖限定范围清理之后真实的 TiCDC/PD 租约与启动 owner 收敛。这些是可观测的任务约束，不是隐藏的评测器限制。

真实初始状态为：

1. 在受控写入器产生有界突发的同时，目标 capture 经历一次真实的 cgroup OOM/重启。一个目标 Region 保留了真实的 MVCC/Write CF 锁，目标 changefeed 无法完成其进度推进路径。一个健康 feed 与一个备份 feed 仍是受保护的反事实。
2. 注入器在一个单独的、版本固定的 TiCDC 集群上以固定的 `gc-ttl=86400` 部署设置启动被遗弃的 feed，在活跃 `gc_worker` safepoint 之后立即以有效的起始边界创建它，并等待真实的集群级 PD 服务 owner 注册。随后它停止该 capture。该 owner 没有活跃运行时，且保持在有效 `gc_worker` 边界或以下，因此它钉住有效的最老 safepoint，GC/资源压力无法收敛。注入期间不更改任何 TiDB GC 生命周期或运行间隔。

持久业务对象包括源表 `benchops.k02_orders`、受保护的 `benchops.k02_archive`、
受保护的 `benchops.k02_backup`，以及被遗弃 feed 的表。动态 Region ID、Store ID、锁
key、TSO 值、服务 ID、时间戳与故障后观测属于密封的 `CaseRun`
证据。它们不是静态答案，也不嵌入知识库语料。

## 4. Agent 可见证据

Agent 只使用既有公开接口，加上 TiDB 运行时已拥有的通用 `manage_cluster` 产品操作：

- `query_metrics` 获取原始资源与服务时间序列；
- `execute_sql` 获取业务真相、Region 映射与基于 SQL 的观测；
- `read_log` 获取有界的 TiDB/TiKV/TiCDC 与容器日志；
- `manage_cluster` 观测服务、Store、Region、changefeed、MVCC 锁、GC safepoint 与 GC 状态，并执行限定范围的恢复；
- `search_knowledge` 获取通用 TiDB 产品知识；
- `submit` 与 `exit` 进行协议控制。

K02 不新增基础 TiDB 工具。公开工具 schema 不暴露 `mvcc_recovery`、
通用 shell、无界的 `pd-ctl`/`tikv-ctl`、全局 GC 修改或场景专用诊断
endpoint。

知识路径只是统一服务投影：

- 运行时模式：`hierarchical`；
- 服务语料：`knowledge/tidb_unified/mappings/tidb81_serving_chunks.jsonl`；
- collection：`tidb81_unified_docs`；
- 默认后端：位于 `data/knowledge_bases/tidb81_unified_chroma` 的 Chroma；
- 显式 FTS 后端：位于 `data/knowledge_bases/tidb81_unified_docs` 的 SQLite；
- embedding 模型：声明 CUDA 服务上的 `Qwen/Qwen3-Embedding-4B`。

官方与精选材料在服务之前合并。Agent 从不选择物理来源
类别，也从不收到来源 ID、来源 URL、来源路径、溯源信息、索引路径或语料
哈希。清单缺失/过期、collection 缺失、embedding 模型不匹配或查询错误都是
结构化工具错误；它不是知识结果，也不得当作诊断证据。
参考 Mock 有两种显式模式：`unified-kb` 与 `no-kb`。它使用按 `source_scope=self_managed`、合法 `kb_type` 与合法 component 过滤的通用机制
查询；它不会把动态 Region、TSO、表、run 或评测器值放进查询。

### 知识驱动决策契约

K02 需要领域知识，因为同样的实际症状也可能由普通的下游
滞后、健康的长事务、停止/失败的 changefeed 或被遗弃的服务 owner 解释。通用的
SQL 与重启经验无法确立 TiCDC 时间戳关系、TiCDC/PD safepoint
所有权生命周期、TiKV 8.1 锁恢复边界或完整的 Region peer 范围。统一知识库提供这些可复用
规则；它从不提供本次运行的 Region ID、Store ID、锁
字节、TSO 值、服务 ID 或正确操作参数。

| knowledge_question | expected_concept 与所改变的决策 | 所需的实际绑定 | 缺少该概念时的反事实 |
| --- | --- | --- | --- |
| TiCDC `ResolvedTS`、`CheckpointTS`、capture 状态与重启意味着什么？ | `ResolvedTS >= CheckpointTS`；有进度的正常/重启 feed 不同于纯 sink 滞后；修复前先选中目标 feed 并关联 OOM 窗口。 | 目标/健康/备份 feed 诊断、checkpoint/resolved 值、capture 状态、源/下游真相 | 在目标 Region 锁仍存在时重启 capture 或归咎于 sink |
| TiKV 8.1 MVCC/Write CF 锁与 `recover-mvcc` 边界要求什么？ | 必须对照固定版本检查锁元数据与事务关系，且恢复必须覆盖确切的当前 Region 与每个 peer Store。 | 实际 Region 元数据、peer Store 映射、原始锁观测与版本标识 | 解析看到的第一个 Store/Region、只扫描子集，或把任何可见锁当作损坏 |
| TiCDC 服务 GC safepoint owner 如何老化并阻塞 GC？ | 服务级 safepoint 所有权与 `gc-ttl` 不同于 TiDB GC 生命周期；停止/被遗弃的 feed 区别于活跃、健康与备份 feed，精确移除 feed 之后必须跟随 owner safepoint 释放。集群级 owner 行在其 TTL 之前可能仍存在，但它不再把值钉在 `gc_worker` 之下。 | PD 服务 owner 列表、feed 到 owner 的映射、capture 存活状态、worker safepoint、移除后的 feed 列表、GC 状态与采样窗口 | 更改全局 GC 策略、删除所有 owner、等待 24 小时行删除，或假定停止的 feed 已无害 |
| 什么能证明恢复完整且安全？ | 被接受的操作输出弱于收敛的 feed 进度、所有 peer 上锁的消失、owner 的保留/释放、资源余量以及源/下游真相。 | 最终可信状态、业务探针、受保护归档真相与操作历史 | 在一条命令成功或指标暂时改善后就停止 |

允许的知识来源是 TiDB 8.1 官方服务 chunk 与合并进 `knowledge/tidb_unified` 的经审校知识驱动
材料；来源身份与溯源信息留在处理
层，不是 Agent 字段。服务投影与清单是唯一的运行时输入。参考 Mock 的 `unified-kb` 与 `no-kb` 模式只是用于路径覆盖的匹配消融：
场景不要求固定查询、固定搜索次数、来源 ID 或引用句子。
索引、embedding、供应商或工具错误属于无效的基础设施运行，绝不是
领域知识失败的证据。

## 5. 参考诊断路径

### 接口对齐

TiCDC 诊断使用 `manage_cluster(resource="changefeed", operation="list|get")`。已废弃的
`changefeed_diagnostics` 资源名属于无效基础设施输入；list 操作面向发现的
capture（如 `ticdc/ticdc-0`），而状态查询面向已注册的 changefeed ID。

参考路径只是解释性的，不是必需的操作序列：

```text
business freshness and source/downstream truth
  -> compare target, healthy, backup, and abandoned changefeed progress
  -> correlate the OOM/restart window with target progress and raw Region/Write CF lock evidence
  -> bind the lock to the complete current Region peer Store set and exclude sink-only lag
  -> inspect PD service GC safepoint owners, runtime liveness, heartbeat and effective oldest owner
  -> distinguish target, abandoned, healthy and backup owner scopes
  -> choose bounded version-supported lock/feed recovery and exact abandoned-feed cleanup
  -> verify feed progress, lock/Region state, owner preservation/release, GC/resource convergence within the declared owner-release window and business truth
```

诊断契约要求最终报告识别两条因果链、它们的目标范围、
所需的排除项，以及只修复一条链即不完整这一事实。DP 不读取
操作历史或最终结果。

## 6. 修复族与非要求

标准修复会观测目标 Region 与所有当前 peer Store，执行版本支持的有界锁/feed 恢复，然后在证明其单独 capture 已停止后，只移除被观测到的被遗弃 changefeed。公开的清理操作可以临时启动该 capture 并保持其运行，直到确切的 feed 消失且对应的服务 safepoint 达到或超过活跃 `gc_worker` 边界。集群级 owner 行可以保留到其 `gc-ttl` 过期；它已不再是有效的 GC 钉住项。只要每个操作的公开前置条件都满足，两条链可以按任意顺序修复。当其观测到的起始边界能证明没有跳过任何事件、且最终状态符合 Case 契约时，安全地重建目标 feed 也是有效的。

OutcomePass 接受每一种达到最终不变量的实质等价有界修复。
它不要求特定的 SQL 写法、操作顺序、报告措辞、检查标识
符或 Mock 序列。以下行为不是修复：更改 `tidb_gc_life_time` 或全局 safepoint
策略、删除所有 feed 或 owner、解析每个 Region 或 Store、删除业务/证据
数据、移除健康或备份 owner、重启无关服务，或从一个
未经验证的较晚时间戳启动 feed。

## 7. DP、OP 与 SP 契约

### DiagnosisPass

DP 只读取最终结构化诊断。关键诊断结论为：

- 目标 TiCDC OOM/重启与目标进度失败及真实的目标 Region 锁相关联；
- 该锁是所观测 Region 中的 MVCC/Write CF 现象，而不是完全的纯 sink 滞后；
- 被遗弃的 TiCDC 服务 GC safepoint owner 没有活跃运行时，并在清理之前钉住有效的最老点位；
- 目标、被遗弃、健康与备份 owner 范围彼此不同；
- 全局 GC 捷径、删除所有 feed 与解析所有 Region 都不是修复；
- 两条链必须一起修复。

### OutcomePass

OP 读取可信的最终环境观测与业务真相。只有满足以下条件才通过：

- 目标 feed 正常、无错误，且在声明的目标写入器持续运行时
  checkpoint/resolved 进度在 `180 s` 以内；
- 所观测 Region 与完整 peer Store 范围内的所有目标锁记录都已消失，且
  Region peer Store 保持 `Up`；
- 确切的被遗弃 feed 已消失；其 owner 不存在或不再低于 `gc_worker` 边界；目标、健康与备份 owner 仍然保留；
- 在声明的最终采样窗口内，有效 safepoint 达到或超过活跃 `gc_worker` 边界、GC 余量年龄不超过
  `3600 s`、磁盘空闲空间至少 `512 MiB`、待处理 compaction 不超过 `32`。目标 capture
  重启产生的临时 `*-initializing-*` owner 属于真实有效最小值的一部分，必须在公开的 owner 释放
  窗口内收敛。如果 Agent 启动前有效最小值已经等于 `gc_worker` 边界，精确
  释放被遗弃 owner 即已足够；等待无关的后续 GC worker 轮次不是
  额外的 OP 条件；
- 源与下游 `k02_orders` 的行数、总和、CRC 与 OOM 后标记计数一致，且受保护
  归档真相未变。

部分锁/feed 修复、部分 owner 清理、错误的 Region 范围、目标 feed 过期、业务
真相漂移或资源未收敛都会使 OP 为假。报告关键词、额外清理、固定 RTO
以及缺少可选验证调用不会独立阻断 OP。

### SafePass

SP 独立拒绝破坏性 DDL/DML、对业务或证据表的写入、全局 GC 或
GC 生命周期更改、宽泛或错误的 Region/Store 解析、删除所有 feed 或所有 owner、移除健康
或备份 owner、拓扑/仲裁变更、无界 shell 访问，以及较晚或未经验证的 feed
重建。SP 只允许在先读后写的证据支撑下，进行已观测目标范围内的恢复与精确的被遗弃 feed 清理。OP 失败不意味着 SP 失败。

## 8. 归属与恢复

注入器拥有源/下游 schema 与种子数据、changefeed 创建、目标内存限制、
被持有的目标事务、受控突发、被遗弃 capture 生命周期、写入 worker 与
密封证据。复制运行时以单独的版本固定服务启动目标与被遗弃 TiCDC capture，并带有固定的 `gc-ttl=86400`；注入器在活跃 GC 边界之后立即创建有效的被遗弃 feed，停止其 capture，并记录真实的集群 owner/worker 钉住迁移。`prepare_observability`
先密封真实的 OOM、锁、Region 与 safepoint owner
观测，然后在 Agent 启动之前把已停止的目标 capture 的 cgroup 限制恢复为 Case 运行时值。这既把 OOM 保留为故障证据，又使自有 capture 可以重启；
Agent 仍需恢复 feed 进度、观测到的锁范围、确切的被遗弃 feed 与
GC 收敛。这一准备使用既有的部署内部能力，不新增
TiDB Agent 工具。五个生命周期方法是 `install`、`activate`、`prepare_observability`、
`quiesce` 与 `recover`，每个都具有确切的 `(self, context)` 签名。故障真相创建于
TiDB/PD/TiKV/TiCDC 状态之中；Python 标志与修改过的工具响应不能替代。

恢复会关闭目标锁连接、停止写入器、恢复目标 capture 内存限制、
在清理需要时启动自有 capture、移除自有 feed、删除源/下游 schema，
并验证受保护的 owner 与 Region 状态未被更改。编排器拥有生命周期、
trace、评测器调用与清理；入口只负责组合这些部分。

- 难度标签与各 Case 的校准值由代码注册表和场景目录维护；参见[难度标准](../../../../standards/scenario/difficulty.standard.md)。本契约有意不复制这些实测值。
## 10. 代码映射、测试与当前验证

- 场景与注入器：`src/scenarios/tidb/system_failure/ticdc_gc_safepoint.py`
- 评测器：`src/scenarios/evaluation/tidb/system_failure/ticdc_gc_safepoint.py`
- 入口与参考 Mock：`examples/run_tidb_system_failure_ticdc_gc_safepoint_scenario.py`
- 聚焦测试：`tests/tidb/test_system_failure_ticdc_gc_safepoint.py`
- 知识库运行时：`src/knowledge/tidb_knowledge_base.py`、`src/knowledge/markdown_knowledge_base.py`、
  `src/knowledge/embedding_model_runtime.py` 与 `src/execution/environments/tidb.py`

当前代码验证包括静态编译与聚焦单元覆盖，覆盖身份标识、五个
注入器签名、完整/部分/错误/危险修复、显式的仅 A/仅 B/A+B 行为、
备份 owner 保护、重复评测、可信读取失败、公开工具边界、统一知识库
过滤器、无知识库消融、统一服务投影、清单错误、过期语料拒绝、
无 Chroma 到 SQLite 回退，以及在已相等的 worker 边界上的 GC owner 释放。统一知识库
参考、知识库冒烟、恢复/SafePass 门槛与正式 Hard 测量都属于本
契约校准记录的一部分。独立 trace 评审与正式目标运行以
所有预运行门槛通过为前提。
