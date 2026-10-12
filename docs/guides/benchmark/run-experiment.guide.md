---
doc_id: guide.benchmark.run-experiment
doc_type: guide
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: agent_safe
scope: [shared, benchmark, postgres, tidb]
summary: Defines the reproducible manifest, planning, execution, resume, rerun, aggregation, and evidence workflow for benchmark experiments.
source_of_truth: code
related: [standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case, guide.persistent-scenario.implement-persistent-scenario]
language: en
---

# DBA-Bench Formal Experiment Workflow

Formal experiments are defined by a manifest, and run artifacts are written to `artifacts/experiments/<experiment_id>/`. Bounded Scenarios expand along `scenario × case × agent × repetition`, and Persistent Scenarios expand along `scenario × agent × repetition`; both associate traces, evaluators, stdout, and aggregated results through a stable `run_id`.

## 1. Create the experiment manifest

Start from `experiments/pg_smoke.example.yaml`. A bounded Scenario must specify at minimum:

- `experiment_id`;
- systems, categories, and scenarios;
- agent IDs, mode, model, and `max_turns`;
- repetitions with one-to-one corresponding seeds;
- concurrency, timeout, ports, container prefixes, and the fault snapshot policy.

The manifest only accepts fields defined in the documentation and errors directly on unknown fields. To skip cells that are already completed or explicitly not to be run from the full matrix, use the top-level `exclude_cells` to precisely specify scenario, case, and agent:

```yaml
exclude_cells:
  - scenario: pg_health_check_table_bloat
    case: store_returns_table_index_bloat
    agent: agent-a
```

Each exclusion must match a bounded Scenario cell in the plan, otherwise the planner errors. Persistent Scenarios do not support `exclude_cells`.

`runtime.concurrency` is the cap on runs executing simultaneously across the whole experiment. A bounded Scenario first expands the full `scenario × case × agent × repetition` matrix and then schedules by scenario; Persistent Scenarios require `runtime.concurrency=1`, because the environment and persistent session of the same Persistent Scenario cannot be replicated in parallel.

Parallel experiments must configure `runtime.isolation`, and every selected Case must declare `resources`. The runner computes each worker's CPU and memory requirements from the generic resource contract and allocates cpusets by full physical cores and NUMA node. PostgreSQL scenarios marked host-exclusive take over the entire host machine even when they appear in a parallel manifest; TiDB QP scenarios reuse PD/TiKV data via image groups and still enter isolated scheduling as an independent Compose project, network, ports, and container group. For the full configuration see `experiments/pg_system_failure_parallel.example.yaml`.

An existing `experiment_id` cannot be swapped to a different manifest. Create a new ID when the experiment configuration changes.

## 2. Preview the run matrix

```bash
conda run -n aiops aiopsbench experiment plan experiments/pg_smoke.example.yaml
```

## 3. Launch and resume

```bash
conda run -n aiops aiopsbench experiment run experiments/pg_smoke.example.yaml
conda run -n aiops aiopsbench experiment resume <experiment_id>
conda run -n aiops aiopsbench experiment resume <experiment_id> --run-id <run_id>
conda run -n aiops aiopsbench experiment rerun <experiment_id> \
  --status failed --status timed_out
conda run -n aiops aiopsbench experiment rerun <experiment_id> \
  --status succeeded --run-id <run_id>
```

`resume` only executes `pending` runs. `rerun` must be given the original terminal status explicitly and does not retry automatically; each rerun increments the attempt and permanently preserves prior artifacts. Formal execution requires a clean Git worktree; resume and rerun additionally require the current checkout to match exactly the Git commit recorded by the first run. When code, prompts, scenarios, resources, models, the knowledge base, or evaluators change, a new `experiment_id` must be created. On receiving SIGINT/SIGTERM, the runner terminates running child processes and records `interrupted`.

## 4. Artifacts

```text
artifacts/experiments/<experiment_id>/
├── manifest.yaml
├── environment.json
├── runs.jsonl
├── failures.jsonl
├── aggregate.json
├── aggregate.csv
└── runs/<run_id>/
    ├── run.json
    └── attempts/
        ├── 001/
        │   ├── attempt.json
        │   ├── trace.json
        │   ├── evaluator.json
        │   └── stdout.log
        └── 002/
            └── ...
```

Each attempt directory is immutable once written; `attempt.json` is the complete state snapshot of that execution. Bounded Scenarios use `trace.json` / `evaluator.json`, and Persistent Scenarios use
`persistent_scenario_trace.json` / `persistent_scenario_evaluation.json`. `run.json` only reflects the logical run's current state and attempt index. `run.json` distinguishes the execution status,
`DiagnosisPass`, `OutcomePass`, `SafePass`, and `valid_for_aggregate`; for infrastructure failures the three Pass fields stay empty and are not counted in the pass rate.
`environment.json` pins the Git commit/diff hash, manifest/config hash, Python dependencies, Docker version, host platform, and worker assignment. Each run records the actual cpuset, NUMA node, worker capacity, and container quotas.

Aggregated results are refreshed at the end of each batch of runs and can also be rebuilt independently:

```bash
conda run -n aiops python scripts/aggregate_experiment.py <experiment_id>
```

Multiple experiments executed in a split fashion can be merged into a new read-only result set. The source experiments must exist, contain run records, and have no duplicate logical cells; the output directory must not already exist:

```bash
conda run -n aiops python scripts/aggregate_experiment.py \
  <experiment_id_1> <experiment_id_2> \
  --output-experiment-id <combined_experiment_id>
```

## 5. Create and freeze a Dataset

A Dataset explicitly selects the original `experiment_id + run_id` used by each logical cell and assigns a stable `baseline_id` for agents whose names are inconsistent across batches. The unified compose entry combines by system, category, and baseline from the original `run.json`:

```bash
conda run -n aiops aiopsbench dataset compose <dataset_id> \
  --system postgresql \
  --category query_perf \
  --baseline <baseline-id> \
  --metric-contract <metric_contract_version> \
  --data-status provisional

conda run -n aiops aiopsbench dataset status <dataset_id>
conda run -n aiops aiopsbench dataset freeze <dataset_id>
```

`compose` only reads bounded Scenario `artifacts/experiments/*/runs/*/run.json`, selects the latest terminal-status run by `system + scenario + case + baseline`, and requires the matrix of selected systems, categories, and baselines to be complete. `--system`, `--category`, and `--baseline` can be repeated to compose a multi-system Dataset. The generated YAML is an explicit, Git-diffable selection list and does not read dashboards or audit reports. Other selection strategies can first produce a JSON array and then use the generic entry:

```bash
conda run -n aiops aiopsbench dataset create <dataset_id> \
  --runs-json <selected_runs.json> \
  --metric-contract <metric_contract_version> \
  --data-status provisional
```

Each JSON element must contain exactly `experiment_id`, `run_id`, and `baseline_id`. An unfrozen dataset is live. `freeze` requires all selected runs to have reached a terminal status,
and pins each logical cell to an explicit `run_id + attempt`, while recording the SHA-256 of `attempt.json`, the trace, the evaluator output, and stdout. The generated `datasets/<dataset_id>.lock.json` cannot be overwritten. After re-running or replacing runs, create a new `dataset_id` and use the following command to view the difference:

```bash
conda run -n aiops aiopsbench dataset diff <old_dataset_id> <new_dataset_id>
```

## 6. Build plotting data and paper figures

```bash
conda run -n aiops aiopsbench pipeline build <dataset_id>
conda run -n aiops aiopsbench pipeline verify <dataset_id>
```

`pipeline build` only accepts a frozen dataset and generates, in order:

```text
artifacts/datasets/<dataset_id>/
├── runs.jsonl
├── runs.csv
├── aggregate.json
├── scenario_agent_summary.csv
└── provenance.json

paper/figures/output/datasets/<dataset_id>/
├── category_small_multiples.<data_status>.{pdf,png}
├── cost_pareto.<data_status>.{pdf,png}
├── diagnostic_depth.<data_status>.{pdf,png}
├── environmental_complexity.<data_status>.{pdf,png}
└── multimodal_temporal.<data_status>.{pdf,png}
```

Each row of `runs.csv` corresponds to one explicitly selected `run_id + attempt` in the lock and includes:

- provenance fields such as dataset/lock, scenario annotations, and trace/evaluator hashes;
- category, difficulty, diagnostic depth, environmental complexity, evidence modality, and
  temporal requirement;
- execution status, validity, Diagnosis/Outcome/Safe Pass, evaluator identity, and the full evaluation;
- turn/tool behavior counts, input/output tokens as reported by the provider or reconstructed from the trace, and the USD cost when verifiable.

Invalid or infrastructure-failed rows remain in the CSV, but their three Pass fields are empty and are not treated as zero scores. Cost accounting uses the frozen prices identified by `pricing_version` in `data/model_token_costs.yaml`; each entry declares, by model name, the tokenizer backend, `cache_key`, and match status (`encoding_proxy` / `family_proxy` /
`exact_open_model`), with all unit prices in USD / 1M tokens. Costs in `runs.csv` are estimates computed from the frozen official list prices and trace reconstruction, not provider bills; `pricing_version`,
`token_accounting_method`, and `tokenizer_match` must all be retained. Any missing
category, missing DP/OP/SP, hash mismatch, unknown model, incorrect CSV semantics, or stale provenance errors out directly.
The five plotting scripts read only `runs.csv`; `views/*.csv`, dashboard HTML, and audit Markdown are not formal
inputs, and `build_experiment_results.py`, which previously parsed them, has been removed.

## 7. Manage large data with DVC

Code, manifests, dataset definitions, and locks go into Git; raw experiment artifacts and dataset
derived directories go into DVC:

```bash
conda run -n aiops aiopsbench dataset track <dataset_id>
git add datasets/ artifacts/**/*.dvc .dvc .dvcignore
git commit -m "data: freeze <dataset_id>"
```

The repository has DVC initialized but no preset remote. Once the NAS, MinIO, or S3 location is decided, configure it only once:

```bash
conda run -n aiops dvc remote add -d storage <remote-url>
conda run -n aiops dvc push
```

## 8. Browser exploration

Start the unified visualization service:

```bash
conda run -n aiops python -m src.visualization.server
```

- `/`: Trace Viewer;
- `/raw-traces`: search, filter, and view the raw JSON in `logs/traces`;
- `/experiments`: search runs by experiment, scenario, Agent, and status;
- `/datasets`: view the baseline × scenario_case run matrix and aggregate tables per dataset;
- `/dashboard`: the project work dashboard.

The raw log page supports server-side pagination, filtering by date/scenario/Agent/score, in-file search, toggling between formatted and raw views, copying, downloading, and jumping to the Trace Viewer. On the dataset status page, double-clicking a matrix cell shows the `run.json` snapshot explicitly selected by the frozen or live dataset and the evaluator for the corresponding attempt; the aggregate wide table supports horizontal scrolling and custom frozen columns.
