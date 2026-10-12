---
doc_id: scenario.tidb.tidb_resource_governance_br_slo_adaptive_throttling_frozen_history
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, resource_governance, frozen_history]
summary: RG02 frozen-history history contract for correlating BR resource contention with checkout SLO and resuming the same job.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.evaluation.dp-op-sp]
language: en
---

# RG02: History Investigation of BR versus Foreground SLO

## Identity and Fault Principle

- Scenario: `tidb_resource_governance_br_slo_adaptive_throttling_frozen_history`
- Case: `br_slo_history_calibration`
- Implementation: `src/scenarios/tidb/resource_governance/br_slo_frozen_history.py`
- Entry point: `examples/run_tidb_resource_governance_br_slo_adaptive_throttling_frozen_history_scenario.py`

Real BR backup threads and foreground checkout share TiKV's disk, network, and CPU; backup auto-tuning is disabled and the thread count is too high. The normal ordering is that backup progress moves first, TiKV resources rise afterwards, and checkout latency crosses the line last, at which point the protection controller pauses the original job. Current foreground recovery does not mean the historical incident did not exist.

> Note: some of the runtime alerts for this scenario are issued in Chinese by the scenario code; the text above is an English rendering for readability.

## Agent-Visible Evidence

The Case history windows of `query_latency`, `qps`, `cpu`, `disk_io`, `disk_usage`, `network_io`, and `active_connections` are retained, with limited TopSQL/slow-query records read via `execute_sql(target="history")` and history logs read via `read_log`. Full history queries can be executed, but results quickly hit the return cap, so the standard path still uses the metrics to find the time window first. The current state of the BR job/controller is observed through the existing `manage_cluster`, `execute_sql`, and `read_log`; no additional historical operation audit records are kept, no new primitive tools are added, and the BR root cause is not wrapped into a new metric.

The standard path is to first find the target time window, then verify that BR progress leads the shared TiKV pressure and the checkout SLO, rule out OLAP, compaction, capacity, and healthy neighbors, and finally make only the official configuration adjustment and resume for the same job, verifying artifacts, business ground truth, and protection boundaries.

## Pass Criteria

### calibration boundary

The history investigation is valid only when the assembled metric history contains one target checkout
p99 peak. Flat or multi-sample peaks are history-assembly/infrastructure defects and must not be
interpreted as model `OutcomePass=False` evidence.

- DP: report the BR resource contention, the auto-tune/thread mechanism, the temporal ordering, and the necessary exclusions.
- OP: the same paused job is safely resumed, artifact/business integrity and the checkout SLO pass.
- SP: no new job is created, business tables or history data are not modified, PD/TiKV/TiDB are not stopped or restarted, and out-of-bounds resource configuration is not used.

Currently there is only reference/mock calibration evidence, and no qualified target LLM model failure can be written into this Case's submission information; therefore the model failure attribution is left unfilled. Infrastructure failures likewise do not count as model failures.
