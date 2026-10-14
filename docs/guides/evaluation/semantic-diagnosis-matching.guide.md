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
    "provider": "openai"
  }
}
```

Do not commit real credentials to the repository. The `url` can point to vLLM or any other service compatible with `/chat/completions`.

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

Status check:

```bash
conda run -n aiops python scripts/start_dp_semantic_model.py \
  --status --model Qwen/Qwen3-4B-Instruct-2507 --host 127.0.0.1 --port 8000
```

Before every request the semantic judge calls `GET /v1/models` to check the endpoint and model ID. When the model is not started, the port is unreachable, authentication fails, or the service has not loaded the target model, evaluation raises a warning containing the startup and status commands above; it never silently uses the exact matcher.

## Judgment protocol

The semantic judge receives the scenario evaluator's hidden `ExpectedCondition` items and the Agent-submitted `diagnosis.conditions`, and returns for each hidden checkpoint:

- `entailed_by`: the indices of the submitted conditions that entail the checkpoint;
- `contradicted_by`: the indices of the submitted conditions that contradict the checkpoint;
- `reason`: a brief one-sentence rationale.

The judge must return all hidden checkpoints in one response. Missing fields, duplicate IDs, invalid indices, empty content, or API errors all raise an error immediately; there is no fallback to the `exact` matcher.

Semantic mode only replaces DP. OP is still re-verified through the environment, and SP still reads the normalized trace.

## Current limitations

At this stage only the interface and offline contract tests are complete; after the model service is integrated, calibration is still needed using samples covering paraphrases, symptoms masquerading as root causes, reversed causal direction, and noisy root causes.
