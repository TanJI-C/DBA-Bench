---
doc_id: guide.evaluation.semantic-diagnosis-matching
doc_type: guide
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: public
scope: [shared, scenario, persistent-scenario]
summary: Configures default Semantic Diagnosis Pass with local or external judges, explicit exact mode, and strict validation.
source_of_truth: code
related: [standard.evaluation.dp-op-sp]
language: zh-CN
---

# Semantic Diagnosis Pass

bounded Scenario 和 Persistent Scenario 的 Diagnosis Pass 默认使用 `semantic`。
通过 `llm_config.json` 中的模型名选择本地小模型或外部大模型；judge 与被测 Agent 的模型独立。
提交格式及 OP/SP 合同保持原有语义，评估边界见
[DP/OP/SP 标准](../../standards/evaluation/dp-op-sp.standard.zh-CN.md)。

## 选择 judge

将 `config/llm_config.example.json` 复制为 `config/llm_config.json`，配置所需的模型。
本地与外部模型使用同一个选择入口：

```json
{
  "Qwen/Qwen3-4B-Instruct-2507": {
    "url": "http://127.0.0.1:8000/v1",
    "api_key": "local",
    "provider": "openai",
    "semantic_judge": {"max_tokens": 2048}
  },
  "your-external-judge": {
    "url": "https://your-gateway.example/v1/chat/completions",
    "api_key": "REPLACE_ME",
    "provider": "openai",
    "semantic_judge": {"max_tokens": 8192}
  }
}
```

本地模式需要先启动 vLLM 等 OpenAI-compatible 服务，方法见下文。
默认 judge 模型名为 `Qwen/Qwen3-4B-Instruct-2507`，必须与服务实际提供的模型名一致。
如果服务使用本地 checkpoint 路径作为模型名，配置 key 也使用该路径。
外部模式可直接选择配置文件中已有的模型。原生 Anthropic 接口使用
`provider: anthropic`，URL 例如 `https://api.anthropic.com/v1/messages`；
OpenAI-compatible 接口使用 `provider: openai`，也是 provider 的默认值。
不要提交真实凭证。

所有场景入口都支持通过环境变量选择：

```bash
export AIOPS_DP_SEMANTIC_MODEL=your-external-judge
export AIOPS_DP_SEMANTIC_CONFIG=config/llm_config.json
conda run -n aiops python examples/run_pg_query_perf_stale_statistics_scenario.py \
  --mode llm --model your-agent-model --case branch_order_distribution_shift
```

提供诊断 CLI 参数的入口也可使用 `--diagnosis-semantic-model your-external-judge`
和 `--diagnosis-semantic-config config/llm_config.json`，显式 CLI 参数优先于环境变量。
不传 judge 模型时使用 judge 默认配置，不再复用 Agent 的 `--model`。
`aiopsbench persistent-scenario run <definition.yaml>` 也支持这些参数。

bounded Scenario 的程序化调用：

```python
from src.scenarios.runtime.orchestrator import OrchestratorRunConfig

run_config = OrchestratorRunConfig(
    diagnosis_semantic_model="your-external-judge",
    diagnosis_semantic_config_path="config/llm_config.json",
)
```

Persistent evaluator 和 `build_persistent_scenario_engine` 接受
`diagnosis_config=DiagnosisEvaluationConfig(...)`；该类定义在
`src.scenarios.evaluation.config`，使用相同字段与默认值。

## Benchmark manifest

```yaml
runtime:
  llm_config: config/llm_config.json
  diagnosis_match_mode: semantic
  diagnosis_semantic_model: your-external-judge
```

省略最后两个字段时，默认使用本地 Qwen 模型的 Semantic DP。
runner 将 manifest 的选择传给每个子进程，包括没有诊断 CLI 参数的脚本，
并覆盖父进程继承的 `AIOPS_DP_*` 配置。bounded 和 persistent 目标均适用。
被测 Agent 的模型仍由 `agents[].model` 选择。

## 显式使用 exact

确定性的 mock 或回归测试可在 manifest 中设置 `diagnosis_match_mode: exact`，
直接运行时使用 `AIOPS_DP_MATCH_MODE=exact`，或在支持该参数的入口传入
`--diagnosis-match-mode exact`。程序化运行可设置
`OrchestratorRunConfig(diagnosis_match_mode="exact")`。
exact 模式不需要 judge 模型或凭证。`mock`、`zero`、`llm` 等 Agent 模式不会隐式改变 DP 模式。

## Judge 请求设置

模型配置中的可选 `semantic_judge` 对象仅作用于 DP：

- `max_tokens`：输出预算，默认 `2048`。推理 token 也可能占用该预算；按需增加，
  并确保上下文容得下输入和输出。本地启动脚本默认上下文为 `4096`。
- `timeout_seconds` 与 `max_retries`：SDK 请求超时和重试次数，两种 provider 默认均为 `120.0` 和 `2`。
- `response_format`：仅 OpenAI-compatible 服务支持，默认或配置为 `null` 时不发送。
  服务支持 JSON mode 时可设置 `{"type": "json_object"}`。

截断响应（`finish_reason="length"` 或 `stop_reason="max_tokens"`）即使文本是合法 JSON 也会拒绝。
配置缺失、不支持的 provider、认证失败、JSON 格式错误、缺失或重复条件 ID、非法报告索引均直接报错。
发生失败时不会换请求参数或自动退回 exact。

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

可选的本地模型目录检查：

```bash
conda run -n aiops python scripts/start_dp_semantic_model.py \
  --status --model Qwen/Qwen3-4B-Instruct-2507 --host 127.0.0.1 --port 8000
```

启动和状态脚本通过 `GET /v1/models` 检查本地 vLLM 服务的模型目录；目录检查不能证明聊天请求一定成功。语义评估直接调用 `/chat/completions`，不查询 `/models`，因此网关返回空目录或未提供目录接口均不阻碍判分。实际聊天请求的连接、鉴权和模型错误直接向调用方抛出；不会静默使用 exact matcher。

## 判定协议

两种 provider SDK 使用相同的隐藏预期条件和提交报告内容。judge 为每个预期条件返回
`entailed_by`、`contradicted_by` 与 `reason`。bounded Scenario 的索引指向提交的诊断条件；
Persistent Scenario 的索引指向已完成的 mailbox 报告。Persistent 沿用结构化诊断加 summary 的
报告范围，不从修复动作推断诊断。空的 persistent 诊断合同仍为 `DiagnosisPass=None`，不请求 judge。

Case 的确定性诊断归一化应实现于 `BaseEvaluator._match_exact_diagnosis`。
两种模式共用的证据校验可覆盖 `DiagnosisPassFunc` 并先调用 `super()`，确保不绕过所选语义 matcher。

结果记录 `matching_mode`、`judge_model`、`judge_usage` 与逐条件 `semantic_judgments`。
OP 与 SP 继续独立验收。离线测试覆盖默认配置、同义改写、矛盾、端点选择、请求失败和非法输出；
模型自身准确率仍需用有代表性的诊断样本校准，这些测试不衡量准确率。
