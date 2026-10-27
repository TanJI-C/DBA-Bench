# AGENTS.md

This file provides guidance to AI coding agents working with code in this repository.

## Project Overview

DBA-Bench is a database operations Agent Benchmark framework for evaluating LLM-based agents on PostgreSQL and TiDB distributed fault diagnosis and remediation scenarios.

## Commands

```bash
# Install in editable mode
pip install -e '.[data]'

# Run tests
pytest tests/                    # All tests
pytest tests/test_mock_llm.py    # Single test file

# Run scenarios
python examples/run_mock_llm_demo.py                                # Mock LLM agent, no API needed
python examples/run_pg_query_perf_missing_index_scenario.py --case product_category_substring
python examples/run_tidb_demo.py                                    # TiDB Docker Compose demo
python examples/run_tpcds_demo.py                                   # TPC-DS workload demo
```

## Architecture

DBA-Bench has two task domains and one shared benchmark execution layer. bounded Scenario and
Persistent Scenario each own their model, runtime, evaluation, and system-specific implementation
under their domain package; benchmark planning and execution are shared.

```text
Persistent Scenario domain (src/persistent_scenarios/)
  model       - strict PersistentScenarioSpec/EventSpec/YAML/calibration contracts
  runtime     - persistent run state, monotonic scheduler, sessions, checkpoints, cleanup, trace
  evaluation  - Persistent Scenario diagnosis/SLO/recovery/safety and DP/OP/SP composition
  backend     - PostgreSQL environment/workload/telemetry and explicit Event capabilities

bounded Scenario domain
  src/scenarios/       - ScenarioCase, registry, FaultPlan and PG/TiDB case bundles
  src/scenarios/runtime/   - Scenario orchestrator and lifecycle helpers
  src/scenarios/evaluation/ - Scenario DP/OP/SP evaluator implementation

Benchmark layer (src/benchmark/)
  manifest/planner/runner/store/aggregate/dataset
  adapters/scenario.py and adapters/persistent_scenario.py select domain targets

Shared infrastructure
  src/execution/       - PGEnv/TiDBEnv and deployments
  src/database/        - SQL/catalog/result primitives
  src/agents/          - benchmark subject implementations
  src/visualization/   - trace/dataset readers and server
```

Persistent Scenario control flow:

```text
persistent_scenarios.api -> model loader -> backend admission
  -> deploy one environment -> start workload/telemetry
  -> monotonic Event arrival + fresh alert/inspection sessions
  -> checkpoints -> final evaluation -> reverse capability cleanup -> teardown
```

### Shared Implementation Map

Search with `rg` before adding a parser, matcher, response decoder, safety tuple, or result-comparison helper. Reuse the module that owns the behavior:

- `src/database/sql.py`: environment/SQL result-row validation and execution helpers.
- `src/database/query_results.py`: business-query result snapshots, canonicalization, sampling, and comparison.
- `src/database/postgres.py`: PostgreSQL catalog SQL and index-signature matching.
- `src/scenarios/evaluation/outcome.py`: reusable Scenario OP verifiers and SQL execution helpers.
- `src/scenarios/evaluation/safety.py`: Scenario safety rules, safety contexts, final-state verifiers, and `postgres_statement_tree` (what PostgreSQL's parser says an executed statement does: kind, options, named relations and indexes, calls, settings).
- `src/persistent_scenarios/runtime/trace.py`: Persistent Scenario `persistent_scenario_trace_v1` writer and seal-time artifact output.
- `src/persistent_scenarios/backend/postgres/registry.py`: explicit PostgreSQL Persistent Scenario Event capability registry.
- `src/benchmark/api.py`: public benchmark manifest/planner/runner/store boundary.

Import from the defining module or the documented public API. Do not recreate parsers, result
comparators, safety rules, or project-root calculations in category modules. Persistent Scenario runtime may use
injected backend ports, but must not import concrete PostgreSQL capability modules; benchmark core may
use target adapters, but must not import concrete domain backends directly.

## Agent Tool Interface

Agents interact with both environments through the same core APIs:

- `query_metrics(metric_type, target)` for environment observations such as `cpu`, `memory`, `disk_io`, raw `active_connections` time series, container/filesystem `disk_usage`, `qps`, `cache_hit_ratio`, and `workload_activity`; SQL-backed details such as connection state, lock waits, database/table/WAL/temp sizes, `slow_queries`, `topsql`, and `dead_tuples` are not pre-aggregated into the Agent tool
- `execute_sql(sql_query)` to execute arbitrary SQL for the SQL-backed details above; the Agent chooses filtering, aggregation, and interpretation
- `manage_instance(action, target)` for lifecycle actions such as `restart`, `start`, and `stop`
- `read_log(log_type, ...)` for bounded database and container logs
- `help`, `submit`, and `exit` for protocol control

LLM agents return JSON in this shape:

```json
{"thinking": "...", "action": {"api": "...", "args": {...}}}
```

They may also use native tool calling through OpenAI or Anthropic function-calling formats.

## LLM Configuration

LLM credentials are stored in `config/llm_config.json`, keyed by model name. `LLMAgent` supports both OpenAI-compatible and Anthropic-native APIs, and auto-detects the provider from the URL or explicit `provider` field. Start from `config/llm_config.example.json`; never commit real credentials.

## Deployment Modes

- **PostgreSQL Docker**: Fat image and optional fault snapshot pattern with explicit resource constraints.
- **TiDB Docker Compose**: Per-run PD, TiKV, and TiDB containers with Prometheus and cAdvisor. Topology and aggregate deployment resources come from `TiDBCaseRuntime`.

## Repository Practices

- Use existing patterns in `src/persistent_scenarios`, `src/scenarios`, `src/benchmark`, and `src/execution` before introducing new abstractions.
- Keep scenario implementations aligned with the scenario documents in `docs/`, especially `docs/catalogs/postgresql-scenarios.catalog.md` and `docs/catalogs/tidb-scenarios.catalog.md`.
- `docs/index.md` is the file-level index of `docs/`; scenario contracts live under `docs/scenarios/`, framework standards under `docs/standards/`, and how-to guides under `docs/guides/`.
- `docs/` holds the English documentation; Chinese counterparts live under `docs/zh/` with the same subdirectory layout and a `.zh-CN.md` filename suffix (see `docs/zh/index.md`). When adding or renaming a document in either tree, keep both sides in sync.
- Add or update focused tests when changing scenario behavior, evaluators, parser logic, or environment APIs.
- Prefer `rg` for searching and inspect nearby code before editing.
