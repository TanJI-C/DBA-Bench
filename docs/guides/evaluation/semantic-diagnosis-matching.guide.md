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
language: en
---

# Semantic Diagnosis Pass

Diagnosis Pass defaults to `semantic` for bounded Scenarios and Persistent Scenarios.
Choose a local small model or an external model by its key in `llm_config.json`;
the diagnosis judge is independent of the Agent model. The submission schema and
OP/SP contracts are unchanged. The [DP/OP/SP standard](../../standards/evaluation/dp-op-sp.standard.md)
defines the evaluation boundaries.

## Choose the judge

Copy `config/llm_config.example.json` to `config/llm_config.json` and configure the
models you need. These are two alternatives using the same judge selection:

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

For a local model, start an OpenAI-compatible service such as vLLM (see below).
The default judge key is `Qwen/Qwen3-4B-Instruct-2507`; it must match the name served
by the endpoint. A local checkpoint path can also be used as the model key when
the server serves that name. For an external model, select an existing model key
in your config. Native Anthropic endpoints are supported with `provider: anthropic`
and a URL such as `https://api.anthropic.com/v1/messages`. OpenAI-compatible
endpoints use `provider: openai` (the default). Never commit real credentials.

All scenario entry points support environment selection:

```bash
export AIOPS_DP_SEMANTIC_MODEL=your-external-judge
export AIOPS_DP_SEMANTIC_CONFIG=config/llm_config.json
conda run -n aiops python examples/run_pg_query_perf_stale_statistics_scenario.py \
  --mode llm --model your-agent-model --case branch_order_distribution_shift
```

Entry points exposing diagnosis CLI options also accept
`--diagnosis-semantic-model your-external-judge` and
`--diagnosis-semantic-config config/llm_config.json`. Explicit CLI values override
the environment. Omitting `--diagnosis-semantic-model` selects the configured judge
default; it does not reuse `--model`. The same options are available for
`aiopsbench persistent-scenario run <definition.yaml>`.

For programmatic bounded runs:

```python
from src.scenarios.runtime.orchestrator import OrchestratorRunConfig

run_config = OrchestratorRunConfig(
    diagnosis_semantic_model="your-external-judge",
    diagnosis_semantic_config_path="config/llm_config.json",
)
```

Persistent evaluators and `build_persistent_scenario_engine` accept a
`diagnosis_config=DiagnosisEvaluationConfig(...)` from
`src.scenarios.evaluation.config`, with the same fields and defaults.

## Benchmark manifest

```yaml
runtime:
  llm_config: config/llm_config.json
  diagnosis_match_mode: semantic
  diagnosis_semantic_model: your-external-judge
```

Omitting the last two fields selects Semantic DP with the local Qwen model key.
The runner passes the manifest selection to every child process, including scripts
without diagnosis CLI options, and overrides inherited `AIOPS_DP_*` settings.
This applies to bounded and persistent targets. Agent model selection remains in
`agents[].model`.

## Explicit exact matching

For deterministic mocks or regression tests, select `diagnosis_match_mode: exact`
in the manifest, `AIOPS_DP_MATCH_MODE=exact` for direct runs, or
`--diagnosis-match-mode exact` on entry points exposing the option. Programmatic
runs can set `OrchestratorRunConfig(diagnosis_match_mode="exact")`.
Exact mode needs no judge model or credentials. Agent modes such as `mock`, `zero`,
and `llm` do not implicitly change the selected matcher.

## Judge request settings

The optional model-level `semantic_judge` object configures only DP:

- `max_tokens`: output budget, default `2048`. Reasoning tokens may consume this
  budget. Increase it when needed, and ensure the model context fits input plus
  output; the local startup script defaults to a `4096`-token context.
- `timeout_seconds` and `max_retries`: SDK request timeout and retry count,
  default `120.0` and `2` for both providers.
- `response_format`: OpenAI-compatible services only, omitted by default or when
  `null`. Use `{"type": "json_object"}` if the endpoint supports JSON mode.

A truncated response (`finish_reason="length"` or `stop_reason="max_tokens"`)
is rejected even if its text parses as JSON. Missing config, unsupported providers,
authentication failures, invalid JSON, missing/duplicate condition IDs, and invalid
report indexes raise errors. Evaluation never changes request settings or switches
to exact matching after a failure.

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

Both provider SDKs send the same hidden expected conditions and submitted report
content. The judge returns `entailed_by`, `contradicted_by`, and `reason` for every
expected condition. These indexes refer to the submitted conditions for bounded
Scenarios, or the completed mailbox reports for Persistent Scenarios. Persistent
reports retain their existing scope: structured diagnosis plus summary. No
explanation is inferred from repair actions. An empty persistent diagnosis
contract remains `DiagnosisPass=None` and makes no judge request.

Case-specific deterministic normalization belongs in `BaseEvaluator._match_exact_diagnosis`.
Shared evidence checks may override `DiagnosisPassFunc` and call `super()` first;
they must preserve the selected semantic matcher.

Results record `matching_mode`, `judge_model`, `judge_usage`, and per-condition
`semantic_judgments`. OP and SP retain their existing independent checks.
Offline tests exercise defaults, paraphrase matching, contradictions, selected
endpoints, request failures, and malformed output. Model accuracy still needs
calibration against representative diagnoses; these tests do not measure it.
