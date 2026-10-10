---
doc_id: guide.benchmark.connect-remote-agent
doc_type: guide
status: canonical
audience: [authoring, maintainer, reviewer]
exposure: agent_safe
scope: [shared, postgres, tidb, benchmark]
summary: Run an out-of-process agent on bounded scenarios through the remote agent mode and its HTTP relay protocol.
source_of_truth: code
related: [guide.benchmark.run-experiment, guide.benchmark.run-human-browser-console, standard.evaluation.dp-op-sp]
---

# Connect a remote agent

The `remote` agent mode runs an agent that lives outside the benchmark process — a service
written in any language — on bounded scenarios. The benchmark stays the only path to the
environment: the remote agent proposes one action at a time, and `RemoteAgent`
(`src/agents/remote_agent.py`) executes it through `EnvGateway`. The action history, Outcome
Pass and Safe Pass therefore see exactly the trace they see for the built-in agents.

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
  of `src/scenarios/evaluation/protocol.py`), or `exit`, which fails the run.
- Consecutive actions with the same `turn_id` count as one turn, like the parallel tool calls
  of one LLM response; an action without `turn_id` is a turn of its own. After `max_turns`
  tool turns the next action must be `submit`; a further tool turn fails the run.
- `usage` is an optional list of provider token-usage records for the model calls behind the
  action: `provider`, `model`, `input_tokens` (all prompt tokens, cached included),
  `output_tokens`, and optionally `cached_input_tokens` and `cache_write_input_tokens`. The
  records feed the efficiency metrics and the trace's `llm_usage`.

`submit` and `exit` never reach the environment.

## Run

Start the agent service, then plan and run the experiment as usual
([run-experiment guide](run-experiment.guide.md)):

```bash
aiopsbench experiment plan experiments/my-remote.yaml
aiopsbench experiment run  experiments/my-remote.yaml
```
