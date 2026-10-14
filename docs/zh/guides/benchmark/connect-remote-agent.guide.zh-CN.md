---
doc_id: guide.benchmark.connect-remote-agent
doc_type: guide
status: canonical
audience: [authoring, maintainer, reviewer]
exposure: agent_safe
scope: [shared, postgres, tidb, benchmark]
language: zh-CN
summary: 通过 remote Agent 模式和 HTTP 协议，在 bounded Scenario 中运行进程外 Agent。
source_of_truth: code
related: [guide.benchmark.run-experiment, guide.benchmark.run-human-browser-console, standard.evaluation.dp-op-sp]
---

# 接入远程 Agent

`remote` 模式支持在 bounded Scenario 中运行独立于 benchmark 进程的 Agent 服务，
服务可以用任意语言编写。外部服务负责模型调用和决策，benchmark 是 HTTP 客户端，
也是环境操作的唯一执行方：`RemoteAgent`（`src/agents/remote_agent.py`）请求一个动作，
通过 `EnvGateway` 执行，将结果交回服务，再请求下一个动作。即使多个动作来自同一次
模型回复，工具仍按顺序执行。评估使用记录的工具操作历史和提交的诊断报告。

[English guide](../../../guides/benchmark/connect-remote-agent.guide.md)

如果 Agent 自行连接数据库或宿主机，相关操作就不会进入历史记录，Safe Pass 和依赖
操作历史的 Outcome Pass 检查会遗漏这些行为。所有观察和修改都应通过工具完成。

## Manifest

```yaml
agents:
  - id: my-agent          # 写入 run 的 Agent ID
    mode: remote
    model: my-agent-v1    # 可选标签，默认是 "remote"
    max_turns: 30
    settings:
      endpoint: http://127.0.0.1:9000/agent
```

`settings` 必须且只能包含 `endpoint`，其值是绝对 `http(s)` URL。`remote` 仅支持
bounded Scenario；不接受 `reasoning_effort` 和 `max_output_tokens`，因为 benchmark
不会替这个 Agent 调用模型。

## 协议

请求和响应正文均为 JSON，路径相对于 `endpoint`。

| 请求 | 请求正文 | 响应 |
|---|---|---|
| `POST /sessions` | `experiment_id`、`agent_id`、`run_id`、`scenario_id`、`case_id`、`system_prompt`、`user_prompt`、`tools`（函数 schema）、`tool_help`、`max_turns` | `{"id": "<session id>"}` |
| `GET /sessions/{id}/next` | 无 | `{"action": {...}}`；35 秒内没有动作时返回 `{"action": null}` |
| `POST /sessions/{id}/result` | `action_id`、`result`（工具的 JSON 结果）、`turns_used`、`max_turns` | 任意 JSON 对象，例如 `{}`；其内容不会被使用 |
| `POST /sessions/{id}/finish` | `evaluation`、`error` | 任意 JSON 对象，例如 `{}`；其内容不会被使用 |

动作格式为 `{"id", "api", "args", "thinking"?, "turn_id"?, "usage"?}`：

- `api` 是 `tools` 中的工具名，或 `submit` / `exit`。`submit` 的参数为
  `{"report": ...}`，报告结构见 [protocol.py](../../../../src/scenarios/evaluation/protocol.py)。
- `thinking` 是可选文本，随动作记录。
- `turn_id` 是服务提供的可选标识，计数规则见下文。
- `usage` 是可选的模型 token 用量记录列表，上报规则见下文。

`submit` 返回报告供评估使用；`exit` 以未提交诊断的错误结束运行。两者都不执行环境
操作、不消耗工具轮数，也不会收到 `/result`。

## 轮数计算

`turns_used` 统计工具动作的分组数。连续动作使用相同且非 null 的 `turn_id` 时只计
一轮；缺少 `turn_id`、值为 null 或 ID 发生变化时，计入新的一轮。例如，
`a, a, b` 计两轮，`a, b, a` 计三轮。达到 `max_turns` 后，再开启一轮工具操作会
导致运行失败；沿用当前 ID 的动作仍会执行。服务应在预算耗尽时提交报告。

接入方应只为同一次模型回复已经选定的动作复用 ID。如果 Agent 读取工具结果后重新
决策，下一个动作应使用新 ID。这是服务实现约定：benchmark 看不到外部模型调用，
无法强制验证。新决策仍复用 ID 会少计轮数，因此 `max_turns` 不能独立限制真实的
模型调用次数或工具动作总数。

Trace viewer 的 Turn 编号来自动作记录，不一定等于 `turns_used`，也不一定等于
外部模型调用次数。trace 包含工具动作及结果、上报的 `thinking` 和 `llm_usage`，
不包含外部服务的完整对话或内部模型请求。

## Usage 与成本上报

benchmark 不会向模型服务商查询 usage，外部服务必须将其附在动作中。最后一次工具
操作之后产生的模型调用，可以通过 `submit` 动作上报：

```json
{
  "action": {
    "id": "action-1",
    "api": "execute_sql",
    "args": {"sql_query": "SELECT 1"},
    "turn_id": "response-1",
    "usage": [{
      "provider": "openai",
      "model": "my-agent-v1",
      "input_tokens": 1200,
      "output_tokens": 150,
      "cached_input_tokens": 200,
      "cache_write_input_tokens": 0
    }]
  }
}
```

每条记录必须包含非空字符串 `provider`、`model`，以及非负整数 `input_tokens`、
`output_tokens`。输入 token 总数包含缓存 token；可选的 `cached_input_tokens` 和
`cache_write_input_tokens` 默认是零。已上报但格式错误的记录会导致运行失败。

每次实际模型调用只上报一次。如果一次回复产生多个动作，只在其中一个动作上附上
该次 usage，框架会追加记录，不会去重。要报告完整用量，就必须包含内部规划和总结
调用。usage 与 `turn_id` 独立，一个动作可以携带多次模型调用的用量。

不提供 usage 不影响运行和 DP/OP/SP 评估。完全没有记录时，效率评估标记为
unmetered；漏报部分调用会使总量不完整。后续生成 token/成本表时，无法从
`RemoteAgent` 的 trace 重建缺失用量。当前成本计算按 run 配置的模型定价，不会按
每条 usage 记录中的模型分别选择价格。要使用这条成本分析路径，应完整上报所有
调用、使用单一模型，并将 manifest 的 `model` 设为 token 成本配置中对应的模型项。
这条路径不能正确计算多模型混用的成本。

## 会话结束

提交 `submit` 后，服务应保持可用，直到收到并响应 `/finish`。benchmark 在评估、
清理和 trace 导出完成后发送这条通知；运行失败时由 `error` 字段提供错误信息。
每次 HTTP 请求超时为 40 秒；`/next` 长轮询应在 35 秒内返回动作或
`{"action": null}`。null 响应会继续轮询，整个运行仍受实验 run timeout 约束。

当前 `/finish` 请求失败会向外抛出，导致进程失败。即使评估结果已经写入 trace，
正式 runner 也会将该 run 排除在正常评分聚合之外。服务必须处理 `/finish`，并返回
例如 `{}` 的 JSON 对象。

## 运行

先启动 Agent 服务，再按[正式实验指南](run-experiment.guide.zh-CN.md)规划并运行实验：

```bash
conda run -n aiops aiopsbench experiment plan experiments/my-remote.yaml
conda run -n aiops aiopsbench experiment run experiments/my-remote.yaml
```
