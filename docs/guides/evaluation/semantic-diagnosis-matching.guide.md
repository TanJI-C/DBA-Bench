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
language: en
---

# DP Semantic Matching Guide

This document describes the implementation of the semantic matcher. The overall DP design, the condition protocol shared by the exact and semantic paths, and the boundary between DP and OP/SP are governed by the [DP, OP, and SP design principles](../../standards/evaluation/dp-op-sp.standard.md).

DP uses the `exact` matcher by default, continuing to match exactly against the aliases declared by the scenario evaluator. To evaluate open-ended expressions, set `OrchestratorRunConfig.diagnosis_match_mode` to `semantic`; semantic mode does not change the Agent's submission schema, nor does it expose candidate root-cause categories to the Agent.

## Usage

Set it explicitly for programmatic runs:

```python
run_config = OrchestratorRunConfig(
    diagnosis_match_mode="semantic",
    diagnosis_semantic_model="Qwen/Qwen3-4B-Instruct-2507",
    diagnosis_semantic_config_path="config/llm_config.json",
)
```

All existing scenario entry points can also be switched via environment variables, without modifying each entry script individually:

```bash
export AIOPS_DP_MATCH_MODE=semantic
export AIOPS_DP_SEMANTIC_MODEL=Qwen/Qwen3-4B-Instruct-2507
export AIOPS_DP_SEMANTIC_CONFIG=config/llm_config.json
conda run -n aiops python examples/run_pg_query_perf_stale_statistics_scenario.py \
  --mode mock --case branch_order_distribution_shift
```

`AIOPS_DP_MATCH_MODE` must be either `exact` or `semantic`; when unset it is `exact`. Once a model is selected for semantic mode, the config file must contain a corresponding OpenAI-compatible configuration:

```json
{
  "Qwen/Qwen3-4B-Instruct-2507": {
    "url": "http://127.0.0.1:8000/v1",
    "api_key": "local",
    "provider": "openai",
    "semantic_judge": {
      "max_tokens": 2048,
      "response_format": null
    }
  }
}
```

Do not commit real credentials to the repository. The `url` can point to vLLM or any other service compatible with `/chat/completions`.

### Judge request settings

The optional `semantic_judge` object configures only the diagnosis judge, independently of the Agent:

- `max_tokens`: output-token budget, default `2048`. For reasoning models, this budget also includes reasoning tokens. Set it to, for example, `8192` or `16384` as needed; the service's context window must fit the input plus this budget. The local startup script's default context window is only `4096`, so increase `--max-model-len` before using a larger budget there.
- `response_format`: omitted from the request by default, including when configured as `null`. For services that support JSON mode, set `{"type": "json_object"}` explicitly. The prompt and strict JSON validation apply in either mode.
- `timeout_seconds` and `max_retries`: OpenAI SDK request timeout and retry count, default `120.0` and `2`.

These settings can also be passed to `OpenAISemanticDiagnosisJudge(...)` directly. There is no automatic retry with different request settings or fallback to exact matching. A response with `finish_reason="length"` is rejected before parsing, even if it contains valid JSON. The error includes the model, configured budget, finish reason, and token usage. Increase the budget or configure reasoning at the model service; a larger budget cannot guarantee that a model will finish.

## Start the small model

The startup script is located at [`scripts/start_dp_semantic_model.py`](../../../scripts/start_dp_semantic_model.py) and by default starts an FP16 vLLM service for Qwen3-4B:

```bash
conda run -n aiops python scripts/start_dp_semantic_model.py \
  --model Qwen/Qwen3-4B-Instruct-2507 \
  --host 127.0.0.1 \
  --port 8000
```

By default the script uses `max_model_len=4096`, `gpu_memory_utilization=0.90`, and single-GPU tensor parallelism. On current single-GPU cards with 11GB of VRAM, if FP16 does not fit in memory, you can switch to a quantized checkpoint provided the model service confirms support:

```bash
conda run -n aiops python scripts/start_dp_semantic_model.py \
  --model Qwen/Qwen3-4B-Instruct-2507 \
  --quantization awq
```

Use `--detach` to start it in the background; logs are written to `logs/dp_semantic_model.log` by default:

```bash
conda run -n aiops python scripts/start_dp_semantic_model.py \
  --model Qwen/Qwen3-4B-Instruct-2507 --detach
```

Optional local model-catalog check:

```bash
conda run -n aiops python scripts/start_dp_semantic_model.py \
  --status --model Qwen/Qwen3-4B-Instruct-2507 --host 127.0.0.1 --port 8000
```

The startup/status script uses `GET /v1/models` to inspect the local vLLM service. This is a catalog check, not proof that a chat request will succeed. Semantic evaluation calls `/chat/completions` directly and does not query `/models`; gateways may return an empty catalog or omit that endpoint. Connection, authentication, and model errors from the actual chat request propagate to the caller; evaluation never silently uses the exact matcher.

## Judgment protocol

The semantic judge receives the scenario evaluator's hidden `ExpectedCondition` items and the Agent-submitted `diagnosis.conditions`, and returns for each hidden checkpoint:

- `entailed_by`: the indices of the submitted conditions that entail the checkpoint;
- `contradicted_by`: the indices of the submitted conditions that contradict the checkpoint;
- `reason`: a brief one-sentence rationale.

The judge must return all hidden checkpoints in one response. Missing fields, duplicate IDs, invalid indices, empty content, or API errors all raise an error immediately; there is no fallback to the `exact` matcher.

Semantic mode only replaces DP. OP is still re-verified through the environment, and SP still reads the normalized trace.

## Current limitations

At this stage only the interface and offline contract tests are complete; after the model service is integrated, calibration is still needed using samples covering paraphrases, symptoms masquerading as root causes, reversed causal direction, and noisy root causes.
