---
doc_id: guide.benchmark.connect-remote-agent
doc_type: guide
status: canonical
audience: [authoring, maintainer, reviewer]
exposure: agent_safe
scope: [shared, postgres, tidb, benchmark]
language: en
summary: Run an out-of-process agent on bounded scenarios through the remote agent mode and its HTTP relay protocol.
source_of_truth: code
related: [guide.benchmark.run-experiment, guide.benchmark.run-human-browser-console, standard.evaluation.dp-op-sp]
---

# Connect a remote agent

The `remote` agent mode runs an agent that lives outside the benchmark process, as a service
written in any language, on bounded scenarios. The external service owns model calls and
decision-making. The benchmark is the HTTP client and stays the only path to the environment:
`RemoteAgent` (`src/agents/remote_agent.py`) requests one action, executes it through
`EnvGateway`, sends the result back, then requests the next action. Tool execution is serial,
even when several actions came from the same model response. Evaluation uses the recorded
tool history and the submitted diagnosis.

[中文指南](../../zh/guides/benchmark/connect-remote-agent.guide.zh-CN.md)

An agent that reaches the database or the host through its own connection bypasses that
history: Safe Pass rules and history-based Outcome Pass checks would then judge a trace that
does not contain the agent's actions. Route every observation and change through the tools.

## Manifest

```yaml
agents:
  - id: my-agent          # recorded as the run's agent id
    mode: remote
    model: my-agent-v1    # optional label, defaults to "remote"
    max_turns: 30
    settings:
      endpoint: http://127.0.0.1:9000/agent
```

`settings` must contain exactly `endpoint`, an absolute `http(s)` URL. `remote` supports
bounded scenarios only; `reasoning_effort` and `max_output_tokens` are rejected because the
benchmark does not call a model for this agent.

## Protocol

All bodies are JSON. Paths are relative to `endpoint`.

| Request | Body | Response |
|---|---|---|
| `POST /sessions` | `experiment_id`, `agent_id`, `run_id`, `scenario_id`, `case_id`, `system_prompt`, `user_prompt`, `tools` (function schemas), `tool_help`, `max_turns` | `{"id": "<session id>"}` |
| `GET /sessions/{id}/next` | — | `{"action": {...}}`, or `{"action": null}` when no action is ready within 35 s |
| `POST /sessions/{id}/result` | `action_id`, `result` (the tool's JSON result), `turns_used`, `max_turns` | any JSON object, e.g. `{}`; content is ignored |
| `POST /sessions/{id}/finish` | `evaluation`, `error` | any JSON object, e.g. `{}`; content is ignored |

An action is `{"id", "api", "args", "thinking"?, "turn_id"?, "usage"?}`:

- `api` is a tool name from `tools`, `submit` with `{"report": ...}` (the structured report
  in [protocol.py](../../../src/scenarios/evaluation/protocol.py)), or `exit`, which fails the run.
- `thinking` is optional text recorded with the action.
- `turn_id` is an optional identifier supplied by the service; its accounting rules are below.
- `usage` is an optional list of model token-usage records; its reporting rules are below.

`submit` returns the report for evaluation; `exit` fails without submitting a diagnosis.
Neither reaches the environment or consumes a tool turn, and neither receives a `/result`.

## Turn accounting

`turns_used` counts groups of tool actions. Consecutive actions with the same non-null
`turn_id` count once. An action with a missing or null `turn_id`, or with a different ID,
starts a new turn. For example, IDs `a, a, b` count as two turns; `a, b, a` count as three.
Once `max_turns` is reached, starting another tool turn fails the run; another action with
the current ID still executes. The service should submit its report when its budget is exhausted.

Use the same ID only for actions already selected by one model response. If the agent reads
a tool result and makes a new decision, give the next action a new ID. This is a service
implementation convention: the benchmark does not observe the external model calls and
cannot enforce it. Reusing an ID for new decisions undercounts turns. `max_turns` therefore
does not independently cap actual model calls or the total number of tool actions.

Trace viewer turn numbers are based on recorded actions and need not match `turns_used` or
the number of external model calls. The trace contains tool actions/results, supplied
`thinking`, and reported `llm_usage`; it does not capture the service's full conversation
or internal model requests.

## Usage and cost reporting

The benchmark does not fetch usage from the model provider. The service must attach it to
an action, including `submit` when reporting calls made after the last tool action:

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

Each record requires non-empty `provider` and `model` strings, and non-negative integer
`input_tokens` and `output_tokens`. Input tokens include cached tokens. Optional
`cached_input_tokens` and `cache_write_input_tokens` default to zero. Invalid supplied
records fail the run.

Report each actual model call exactly once. If one response produced several actions,
attach its usage to one action only: records are appended without deduplication. Include
internal planning and summary calls when reporting complete usage. Usage is independent
of `turn_id`; one action may carry records for several calls.

Omitting usage does not prevent execution or DP/OP/SP evaluation. With no records, the
efficiency evaluator marks the agent as unmetered. Missing calls make totals incomplete.
Later token/cost table generation cannot reconstruct missing usage for `RemoteAgent`
from its trace. Current cost accounting prices records using the run's configured model,
rather than selecting prices by each usage record's model. For supported cost analysis,
report all calls, use a single model, and set manifest `model` to the matching entry in
the token-cost configuration. Multiple models are not priced correctly by this path.

## Session completion

Keep the service available after `submit` until it has received and responded to `/finish`.
The benchmark sends this notification after evaluation, cleanup, and trace export; its
`error` field reports a run failure when present. Every HTTP request has a 40-second timeout;
a `/next` long poll should return an action or `{"action": null}` within 35 seconds.
Null responses continue polling; the experiment's run timeout still bounds execution.

Currently a failed `/finish` request propagates as a process failure. Even if evaluation
is already saved in the trace, the formal runner then excludes the run from normal scoring
aggregation. The service must handle `/finish` and return a JSON object such as `{}`.

## Run

Start the agent service, then plan and run the experiment as usual
([run-experiment guide](run-experiment.guide.md)):

```bash
conda run -n aiops aiopsbench experiment plan experiments/my-remote.yaml
conda run -n aiops aiopsbench experiment run experiments/my-remote.yaml
```
