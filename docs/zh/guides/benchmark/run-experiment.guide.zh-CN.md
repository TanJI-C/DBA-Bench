---
doc_id: guide.benchmark.run-experiment
doc_type: guide
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: agent_safe
scope: [shared, benchmark, postgres, tidb]
summary: Defines the reproducible manifest, planning, execution, resume, rerun, aggregation, and evidence workflow for benchmark experiments.
source_of_truth: code
related: [standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case, guide.persistent-scenario.implement-persistent-scenario]
language: zh-CN
---

# DBA-Bench 正式实验工作流

正式实验由 manifest 定义，运行产物写入 `artifacts/experiments/<experiment_id>/`。bounded
Scenario 按 `scenario × case × agent × repetition` 展开，Persistent Scenario 按
`scenario × agent × repetition` 展开；两者都通过稳定的 `run_id` 关联 trace、evaluator、stdout 和聚合结果。

## 1. 创建实验清单

从 `experiments/pg_smoke.example.yaml` 开始。bounded Scenario 至少明确：

- `experiment_id`；
- systems、categories 和 scenarios；
- agent ID、mode、model 和 `max_turns`；
- repetitions 与一一对应的 seeds；
- concurrency、timeout、端口、容器前缀和 fault snapshot 策略。

manifest 只接受文档定义的字段，未知字段直接报错。需要从完整矩阵中跳过已经完成或明确
不运行的单元时，使用顶层 `exclude_cells` 精确指定 scenario、case 和 agent：

```yaml
exclude_cells:
  - scenario: pg_health_check_table_bloat
    case: store_returns_table_index_bloat
    agent: agent-a
```

每个排除项必须匹配计划中的 bounded Scenario 单元，否则 planner 会报错。Persistent Scenario 不支持 `exclude_cells`。

`runtime.concurrency` 是整个实验同时运行的 run 上限。bounded Scenario 会先展开完整的
`scenario × case × agent × repetition` 矩阵，再按场景调度；Persistent Scenario 要求
`runtime.concurrency=1`，因为同一个 Persistent Scenario 的环境和持久 session 不能并行复制。

并行实验必须配置 `runtime.isolation`，并且每个所选 Case 都必须声明 `resources`。runner
根据通用资源合同计算每个 worker 的 CPU、内存需求，并按完整物理核和 NUMA node 分配
cpuset。标记为 host-exclusive 的 PostgreSQL 场景即使出现在并行 manifest 中也会独占宿主机；
TiDB QP 场景的 PD/TiKV 数据通过镜像组复用，仍按独立 Compose project、network、端口和容器
组进入隔离调度。完整配置见
`experiments/pg_system_failure_parallel.example.yaml`。

已存在的 `experiment_id` 不能换用另一份 manifest。实验配置变化时创建新的 ID。

## 2. 预览运行矩阵

```bash
conda run -n aiops aiopsbench experiment plan experiments/pg_smoke.example.yaml
```

## 3. 启动与恢复

```bash
conda run -n aiops aiopsbench experiment run experiments/pg_smoke.example.yaml
conda run -n aiops aiopsbench experiment resume <experiment_id>
conda run -n aiops aiopsbench experiment resume <experiment_id> --run-id <run_id>
conda run -n aiops aiopsbench experiment rerun <experiment_id> \
  --status failed --status timed_out
conda run -n aiops aiopsbench experiment rerun <experiment_id> \
  --status succeeded --run-id <run_id>
```

`resume` 只执行 `pending` run。`rerun` 必须显式给出原终态，不自动重试；每次重跑增加
attempt，并永久保留先前产物。正式执行要求 Git worktree clean；恢复或重跑还要求当前
checkout 与首次运行记录的 Git commit 完全一致。代码、prompt、场景、资源、模型、知识库
或 evaluator 发生变化时必须创建新的 `experiment_id`。收到 SIGINT/SIGTERM 时，runner
终止正在运行的子进程并记录 `interrupted`。

## 4. 产物

```text
artifacts/experiments/<experiment_id>/
├── manifest.yaml
├── environment.json
├── runs.jsonl
├── failures.jsonl
├── aggregate.json
├── aggregate.csv
└── runs/<run_id>/
    ├── run.json
    └── attempts/
        ├── 001/
        │   ├── attempt.json
        │   ├── trace.json
        │   ├── evaluator.json
        │   └── stdout.log
        └── 002/
            └── ...
```

每个 attempt 目录写完后不可修改，`attempt.json` 是该次执行的完整状态快照。bounded Scenario 使用 `trace.json` / `evaluator.json`，Persistent Scenario 使用
`persistent_scenario_trace.json` / `persistent_scenario_evaluation.json`。`run.json`
只反映逻辑 run 的当前状态和 attempt 索引。`run.json` 区分执行状态、
`DiagnosisPass`、`OutcomePass`、`SafePass` 和 `valid_for_aggregate`；基础设施失败的三个 Pass
保持为空，不计入通过率。
`environment.json` 固定 Git commit/diff hash、manifest/config hash、Python 依赖、Docker
版本、宿主平台和 worker 分配。每次 run 记录实际 cpuset、NUMA node、worker 容量和容器配额。

聚合结果会在每批运行结束时刷新，也可以单独重建：

```bash
conda run -n aiops python scripts/aggregate_experiment.py <experiment_id>
```

拆分执行的多个 experiment 可以合并为一个新的只读结果集。源实验必须存在、包含 run
记录并且逻辑单元不能重复，输出目录也不能预先存在：

```bash
conda run -n aiops python scripts/aggregate_experiment.py \
  <experiment_id_1> <experiment_id_2> \
  --output-experiment-id <combined_experiment_id>
```

## 5. 创建和冻结 Dataset

Dataset 显式选择每个逻辑格使用的原始 `experiment_id + run_id`，并为跨批次
命名不一致的 agent 指定稳定 `baseline_id`。统一 compose 入口从原始 `run.json` 按系统、
分类和 baseline 组合：

```bash
conda run -n aiops aiopsbench dataset compose <dataset_id> \
  --system postgresql \
  --category query_perf \
  --baseline <baseline-id> \
  --metric-contract <metric_contract_version> \
  --data-status provisional

conda run -n aiops aiopsbench dataset status <dataset_id>
conda run -n aiops aiopsbench dataset freeze <dataset_id>
```

`compose` 只读取 bounded Scenario 的 `artifacts/experiments/*/runs/*/run.json`，按
`system + scenario + case + baseline` 选择最新终态 run，并要求所选系统、分类和 baseline 的
矩阵完整。可重复传入 `--system`、`--category` 和 `--baseline` 组合多系统 Dataset。生成的 YAML
是显式、可 Git diff 的选择清单，不读取 dashboard 或审计报告。其他选择策略可以先生成 JSON
数组，再使用通用入口：

```bash
conda run -n aiops aiopsbench dataset create <dataset_id> \
  --runs-json <selected_runs.json> \
  --metric-contract <metric_contract_version> \
  --data-status provisional
```

每个 JSON 元素必须且只能包含 `experiment_id`、`run_id` 和 `baseline_id`。未冻结的 dataset
是 live 状态。`freeze` 要求所有选中 run 已进入终态，
并将每个逻辑单元固定到明确的 `run_id + attempt`，同时记录 `attempt.json`、trace、evaluator
和 stdout 的 SHA-256。生成的 `datasets/<dataset_id>.lock.json` 不允许覆盖。补跑或替换 run
后创建新的 `dataset_id`，使用以下命令查看差异：

```bash
conda run -n aiops aiopsbench dataset diff <old_dataset_id> <new_dataset_id>
```

## 6. 构建作图数据和论文图片

```bash
conda run -n aiops aiopsbench pipeline build <dataset_id>
conda run -n aiops aiopsbench pipeline verify <dataset_id>
```

`pipeline build` 只接受冻结 dataset，依次生成：

```text
artifacts/datasets/<dataset_id>/
├── runs.jsonl
├── runs.csv
├── aggregate.json
├── scenario_agent_summary.csv
└── provenance.json

paper/figures/output/datasets/<dataset_id>/
├── category_small_multiples.<data_status>.{pdf,png}
├── cost_pareto.<data_status>.{pdf,png}
├── diagnostic_depth.<data_status>.{pdf,png}
├── environmental_complexity.<data_status>.{pdf,png}
└── multimodal_temporal.<data_status>.{pdf,png}
```

`runs.csv` 每行对应 lock 中明确选择的一个 `run_id + attempt`，同时包含：

- dataset/lock、scenario annotation、trace/evaluator hash 等溯源字段；
- category、difficulty、diagnostic depth、environmental complexity、evidence modality 和
  temporal requirement；
- 执行状态、有效性、Diagnosis/Outcome/Safe Pass、evaluator identity 和完整 evaluation；
- turn/tool 行为计数、provider 上报或 trace 重建的 input/output token，以及可验证时的 USD cost。

无效或基础设施失败行保留在 CSV 中，但三个 Pass 字段为空，不按 0 分处理。成本核算使用
`data/model_token_costs.yaml` 中由 `pricing_version` 标识的冻结价格；每个条目按模型名声明
tokenizer backend、`cache_key` 与匹配状态（`encoding_proxy` / `family_proxy` /
`exact_open_model`），单价单位均为 USD / 1M tokens。`runs.csv` 中的成本是按冻结官方标价和
trace 重建的估算值，不是 provider 账单；必须同时保留 `pricing_version`、
`token_accounting_method` 和 `tokenizer_match`。任何缺失
类别、缺失 DP/OP/SP、hash 不一致、未知模型、错误 CSV 语义或过期 provenance 都直接报错。
五个绘图脚本只读取 `runs.csv`；`views/*.csv`、dashboard HTML、审计 Markdown 都不是正式
输入，原先解析这些内容的 `build_experiment_results.py` 已移除。

## 7. 使用 DVC 管理大体积数据

代码、manifest、dataset definition 和 lock 进入 Git；原始 experiment artifact 和 dataset
派生目录进入 DVC：

```bash
conda run -n aiops aiopsbench dataset track <dataset_id>
git add datasets/ artifacts/**/*.dvc .dvc .dvcignore
git commit -m "data: freeze <dataset_id>"
```

仓库已初始化 DVC，但没有预设 remote。确定 NAS、MinIO 或 S3 位置后只配置一次：

```bash
conda run -n aiops dvc remote add -d storage <remote-url>
conda run -n aiops dvc push
```

## 8. 浏览器检索

启动统一可视化服务：

```bash
conda run -n aiops python -m src.visualization.server
```

- `/`：Trace Viewer；
- `/raw-traces`：搜索、筛选并查看 `logs/traces` 原始 JSON；
- `/experiments`：按实验、场景、Agent 和状态检索 run；
- `/datasets`：按 dataset 查看 baseline × scenario_case 运行矩阵和聚合表；
- `/dashboard`：项目工作看板。

原始日志页面支持服务端分页、日期/场景/Agent/评分筛选、文件内查找、格式化/原文切换、
复制、下载和跳转 Trace Viewer。Dataset 状态页双击矩阵单元格可查看冻结或 live dataset
明确选择的 `run.json` 快照和对应 attempt 的 evaluator；聚合宽表支持横向滚动和自定义固定列。
