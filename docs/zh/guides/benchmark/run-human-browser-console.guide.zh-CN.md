---
doc_id: guide.benchmark.run-human-browser-console
doc_type: guide
status: canonical
audience: [maintainer, reviewer]
exposure: internal
scope: [shared, postgres, tidb, benchmark]
summary: 使用浏览器工具工作台运行现有 bounded case，操作工具、查看结果、绘图并提交结构化作答。
source_of_truth: code
related: [standard.scenario.architecture, standard.evaluation.dp-op-sp]
language: zh-CN
---

# 人类浏览器工作台

在仓库根目录启动统一可视化服务：

```bash
conda run -n aiops python scripts/serve_visualization.py
```

打开 `http://127.0.0.1:9235/human`。远程主机可以用 SSH 转发：

```bash
ssh -N -L 9235:127.0.0.1:9235 <user>@<host>
```

工作台与 Trace Viewer、实验运行、实验结果使用同一个服务。若服务在本次功能加入前已经启动，需要先停止旧进程，再从包含本功能的分支启动。页面面向可信本地/SSH 使用；参与者编号用于记录身份，不是登录认证。

## 开始作答

选择数据库、场景、case，输入参与者编号即可开始。PG 的 CPU 集合默认留空，服务端复用 benchmark 资源分配器，按题目资源需求和机器拓扑自动选择 CPU 与 NUMA 内存节点，将分配结果写入 manifest，并使用相同 CPU 集合启动 runner。资源不足会明确报错。

运行设置允许修改数据库端口和手动指定 PG CPU 集合。管理员需要固定资源时可填写完整物理核集合（含 SMT 线程）；例如 `8-11,32-35` 只适用于验证时这台主机的拓扑。自动分配和手动绑定均不代表独占预约，共享主机的正式实验仍需管理员检查其他负载。

点击「准备环境并开始」会生成一次独立实验 manifest，先执行 runner dry-run，再串行运行选中的一个 case。准备完成后自动显示题目、约束与工具。准备失败会显示错误。可以在「开始一道题」区域终止准备中或执行中的运行，runner 负责清理。

目录来自正式 Scenario registry，包含当前所有有正式入口的 bounded case。新增注册 case 自动出现。Persistent Scenario 不在此入口支持范围内。一次只启动一道题；多个浏览器可以查看同一会话，服务端只接受一条待执行动作，避免重复并发修改数据库。

## 工具操作

工具列表与 LLM Agent 共用环境的已启用工具 schema。普通 TiDB case 默认提供 8 个工具：`query_metrics`、`execute_sql`、`manage_cluster`、`read_log`、`search_knowledge`、`help`、`submit`、`exit`。HC04 备份恢复题目注册恢复运行时后才额外提供 4 个归档检查、修复和隔离恢复工具；清理时撤销。PG 工具面继续遵循所选 `TOOL_PROFILES`，两个知识库实现对外共用 `query_knowledge_base` 别名。

- `execute_sql`：多行 SQL 编辑器，Ctrl/⌘ + Enter 执行。保留 SQL、目标、笔记、耗时和原始结果。表格支持筛选、排序与 CSV 导出，NULL 单独显示，截断结果明确提示。
- `query_metrics`：指标下拉框来自当前 case 的实际 schema。支持目标、UTC 起止时间、步长与点数参数；返回窗口及完整原始数据可查。时序结果自动展开图表。
- `manage_instance`：PG 动作下拉框、目标与配置值表单。实例停止、重启、修改配置等操作在执行前确认。
- `manage_cluster`：TiDB 资源和操作联动选择，目标要求、操作参数和约束随选择变化。通过「发现可用目标」执行该操作合同声明的 discovery 工具，再填写返回的稳定实例标识。
- `read_log`：按数据库提供的日志类型/组件目标、行范围、关键字、UTC 时间窗口读取。结果可再次筛选日志行，截断与分页信息可查。
- `query_knowledge_base` / `search_knowledge`：问题文本与检索范围表单；可选值、结果数量和长度限制遵循实际工具 schema。
- `help`：工具列表及完整参数说明；复杂工具的资源、操作、指标定义以表格和可展开区域展示。
- `submit`：使用结构化表单添加诊断条件，每行填写一条证据、改动或验证；可提供 case 所需的 JSON plan。服务端使用项目 `StructuredReport` 校验，错误报告可以修改后重新提交。提交成功后停止工具操作，显示 DP/OP/SP 评估结果。
- `exit`：结束作答并清理，本次运行记录为失败/中断，不会伪装成已完成的评测。
- 其他 case 专用工具（包括备份检查、归档修复和隔离恢复）按实际 schema 生成参数表单，不需要前端注册新工具名。

所有工具结果保留原始返回。工具返回的数据库错误会显示在对应操作记录中，可以修正参数继续；基础设施异常会结束运行并显示失败。

## 通用绘图

点击结果中的「绘制时序 / 数据图」，选择数据表、X 列、数值 Y 列及分组列。X 轴可以使用 UTC 时间或数值。指标 `series.<target>.timestamps` 数组、长历史压缩网格 `{start,end,step_seconds,count}`、SQL 的 `columns/result` 表格、对象行数组及二元时序点数组均可读取。

图表支持图例开关、滚轮缩放、拖动平移、悬停采样值和重置缩放。缺失数值显示为断点；没有可绘图数据时显示空状态。SQL 返回任意时间列与数值列即可绘图，不需要专用 SQL API。比较不同量纲时分别选择相应数据/指标，避免把数值幅度误读为同一单位。

## 生命周期与产物

`BrowserHumanAgent` 通过 HTTP 长轮询接收浏览器动作，实际工具访问仍走 `BaseAgent.execute → EnvGateway → Environment`。题目、system prompt、工具 schema 和公开工具帮助由现有 orchestrator 注入；控制台不会读取 reference report、故障真值或 evaluator 内部状态作为作答提示。

提交由 Agent 消费，随后 orchestrator 完成评估、故障恢复、环境 teardown、trace 导出，最后通知控制台。runner 继续记录实验状态、资源与清理证据。

- 临时 manifest：`experiments/tmp/human-<id>.yaml`。
- 实验真值：`artifacts/experiments/human-<id>/runs/<run_id>/attempts/<NNN>/{trace,evaluator,attempt}.json`。
- 浏览器会话与笔记：`artifacts/human-console/sessions/<session_id>.json`。
- 启动/准备日志：`artifacts/human-console/human-<id>.log`。

刷新浏览器可以恢复会话、操作历史及已保存的工具参数草稿。服务重启不会恢复活跃 Agent 通道，旧会话明确显示失败；需要从 runner 中断并清理旧运行后再开始新题。已完成会话可查看、导出，不能继续执行工具。

也可以直接编写 runner manifest，Agent 配置如下：

```yaml
agents:
  - id: participant-001
    mode: human
    max_turns: 1000
    settings:
      console_url: http://127.0.0.1:9235
      participant: participant-001
```

其余 benchmark、exclude_cells 和 runtime 配置遵循标准 experiment manifest。人类模式无需模型与 LLM 凭据，现有入口的 `llm` 执行分支由 Agent 工厂选择真实的人类 Agent。长轮询等待时间属于参与者作答时间；human Agent 不按 LLM 对话轮数自动提交，由实验总超时控制运行上限。

## 浏览器验收复现

浏览器验收脚本通过 Playwright 实际填写工作台、执行工具、刷新页面、提交报告并检查评估结果。它使用现有 mock/reference fixture 作为操作输入，是 UI 验收，不是人类受试者实验。运行前按项目实验流程验证对应 case 的 mock smoke，并保证没有其他题目占用所选端口。

```bash
conda run -n aiops python scripts/check_human_console_browser.py --system postgresql
conda run -n aiops python scripts/check_human_console_browser.py --system tidb
```

不传 `--cpuset-cpus` 时，浏览器验收保持运行设置关闭，覆盖 CPU 留空的默认启动路径；传入时覆盖手动指定路径。验收完成后，可用下面的脚本在实际访问地址检查结果区控件，包括 HTTP 上的复制粘贴、JSON/CSV 下载、筛选排序、参数复用、图表和会话导出：

```bash
conda run -n aiops python scripts/check_human_console_results_browser.py --url http://<host>:9235
```

上述测试覆盖指定案例及脚本中列出的操作，不代表遍历了所有工具的参数组合或所有可能改变环境的管理动作。

工具面回归可运行 `conda run -n aiops python scripts/check_human_console_tools_browser.py`。它通过临时 HTTP 服务和真实浏览器检查 TiDB 通用/HC04 活动/清理后三种工具面、PG 四种 profile，以及后端拒绝未提供的工具；使用真实环境 schema，但不部署数据库、不代表完整题目验收。结果写入 `artifacts/human-console/tool-scope/browser-check.json`。

测试环境需要 Playwright 与 Chromium。脚本在 `artifacts/human-console/` 保存截图和 `*-acceptance.json`；实际 benchmark 产物仍由 runner 保存。脚本验证 SQL 表格、日志、工具帮助、PG 配置查询、TiDB 资源发现、指标图表、任意 SQL 时间表格绘图、刷新恢复和结构化提交。
