---
doc_id: standard.scenario.taxonomy
doc_type: standard
status: canonical
audience: [authoring, reviewer, maintainer, runtime_agent]
exposure: agent_safe
scope: [shared, scenario, postgres, tidb]
summary: Defines the current database-specific Scenario category boundaries, Agent tool surface, and the separation between catalog navigation and DP/OP/SP evaluation.
source_of_truth: code
related: [catalog.postgresql-scenarios, catalog.tidb-scenarios, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp]
language: en
---

# Scenario Taxonomy and Tool Surface

This document defines the current category boundaries of DBA-Bench Scenarios and the common Agent
tool surface. It explains only how to understand and locate scenarios and does not enumerate
specific Scenarios/Cases; see the
[PostgreSQL Scenario Catalog](../../catalogs/postgresql-scenarios.catalog.md) and the
[TiDB Scenario Catalog](../../catalogs/tidb-scenarios.catalog.md) for the official registry and
Case snapshots.

## 1. Current Categories

Official PostgreSQL Scenarios can only fall into the following five categories:

| Category | Task boundary |
| --- | --- |
| `query_perf` | A known SQL statement or SQL fingerprint has regressed in performance; locate execution, statistics, or storage-path problems |
| `system_failure` | Services, transactions, replication, or storage are already abnormal; identify the primary fault and recover |
| `health_check` | Proactive inspection, capacity, consistency, or pre-change checks; the goal is to discover risks and form a trustworthy conclusion |
| `business_change` | Upgrades, migrations, scaling, backup and restore, disaster-recovery switchover, and planned DDL/DML |
| `resource_governance` | Govern RU, concurrency, storage, topology, and background task budgets under business SLO, security, or compliance constraints |

Compound causal chains and misleading first-screen evidence are Case difficulty and evidence
structure, not top-level task categories. Multi-root-cause tasks are classified into the table
above by their primary operations objective; alert-attribution bias is classified into the
corresponding business category by the real problem. The catalogs of the two databases each record
the current registration distribution; the category enumeration keeps only the five categories
above.

The name itself does not decide the classification: planned recovery belongs to
`business_change`, failover after losing the majority of replicas belongs to `system_failure`,
and recovery throttling under a foreground SLO belongs to `resource_governance`. Do not create
additional categories for a single business topic.

## 2. Agent Tool Surface

The Agent observes and handles Scenarios through the common protocol:

- `query_metrics`: read environment resources, load, and declared metric time series;
- `execute_sql`: query database state, locks, objects, business results, and other SQL-backed
  details as the task requires;
- `manage_instance`: perform explicit instance lifecycle actions;
- `read_log`: read bounded database or container logs;
- `help`, `submit`, `exit`: protocol control and structured submission.

Tool parameters, return envelopes, permissions, and safety boundaries follow the current
environment and code protocol. Documentation must not pass off evaluator-internal observations,
injection evidence, or fixed answers as Agent tool results.

## 3. Evaluation Boundary

DP, OP, and SP are three independent decision surfaces; see the
[DP, OP, and SP Standard](../evaluation/dp-op-sp.standard.md) for definitions and implementation:

- DP judges only whether the final structured diagnosis expresses the root cause; no-root-cause
  tasks use `DiagnosisPass=None`;
- OP judges from the final environment, business ground truth, or trusted artifacts whether the
  task is complete, and accepts safe and materially equivalent remediations;
- SP independently judges whether the action process caused real safety problems; efficiency,
  action counts, and MTTR are descriptive evidence only;
- failures of valid runs go to an independent trace-level judge that classifies them by the
  semantics of the diagnosis, remediation path, and evidence; failure types are not mechanically
  inferred from specific DP/OP/SP values or combinations.

Difficulty is not an evaluation weight. `D_s`, `C_s`, reference runs, `m/n` counts, and the
`Easy`/`Hard` labels are defined uniformly in the
[Scenario Difficulty Standard](difficulty.standard.md).

## 4. Reading Order

Read the corresponding database catalog first, then the current Scenario/Case contracts and code.
The catalog is navigation and a snapshot of the current registry; it does not replace the specific
contracts.
