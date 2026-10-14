---
doc_id: guide.evaluation.semantic-diagnosis-matching
doc_type: guide
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: public
scope: [shared, scenario, persistent-scenario]
summary: Describes the exact and semantic DP matcher configuration, validation protocol, and non-fallback behavior.
source_of_truth: code
related: [standard.evaluation.dp-op-sp]
language: zh-CN
---

# DP 语义匹配指南

本文是 semantic matcher 的实现说明。DP 的总体设计、精确/语义两条路径共用的条件协议，以及
DP 与 OP/SP 的边界，统一以 [DP、OP、SP 设计原则](../../../standards/evaluation/dp-op-sp.standard.md) 为准。

DP 默认使用 `exact` matcher，继续按场景 evaluator 声明的 alias 精确匹配。需要评估开放表达时，将 `OrchestratorRunConfig.diagnosis_match_mode` 设为 `semantic`；语义模式不改变 Agent 的提交 schema，也不把候选根因类别暴露给 Agent。

## 使用方式

程序化运行时显式设置：

```python
run_config = OrchestratorRunConfig(
    diagnosis_match_mode="semantic",
    diagnosis_semantic_model="Qwen/Qwen3-4B-Instruct-2507",
    diagnosis_semantic_config_path="config/llm_config.json",
)
```

所有现有场景入口也可以通过环境变量切换，不需要逐个修改入口脚本：

```bash
export AIOPS_DP_MATCH_MODE=semantic
export AIOPS_DP_SEMANTIC_MODEL=Qwen/Qwen3-4B-Instruct-2507
export AIOPS_DP_SEMANTIC_CONFIG=config/llm_config.json
conda run -n aiops python examples/run_pg_query_perf_stale_statistics_scenario.py \
  --mode mock --case branch_order_distribution_shift
```

`AIOPS_DP_MATCH_MODE` 只能是 `exact` 或 `semantic`。未设置时为 `exact`。语义模式选择模型后，配置文件必须存在对应的 OpenAI-compatible 配置：

```json
{
  "Qwen/Qwen3-4B-Instruct-2507": {
    "url": "http://127.0.0.1:8000/v1",
    "api_key": "local",
    "provider": "openai"
  }
}
```

不要把真实凭证提交到仓库。`url` 可以指向 vLLM 或其他兼容 `/chat/completions` 的服务。

## 启动小模型

启动脚本位于 [`scripts/start_dp_semantic_model.py`](../../../../scripts/start_dp_semantic_model.py)，默认启动 Qwen3-4B 的 FP16 vLLM 服务：

```bash
conda run -n aiops python scripts/start_dp_semantic_model.py \
  --model Qwen/Qwen3-4B-Instruct-2507 \
  --host 127.0.0.1 \
  --port 8000
```

脚本默认使用 `max_model_len=4096`、`gpu_memory_utilization=0.90`、单卡张量并行。当前 11GB 显存的单卡 GPU 如果 FP16 显存不足，可在模型服务确认支持的前提下改用量化 checkpoint：

```bash
conda run -n aiops python scripts/start_dp_semantic_model.py \
  --model Qwen/Qwen3-4B-Instruct-2507 \
  --quantization awq
```

使用 `--detach` 可后台启动，日志默认写入 `logs/dp_semantic_model.log`：

```bash
conda run -n aiops python scripts/start_dp_semantic_model.py \
  --model Qwen/Qwen3-4B-Instruct-2507 --detach
```

状态检查：

```bash
conda run -n aiops python scripts/start_dp_semantic_model.py \
  --status --model Qwen/Qwen3-4B-Instruct-2507 --host 127.0.0.1 --port 8000
```

语义 judge 每次请求前都会调用 `GET /v1/models` 检查 endpoint 和模型 ID。模型未启动、端口不可达、鉴权失败或服务未加载目标模型时，评估会直接抛出包含上述启动命令和 status 命令的 warning；不会静默使用 exact matcher。

## 判定协议

语义 judge 收到场景 evaluator 的隐藏 `ExpectedCondition` 和 Agent 提交的 `diagnosis.conditions`，对每个隐藏检查点返回：

- `entailed_by`：支持该检查点的 submitted condition 下标；
- `contradicted_by`：与该检查点矛盾的 submitted condition 下标；
- `reason`：一句简短理由。

judge 必须一次返回全部隐藏检查点。返回缺字段、重复 ID、非法下标、空内容或 API 错误都会直接抛错；不会退回 `exact` matcher。

语义模式只替换 DP。OP 仍通过环境重新验证，SP 仍读取规范化 trace。

## 当前限制

本阶段只完成接口和离线契约测试；模型服务联调后还需要用同义、症状冒充根因、因果方向相反和噪声根因样本进行校准。
