---
doc_id: guide.benchmark.run-human-browser-console
doc_type: guide
status: canonical
audience: [maintainer, reviewer]
exposure: internal
scope: [shared, postgres, tidb, benchmark]
summary: Run existing bounded cases with the browser tool workbench: operate tools, view results, plot data, and submit structured answers.
source_of_truth: code
related: [standard.scenario.architecture, standard.evaluation.dp-op-sp]
language: en
---

# Human Browser Workbench

Start the unified visualization service from the repository root:

```bash
conda run -n aiops python scripts/serve_visualization.py
```

Open `http://127.0.0.1:9235/human`. Remote hosts can use SSH forwarding:

```bash
ssh -N -L 9235:127.0.0.1:9235 <user>@<host>
```

The workbench shares the same service as the Trace Viewer, experiment runs, and experiment results. If the service was started before this feature was added, stop the old process first, then start it again from the branch containing this feature. The page is intended for trusted local/SSH use; the participant ID records identity and is not login authentication.

## Start answering

Select the database, scenario, and case, then enter a participant ID to start. The PG CPU set is left empty by default: the server reuses the benchmark resource allocator to automatically select the CPU and NUMA memory nodes according to the case's resource requirements and the machine topology, writes the allocation into the manifest, and starts the runner with the same CPU set. Insufficient resources produce an explicit error.

Run settings allow changing the database port and manually specifying the PG CPU set. When an administrator needs to pin resources, they can fill in a complete physical core set (including SMT threads); for example, `8-11,32-35` only applies to this host's topology at the time of verification. Neither automatic allocation nor manual binding constitutes an exclusive reservation; formal experiments on shared hosts still require the administrator to check other workloads.

Clicking "Prepare environment and start" generates an independent experiment manifest, first executes a runner dry-run, and then serially runs the single selected case. Once preparation completes, the case, constraints, and tools are displayed automatically. Preparation failures display the error. The "Start a case" area can terminate a run that is preparing or executing; the runner is responsible for cleanup.

The catalog comes from the formal Scenario registry and includes all bounded cases that currently have a formal entry point. Newly registered cases appear automatically. Persistent Scenarios are outside the scope of this entry point. Only one case is started at a time; multiple browsers can view the same session, and the server accepts only one pending action to avoid duplicate concurrent modifications to the database.

## Tool operations

The tool list shares the environment's enabled tool schema with the LLM Agent. A regular TiDB case provides 8 tools by default: `query_metrics`, `execute_sql`, `manage_cluster`, `read_log`, `search_knowledge`, `help`, `submit`, `exit`. HC04 backup-recovery cases additionally provide 4 archive-inspection, remediation, and isolated-recovery tools only after the recovery runtime is registered; these are revoked during cleanup. The PG tool surface continues to follow the selected `TOOL_PROFILES`, and the two knowledge base implementations share the `query_knowledge_base` alias externally.

- `execute_sql`: a multi-line SQL editor, executed with Ctrl/⌘ + Enter. Keeps the SQL, target, notes, elapsed time, and raw results. Tables support filtering, sorting, and CSV export; NULL is displayed separately, and truncated results are clearly indicated.
- `query_metrics`: the metric dropdown comes from the current case's actual schema. Supports target, UTC start/end times, step, and point-count parameters; the returned window and the full raw data can be inspected. Time-series results automatically expand a chart.
- `manage_instance`: a PG action dropdown plus target and configuration value forms. Instance stop, restart, configuration changes, and similar operations are confirmed before execution.
- `manage_cluster`: linked selection of TiDB resources and operations, with target requirements, operation parameters, and constraints changing with the selection. Use "Discover available targets" to run the discovery tool declared by the operation contract, then fill in the returned stable instance identifier.
- `read_log`: reads by the log type/component targets provided per database, line ranges, keywords, and UTC time windows. Results can be filtered again by log line; truncation and pagination information can be inspected.
- `query_knowledge_base` / `search_knowledge`: forms for question text and retrieval scope; allowed values, result counts, and length limits follow the actual tool schema.
- `help`: the tool list with full parameter descriptions; resources, operations, and metric definitions for complex tools are shown in tables and expandable sections.
- `submit`: adds diagnosis conditions through a structured form, with one piece of evidence, one change, or one verification per line; a JSON plan can be provided where the case requires one. The server validates using the project's `StructuredReport`, and an invalid report can be corrected and resubmitted. After a successful submission, tool operations stop and the DP/OP/SP evaluation results are displayed.
- `exit`: ends the answer session and cleans up; this run is recorded as failed/interrupted and is never disguised as a completed evaluation.
- Other case-specific tools (including backup inspection, archive remediation, and isolated recovery) generate parameter forms from the actual schema; the frontend does not need to register new tool names.

All tool results keep the original return value. Database errors returned by tools are shown in the corresponding operation record, and parameters can be corrected to continue; infrastructure exceptions end the run and display a failure.

## Generic plotting

Click "Plot time series / data chart" in a result, then select the data table, the X column, the numeric Y column, and the group column. The X axis can use UTC time or numeric values. Metric `series.<target>.timestamps` arrays, long-history compressed grids `{start,end,step_seconds,count}`, SQL `columns/result` tables, arrays of object rows, and arrays of binary time-series points can all be read.

Charts support legend toggling, wheel zooming, drag panning, hover sample values, and zoom reset. Missing values are shown as gaps; an empty state is shown when there is no plottable data. Plotting works whenever SQL returns any time column and numeric column — no dedicated SQL API is needed. When comparing different dimensions, select the corresponding data/metrics separately to avoid misreading numeric magnitudes as if they shared a unit.

## Lifecycle and artifacts

`BrowserHumanAgent` receives browser actions via HTTP long polling, while actual tool access still goes through `BaseAgent.execute → EnvGateway → Environment`. The case, system prompt, tool schemas, and public tool help are injected by the existing orchestrator; the console never reads the reference report, fault ground truth, or evaluator internal state as answering hints.

Submissions are consumed by the Agent; the orchestrator then completes evaluation, fault recovery, environment teardown, and trace export, and finally notifies the console. The runner continues to record experiment status, resources, and cleanup evidence.

- Temporary manifest: `experiments/tmp/human-<id>.yaml`.
- Experiment ground truth: `artifacts/experiments/human-<id>/runs/<run_id>/attempts/<NNN>/{trace,evaluator,attempt}.json`.
- Browser sessions and notes: `artifacts/human-console/sessions/<session_id>.json`.
- Startup/preparation log: `artifacts/human-console/human-<id>.log`.

Refreshing the browser restores the session, operation history, and saved tool-parameter drafts. A service restart does not restore the active Agent channel, and old sessions explicitly show as failed; the old run must be interrupted and cleaned up from the runner before starting a new case. Completed sessions can be viewed and exported but cannot continue executing tools.

You can also write the runner manifest directly; the Agent configuration is as follows:

```yaml
agents:
  - id: participant-001
    mode: human
    max_turns: 1000
    settings:
      console_url: http://127.0.0.1:9235
      participant: participant-001
```

The remaining benchmark, `exclude_cells`, and runtime configuration follows the standard experiment manifest. Human mode requires no model or LLM credentials; the Agent factory selects the real human Agent in place of the existing entry point's `llm` execution branch. Long-polling wait time counts as participant answering time; the human Agent does not auto-submit based on LLM conversation turns, and the overall experiment timeout bounds the run.

## Browser acceptance reproduction

The browser acceptance script uses Playwright to actually fill in the workbench, execute tools, refresh the page, submit the report, and check the evaluation results. It uses the existing mock/reference fixtures as operation inputs; it is UI acceptance, not a human-subject experiment. Before running it, validate the corresponding case's mock smoke per the project experiment process, and make sure no other case occupies the selected ports.

```bash
conda run -n aiops python scripts/check_human_console_browser.py --system postgresql
conda run -n aiops python scripts/check_human_console_browser.py --system tidb
```

Without `--cpuset-cpus`, browser acceptance keeps run settings disabled, covering the default startup path with an empty CPU set; passing it covers the manually specified path. After acceptance completes, the following script can check the results-area controls at the actual access address, including copy-paste over HTTP, JSON/CSV downloads, filtering and sorting, parameter reuse, charts, and session export:

```bash
conda run -n aiops python scripts/check_human_console_results_browser.py --url http://<host>:9235
```

The tests above cover the specified cases and the operations listed in the scripts; they do not constitute exhaustive coverage of every tool's parameter combinations or every management action that could change the environment.

For tool-surface regression, run `conda run -n aiops python scripts/check_human_console_tools_browser.py`. Using a temporary HTTP service and a real browser, it checks the three TiDB tool surfaces (regular / HC04 active / post-cleanup), the four PG profiles, and backend rejection of tools that are not provided; it uses the real environment schema but does not deploy databases and does not constitute full case acceptance. Results are written to `artifacts/human-console/tool-scope/browser-check.json`.

The test environment needs Playwright and Chromium. The scripts save screenshots and `*-acceptance.json` files under `artifacts/human-console/`; actual benchmark artifacts are still saved by the runner. The scripts verify SQL tables, logs, tool help, PG configuration queries, TiDB resource discovery, metric charts, plotting from arbitrary SQL time tables, refresh recovery, and structured submission.
