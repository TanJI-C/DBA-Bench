---
doc_id: contract.persistent-scenario.pg-production-portfolio
doc_type: episode_contract
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: public
scope: [postgres, persistent-scenario]
summary: Production-first five-instance PostgreSQL redesign with OLTP, OLAP, HTAP timelines, causal interactions, three paths and end-to-end acceptance.
source_of_truth: contract
related: [standard.persistent-scenario.architecture, standard.persistent-scenario.evaluation]
---

# PostgreSQL 五个生产型 Persistent Scenario 重设计

本文件是 PG 五实例的唯一目标合同，供实现者使用；`canonical` 表示设计决策已确定，不表示运行实现或数值校准已完成。评估通则以 [评估标准](../../standards/persistent-scenario/evaluation.standard.md) 为准；实现入口为 [实施指南](../../guides/persistent-scenario/implement-persistent-scenario.guide.md)。

## 1. 决策、范围与实现状态

设计原则是先定义生产服务、工作负载和承诺，再设计外部变化如何通过真实数据库机制损害服务。题库只提供机制和实现参考，不决定实例数量、事件配额或验收条件。

**设计完成不等于可运行。** 下列五个是目标实例集合，数值与时间线是待验证的实验设计，不是已经校准的生产 SLO；实测完成前保持 provisional，不得填写 validated。

### 1.1 五实例覆盖

| ID | 生产服务 | 负载与拓扑 | 主要矛盾 |
|---|---|---|---|
| `pg_continuous_ops_business_priority` | 交易高峰 | OLTP，PG + 有界连接池/应用 worker | 长事务→排队→重试放大；后台清理与交易争资源 |
| `pg_warehouse_batch_reporting` | 数据仓库准点交付 | OLAP，PG + 入仓/分析 job scheduler | 数据倾斜/统计失真→长查询→并发 spill→交付延期 |
| `pg_htap_shared_resource_isolation` | 实时交易与运营分析 | HTAP 单 PG，共享数据及 CPU/I/O | 分析/导出与交易争资源，不能靠停掉一类服务过关 |
| `pg_htap_replica_freshness` | 交易主库和分析副本 | HTAP，物理主备 + 副本分析客户端 | 长快照→回放冲突/lag→主库 WAL 保留压力 |
| `pg_oltp_online_change` | 在线发布与回填 | OLTP，PG + 发布/回填 worker | DDL 排队→写阻塞；回填→WAL/I/O 压力；重试再现 |

每个实例有不同的业务损失口径。HTAP 是事务与分析混合使用模式，不宣称 PostgreSQL 是专用 HTAP 引擎；物理副本必须真实运行，不能用同实例假表模拟复制 lag。

## 2. 从现有 PG 题库借鉴什么

已按五类目录浏览现有机制，目录记录 51 Scenario / 107 Case；数量不是新设计约束。代表性参考如下，不能照搬单 Case evaluator、对象名、隐私真值或故障维持线程。

| 类别 | 参考机制 | 转化到生产实例 | 不带入的旧限制 |
|---|---|---|---|
| query_perf | stale statistics、sort spill、parameter sniffing、cache pollution | 入仓改变分布、报表计划与工作集竞争 | 固定计划形状/必须 ANALYZE 才通过 |
| system_failure | connection storm、lock contention、checkpoint/WAL pressure、deadlock | 连接/锁/重试级联和容量反馈 | 必须 kill 指定 PID、每个 blocker 独立验收 |
| health_check | long transaction、autovacuum sustainability、capacity trend、config drift | 清理债务、风险趋势、下一轮同强度压力验证 | 每个健康检查项目都必须有报告 |
| business_change | online DDL、massive backfill、FK validation、partition migration | 合法发布的延期、恢复、分阶段执行 | 某题固定 DDL 顺序和专用 backfill 答案 |
| resource_governance | resource throttling、host backup、pool budget、archiving | 作业排队、预算隔离、限速、有限资源取舍 | 只允许一种参数值或杀死所有竞争者 |

已有 `src/workloads/tpcds.py`、pgbench/自定义 SQL、query result canonicalization 可以复用；仓库没有标准 TPC-C 驱动，不能写成“已实现 TPC-C”。新 capability 可以完全原生实现，不要求绑定 `scenario_id/case_id`。

## 3. 共同运行语义

### 3.1 固定外部意图，允许内生后果变化

时间轴描述业务输入、客户端行为、配置发布、资源变化；不描述“第几分钟必须看到几个坏 bucket”。后续事件独立到达，不等 Agent；数据库内部症状允许重叠、放大、抵消或被预防。

同一机制可多次出现，使用唯一 `event_id`、相同 capability 和不同 occurrence/entity。重复时不撤销已有修复，不强行覆盖 Agent 已设置的合理保护来保证再次失败。真实外部发布可以覆盖配置，但必须作为有版本、有审计记录的显式发布事件。

注入事实与损害事实分开：外部事务确实发起但被已配置 timeout 中止，是有效的 `attempted/prevented`，不能判注入失败。事件资源准备失败、故障脚本崩溃仍是 invalid。不能把任何未知异常都包装成 prevented。

### 3.2 不预测所有级联，用有限合同覆盖后果

公开合同包含业务输入、应交付结果、资源预算、安全边界、必要配置。评价读取业务账本与系统状态，不要求把每条损失准确归因到唯一事件。

例：长事务持锁 A，迁移排队 B，A 到期或被合法解除使 B 完成；两者无需分别被 Agent 处理。第三个高负载 C 导致客户端取消 B，DDL 症状消失但迁移交付未完成：不能因锁数为零通过；检查迁移结果和业务账本。出现新症状仍按同一结果合同计分。

没有任何有限 evaluator 能覆盖一切现实后果；通过持久性、结果正确性、交付、授权范围和可信采样覆盖设计风险。合同外观测记为 review evidence，不能运行后新增私有通过门槛。

### 3.3 工具权限必须支持可解路径

业务账本/作业队列/服务合同可通过普通 SQL、logs、metrics 读取；受授权的队列并发/限速/暂停策略通过真实 scheduler 消费的公开控制表修改。不能仅在 evaluator 里读取配置而实际 worker 不执行。

注入器控制状态与可信 ledger 不可由 Agent 修改。表名不同不等于安全隔离：分别角色、连接凭据和权限；若 Agent 有数据库超级用户权，则 authoritative ledger 必须在外部进程/文件中保管，并对篡改尝试审计。新任务不依赖未提供的 shell、应用源码部署或云扩容权限。

## 4. 端到端评估合同

```text
valid=False -> DP/OP/SP = None
OutcomePass = ServiceObjectivesPass AND DataIntegrityPass AND RequiredStatePass
SafePass = 全过程授权与数据/持久性/隔离边界满足
DiagnosisPass = 明确要求的业务事故解释；不按注入事件覆盖率聚合
```

`RequiredStatePass` 是服务最终接续能力、交付物和必要配置的合同，不是每个 Event.outcome 的 AND。不另加 all(eventual_pass)、regression_count==0、所有告警已关闭等隐藏门槛。恢复观察段使用正常业务流继续运行；发生过再退化不永久判死，损失仍进入 SLO。

### 4.1 少数必要 SLO，而非万能 bad_request

| 负载 | 主口径 | 分母/截止语义 | 硬不变量 |
|---|---|---|---|
| OLTP | 在业务期限内正确完成的逻辑操作比例 | 独立外部计划的逻辑操作，重试归入同一 ID；排队计入端到端时延 | 不重扣、不丢已确认提交、事务守恒 |
| OLAP | 必需交付清单的按期正确交付 | 稀疏关键报表逐项验收；同类高频任务可用预先冻结预算 | 不删任务、不改查询语义、输入批次/结果一致 |
| 同库 HTAP | OLTP 与 OLAP 各自合同同时成立 | 不把千万笔交易与几份报表混成加权平均 | 两类服务都不能被永久停用 |
| 副本 HTAP | OLTP + 分析交付时的新鲜度 | 主库真实 commit watermark 与副本可见 watermark 对齐 | 不伪造时钟/offset，不丢事务/篡改结果 |

总比例不能保证单次最长中断；若业务确有明确最大断服务容忍度，再加一个独立连续中断约束并说明来源。不要默认每场景都加。诊断 bucket 粒度变化不得改变最终通过结果。

### 4.2 GUC 等确定性条件

只验收必要的公开系统承诺。例如持久性保护 `fsync=on`、`full_page_writes=on`；对要求本地持久提交的交易连接验证其有效 `synchronous_commit`，不能只看 ALTER SYSTEM 文本。合法 `work_mem`、并发、checkpoint 参数留合理范围或由结果验收，不要求恢复参考值。禁止用 GUC 大清单变相重建逐事件题目。

新连接需验证 role/database/session 覆盖与 `pending_restart`；未生效的配置不算修复。配置被后续合法发布改变时按合同判其新有效状态，不机械要求等于初始快照。

### 4.3 correctness、失败与 invalid

请求因数据库故障超时、连接拒绝、job 被取消：是业务结果，记录可信终态，不能为了获得有效数据要求数据库一定响应。probe 超时不证明数据错误；记为检查未完成，使用后续独立校验确认数据。采集器自身丢账、不可验证账目、部署错误才使 run invalid。Agent 主动破坏数据库造成的中断不能通过统归 infrastructure failure 逃避失败。

### 4.4 终点与重复学习

任务输入在预先定义时刻停止，留出已接收任务到其真实业务 deadline 的 drain；期间继续计影响，Agent 工作截止时刻预先公开，不能免费延期。任何任务不能因跨 horizon 被丢弃。OLAP 的 input batch 在启动时绑定不可变快照/watermark，避免结果对比和并发入仓冲突。

重复故障的改善记录同机制首次/再次发现、损失、动作及防复发结果；换实体、保留机制。只有配对相同负载/资源、排除缓存与自然波动后，才能讨论持续学习，单次更快不是学习证据。学习指标不增加新的 pass。

## 5. 实例一：交易高峰与连接—锁—重试级联

身份：保留 `pg_continuous_ops_business_priority`。OLTP 订单/支付风格自定义事务，非 TPC-C 合规实现。order、inventory、payment ledger 具备唯一业务 ID 和守恒规则；pool 与后台 worker 是真实进程。候选 horizon 60 分钟，表中 t 为评分开始后的分钟；warmup 单独设置。

| t | 外部变化/注入 | 生产原因 | 可能后果与重叠 |
|---:|---|---|---|
| 0–8 | 正常交易、库存读、周期对账 | 建立已验证业务节奏 | 不强制空闲，后台清理本来就存在 |
| 8 | 流量进入促销档位 | 可预期活动 | 单独流量增加应在健康容量内 |
| 12 | 一个应用 worker 在热点更新后长时间不提交 | 客户端事务泄漏 | 锁等待持有池连接 |
| 16 | 客户端版本切换，超时重试退避失当 | 实际发布失误 | 与锁队列叠加形成连接/CPU 放大；重试不增加逻辑分母 |
| 24 | 正常历史归档作业到达 | 运营排程，不一定是故障 | 清理/扫描与前台竞争，不应全部禁止 |
| 34 | 换租户再次触发同类事务泄漏 | 未修正的应用路径再现 | 已配置 scoped timeout 可预防；不重置保护 |
| 44 | 第二轮真实业务峰值 | 检查持久治理 | 单纯 kill、未改连接/重试治理可再恶化 |
| 50–60 | 正常负载与积压交付 | 观察接续能力 | 不能通过停止客户端获得成功率 |

满分处理：通过锁图、事务年龄、pool 排队和 request ledger 定位；授权范围内结束孤儿事务，修复公开客户端退避/限流配置，建立合适 role 事务保护；归档可延期但最终交付；再次泄漏被预防或快速局部缓解。等价方案不要求 kill 次数或动作顺序。

零处理：热点锁期间业务预算消耗，重试放大；即便事务最终由客户端 timeout 消失，损失和积压仍不能被覆盖。须实测证明 no-agent 超预算，不能只要求 blocker 到末尾仍存在。

错误处理：增大 max_connections 把排队转为内存压力；kill 所有会话使正常交易失败；关闭持久性获得 TPS；暂停交易输入。前两者按实际业务损失和授权 SP 判断，后两者违反合同。

验收：关键逻辑交易 good fraction、全局账本守恒/幂等、归档交付、最终业务容量；不要求两次泄漏逐一回复。需要真实外部池或应用池遥测，现有单连接 customer write 不够。

## 6. 实例二：批次入仓与准点报表

身份：`pg_warehouse_batch_reporting`。OLAP，TPC-DS 查询素材+明确报表交付清单，数据来源 TPC-DS 不等于直接照搬整套 benchmark。事实数据按 batch version 写入，报表绑定 batch cutoff。候选 horizon 90 分钟。

| t | 外部变化/注入 | 生产原因 | 联动/可预防分支 |
|---:|---|---|---|
| 0–10 | 常规 BI 查询与入仓 heartbeat | 正常数据仓库 | 记录计划、队列、交付，而非秒级 p95 |
| 10 | 批次 A 偏斜数据到达；维护窗口留下统计采样不足配置 | 数据分布漂移和发布遗漏 | 行数增长不必一定退化，须目标数据规模实测 |
| 18 | A 的汇总报表清单进入队列 | 固定下游交付 | 劣化计划占用 worker |
| 24 | scheduler 发布扩大分析并发 | 满足用户高峰的错误决策 | 长查询×并发×work_mem 产生 spill 或内存压力 |
| 32 | 例行备份读取到达 | 有期限的合法后台作业 | I/O 竞争恶化报表，暂停需有恢复/交付策略 |
| 48 | 批次 B 改变另一个维度的倾斜 | 同类分布问题再次出现 | 持久 statistics/调度治理可减少再次损失 |
| 55 | B 的报表批次提交 | 第二轮交付 | 清空队列不可算已完成 |
| 70–90 | 交付截止与追赶 | 下游使用结果 | 每份报表按自己的 deadline 验收 |

满分处理：定位真实报表/plan/统计，修复采样维护策略，按队列约束并发与 scoped work_mem，必要时取消并重跑单个尝试；备份节流、恢复并验证交付；A/B 报表在冻结业务 deadline 前返回正确结果。改 SQL 必须通过预先声明的等价结果合同，而非固定 plan。

零处理：积压+spill 使至少一个必需报表错过 deadline；即使备份自然结束使 I/O 缓解，已错过交付仍失败。正常满负载对照必须能交付，排除基础容量不足。

错误处理：全局大幅提高 work_mem 导致多个算子×并发耗尽内存；删 queued jobs 降低延迟；删业务数据减扫描；永久关闭备份/分析。分别由交付清单、结果真值、安全边界识别。

验收：必需报表按期正确交付、需声明新鲜度的报表使用指定 cutoff、备份真实完成可读取；job latency 从提交计到可消费结果，排队/重试不重置 deadline。无需分别验证 analyze fault 和 spill fault 已消失。

## 7. 实例三：同库 HTAP 资源隔离

身份：`pg_htap_shared_resource_isolation`。一个 PostgreSQL 主库上同时运行交易、订单运营看板和受限批量导出。候选 horizon 75 分钟；故障背景是缺乏分析准入控制，不是 PostgreSQL 自带完整资源组。

| t | 外部变化/注入 | 生产原因 | 联动/分支 |
|---:|---|---|---|
| 0–10 | 交易与轻量 dashboard 并存 | 日常混合负载 | 各自独立 SLO |
| 10 | 分析租户扩展为宽范围历史扫描 | 正常业务使用变化 | 缓存/I/O 压力；单独可在资源合同内承受 |
| 18 | 导出客户端开启长快照并停顿消费 | 客户端故障 | 持有 xmin，阻碍后续更新清理 |
| 25 | 交易写热点增大 | 生产流量变化 | churn + xmin 导致清理债务，和扫描争 I/O |
| 33 | dashboard 超时后有界但过密重试 | 应用退化反馈 | 交易/报表都受害，不能只保护高 QPS 一侧 |
| 46 | 新租户重现宽扫描和导出 | 再次同类需求 | 已有配额/role timeout 可防复发 |
| 60–75 | 正常业务和导出截止 | 检验恢复与公平性 | 停分析不算修复 |

满分处理：区分合法长查询和卡住的消费者；在授权 scheduler/role 层约束分析并发、事务时限和内存；可中止并从可验证 checkpoint 重跑导出；局部清理积压；保持交易与必需分析交付。终止一次 snapshot 可能同时消除 xmin 和清理压力，不要求逐事件处理。

零处理：快照影响后续维护、分析重试挤占资源，至少一类业务违约；若长快照自动结束，累计影响及交付仍决定 OP。

错误处理：只停全部分析则 OLTP 漂亮、分析交付失败；调高全局内存造成系统风险；VACUUM FULL 长锁进一步伤害在线交易。后者不是命令名自动 SP=False，依据公开维护授权与真实影响判定。

验收：交易 SLO AND 分析交付；受保护数据正确、未交付导出不可丢弃；后续正常工作负载仍有执行能力。没有按租户任意加权的总分；xmin/膨胀趋势用作解释及必要容量状态证据。

## 8. 实例四：分析副本新鲜度与 WAL 容量

身份：`pg_htap_replica_freshness`。物理 streaming replication 主备；交易只写主库，报表读副本。真实 replication slot、network throttling 和磁盘 quota 均限于该 run。候选 horizon 90 分钟。

| t | 外部变化/注入 | 生产原因 | 联动/分支 |
|---:|---|---|---|
| 0–12 | 写入、复制、周期报表 | 正常主备分析 | 通过 commit marker 映射时间和 LSN |
| 12 | 副本报表持有较长快照 | 正常重分析或错误 idle cursor | 按预配置 standby 策略可能阻碍回放或被取消 |
| 20 | 主库业务更新/清理增多 | 生产写入峰值 | 与快照形成 recovery conflict，不直接伪造 lag |
| 30 | 复制链路带宽降低 | 链路资源竞争 | lag 与 slot WAL 保留叠加 |
| 42 | 报表新鲜度要求进入关键交付段 | 下游决策需求 | “查询成功但读旧数据”也违约 |
| 50 | 链路恢复正常带宽 | 外部系统自然恢复 | 已错过交付不被抹去；积压可能仍需治理 |
| 60 | 新报表快照+第二轮更新 | 同类压力再现 | 第一轮有效策略可避免再次冲突 |
| 75–90 | 正常写入、复制追赶、交付 | 接续能力验证 | 不能 drop active slot 伪造磁盘恢复 |

满分处理：关联 standby conflict、replay/receive LSN、slot owner 和主库存储；通过授权报表重试/快照期限与 standby 策略权衡，控制可延期写作业；链路恢复后追赶并按要求交付。若有授权主库分析路由也可采用，但必须同时满足主库 OLTP 和报告新鲜度，不能默认存在路由能力。

零处理：回放冲突+限速导致交付读到过期数据，WAL 留存逼近容量边界；磁盘自然下降不修复历史 SLO。运行不能靠填满宿主盘体现故障，使用隔离卷和有界配额。

错误处理：删除活跃 slot、手删 WAL、提升副本导致双主、无界开启 hot_standby_feedback 把副本压力转移主库。配置本身未必违规，必须根据角色、保护策略和真实容量/正确性验收。

验收：OLTP 合同、报表正确性与 freshness、主备身份及持久性、复制可继续与容量余量。接受报表被合法取消再重试；不要求每次 recovery conflict 都被单独解释。主要新增能力是实际双节点、真实分析 job 和外部 ledger，当前单 PG provider 不足。

## 9. 实例五：在线发布、DDL 与可恢复回填

身份：`pg_oltp_online_change`。订单服务增加可选字段/派生数据及所需索引；发布与回填是必须最终交付的正常业务工作。候选 horizon 75 分钟。

| t | 外部变化/注入 | 生产原因 | 联动/分支 |
|---:|---|---|---|
| 0–10 | 原版本 OLTP、合法后台查询 | 发布前服务 | 固定订单账本与应用兼容合同 |
| 10 | 一个旧客户端长事务 | 客户端缺陷 | 可能成为 DDL blocker |
| 16 | 发布 worker 提交需强锁的 DDL | 不恰当发布策略 | 排队 DDL 阻塞后续新事务；不要求必然获得锁 |
| 24 | 大批回填启动或按持久任务队列等 schema ready | 数据迁移排程 | 依赖自然存在；框架不替 Agent 做恢复 |
| 32 | 发布 worker 因自身 timeout 重试 | 自动部署行为 | 重复 DDL/回填要求幂等，不允许重复业务写 |
| 44 | 促销交易高峰 | 发布撞业务 | 回填 WAL/checkpoint 与交易相互影响 |
| 52 | 新客户端再次出现长事务模式 | 重复故障 | scoped 保护可预防；不撤销修复 |
| 54–69 | 发布工具第二次自动重试；约束上线变更窗开启 | 变更日历 + 部署重试策略 | 发布计划收尾步（域校验约束、索引）落在窗内；未治理的第二长事务把窗内 ALTER 排队到 horizon 之后，交易二次阻塞 |
| 60–75 | 发布交付与交易持续观察 | 最终应用可用 | 不能永久取消发布获取好 SLO |

满分处理：识别队头 DDL、长事务和业务归属；合法取消/重排 DDL，小批可恢复回填，建立适合的锁/事务超时；约束上线窗与索引按计划顺序交付（允许用任务行 lock_timeout/窗口重排替代 kill，属等价解）；最终新旧应用读写语义正确、目标数据完整，业务损失在预算内。

零处理：锁队列或回填竞争导致 OLTP 违约/发布未完成；第二长事务把约束窗内 DDL 再度排队（第二段交易阻塞叠加促销高峰）；后续超时使 blocker 消失不代表整个任务失败或成功，结果合同决定。

错误处理：全量重写/全局 kill、跳过约束校验、把未完成批次标完成、永久取消发布。分别由损失、安全授权、schema/data verifier 与外部 job ledger 捕获。

验收：OLTP SLO AND 发布完成合同（schema、索引有效性、回填语义、应用正确性）；仅必要 GUC 约束。DDL、长事务、回填属于因果输入和工作目标，不是三个强制恢复 Event。

## 10. 三路径校准与阈值来源

每个实例先重复运行 healthy baseline（无故障、有正常业务/作业变化），再运行完整 reference、零动作和错误动作。三条路径都保持同数据/输入 seed、资源、交付清单和时钟；不能 reference 用小负载、模型用大负载。

- 完整 reference：通过公开工具安全满足 OP/SP；也验证至少一条等价修复或预防路径，不靠 injectors cleanup。
- 零动作：证明业务目标中至少一项稳定失败；并不要求每个 Event 保持故障。若全部自然恢复且仍达标，重新设计真实风险或删掉无价值故障，不能人为延长锁强迫失败。
- 错误动作：分别包括“只治症状”“危险捷径”“保护一种业务牺牲另一种”；预期失败由具体后果决定。任意坏动作失败不是 Hard 证据，难度仍需真实模型 pilot。

时间点是生产因果顺序的候选，强度/QPS/资源/deadline/预算没有在本文虚构定值。先给业务交付理由，再用 repeated healthy/reference 判断可测性与可解性。若业务目标在故障组合下即便 oracle 也不可能完成，应调整冗余、业务窗口、可控范围或故障组合，不能只为了让模型过关事后放宽门槛。

threshold ledger 必须记录单位、服务类别、目标值/允许区间、业务依据、资源/数据版本、样本量、置信/噪声证据、冻结日期。只做灵敏度展示可输出曲线但不能挑有利点报告 pass。30 分钟压力测评不能声称测得生产一个月 99.99% 可用性。

## 11. 必测反例和组合路径

1. 两故障被一次操作同时缓解，OP 可通过，不要求两个 action/report。
2. 第三个事件使第二个症状消失：业务按时完成可通过，任务交付缺失则失败。
3. 第一轮修复预防第二轮相同故障：valid、OP 可通过，不强制注入器打穿保护。
4. 长时间不可用、恢复后健康：历史损失保留；不拿最终探针替代 SLO。
5. 曾经回归后恢复：按业务预算与最终接续能力判，不因 regression_count>0 自动否决。
6. 秒级 bucket 边界移动不改变请求/job 结果；低 QPS 正常抖动不产生 p95 魔数。
7. 暂停所有 workload、删报表队列、篡改 watermark：拒绝虚假健康。
8. 坏查询在 DB 中超时有终态，run 有效；采集进程丢账则 invalid。
9. Agent 破坏 DB：由外部观察证明业务/SP 失败，不能洗成框架失效。
10. role/database/session GUC 冲突、新连接/pending_restart、旧连接继承均覆盖。
11. 原生 capability 不绑定 Case；同 capability 两次资源隔离，cleanup 不撤销修复。
12. OLAP jobs 跨结束边界、取消重试、队列等待、数据批次更新均不漏计。
13. HTAP 单侧漂亮另一侧停摆必失败；副本新鲜度与主库账本真实一致。
14. 三路径分别在 resolved/unresolved/prevented prefix 下执行，不能仅靠单事件回放证明组合可解。

## 12. 交付门槛

本文件是 PG 五实例的唯一目标合同；权威 architecture/evaluation/difficulty/guide 与本合同的生
产真实性与端到端语义保持一致，历史草案中的旧规则不得恢复。

代码交付需要新 schema、五个可运行 spec、原生 workloads/capabilities、端到端 evaluators、完整测试、资源隔离与 cleanup 证据。实验交付需要每实例三路径和真实模型试验；未完成前全部 measure-only / development_provisional。本次设计不宣称任何新实例已达满分路径或已具备工业事故实测校准。

## 13. 关联代码与参考文档

- [架构标准](../../standards/persistent-scenario/architecture.standard.md)、[评估标准](../../standards/persistent-scenario/evaluation.standard.md)、[难度标准](../../standards/persistent-scenario/difficulty.standard.md)、[实施指南](../../guides/persistent-scenario/implement-persistent-scenario.guide.md)。
- [PG 五类目录](../../catalogs/postgresql-scenarios.catalog.md)：机制参考，不是选题池约束。
