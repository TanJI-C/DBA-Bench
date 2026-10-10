# Baseline evolution overview and automatic evolution usage

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-plan-management.md`
- Source Title: `SQL Plan Management (SPM)`
- Source Heading Path: `SQL Plan Management (SPM) > Baseline evolution | SQL Plan Management (SPM) > Baseline evolution > Usage`
- Source Line Ranges: `743-817`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `sql-plan-management`, `baseline-evolution`, `bindings`, `optimizer`, `execution-plan`, `experimental-feature`, `configuration`, `verification-window`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0167_44b61abdc3`
- Source ID: `tidb-docs-8.1:sql-plan-management.md#baseline-evolution`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d856b0fc62b76ddac4518fdb436fcaa1f36c34d9f0c947a83957973fa5d6c01a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-plan-management#baseline-evolution
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-plan-management.md

## Retrieval Guidance

- Use When: Use this chunk when you need the overview of baseline evolution, the tidb_evolve_plan_baselines setting, verification behavior for candidate plans, or the evolution time-window configuration.
- Retrieval Keywords: Baseline evolution, tidb_evolve_plan_baselines, SET GLOBAL tidb_evolve_plan_baselines = ON, experimental feature, bind-info-lease, waiting for verification, usable binding, 2/3, CREATE GLOBAL BINDING, use index(a), index b, tidb_evolve_plan_task_max_time, tidb_evolve_plan_task_start_time, tidb_evolve_plan_task_end_time
- Follow-up Guidance: The content also provides an example with CREATE GLOBAL BINDING and explains that candidate plans are verified against the current binding by actual execution time.
- Classification Note: This is classified as performance because it covers automatic evolution of bound execution plans so the optimizer can adopt a faster verified plan as data and statistics change.

## Official Source Content

## Baseline evolution

Baseline evolution is an important feature of SPM introduced in TiDB v4.0.

As data updates, the previously bound execution plan might no longer be optimal. The baseline evolution feature can automatically optimize the bound execution plan.

In addition, baseline evolution, to a certain extent, can also avoid the jitter brought to the execution plan caused by the change of statistical information.
### Usage

Use the following statement to enable automatic binding evolution:

```sql
SET GLOBAL tidb_evolve_plan_baselines = ON;
```

The default value of `tidb_evolve_plan_baselines` is `off`.

> **Warning:**
>
> + Baseline evolution is an experimental feature. Unknown risks might exist. It is **NOT** recommended that you use it in the production environment.
> + This variable is forcibly set to `off` until the baseline evolution feature becomes generally available (GA). If you try to enable this feature, an error is returned. If you have already used this feature in a production environment, disable it as soon as possible. If you find that the binding status is not as expected, [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.

> **Warning:**
>
> + Baseline evolution is an experimental feature. Unknown risks might exist. It is **NOT** recommended that you use it in the production environment.
> + This variable is forcibly set to `off` until the baseline evolution feature becomes generally available (GA). If you try to enable this feature, an error is returned. If you have already used this feature in a production environment, disable it as soon as possible. If you find that the binding status is not as expected, [contact TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).

After the automatic binding evolution feature is enabled, if the optimal execution plan selected by the optimizer is not among the binding execution plans, the optimizer marks the plan as an execution plan that waits for verification. At every `bind-info-lease` (the default value is `3s`) interval, an execution plan to be verified is selected and compared with the binding execution plan that has the least cost in terms of the actual execution time. If the plan to be verified has shorter execution time (the current criterion for the comparison is that the execution time of the plan to be verified is no longer than 2/3 that of the binding execution plan), this plan is marked as a usable binding. The following example describes the process above.

Assume that table `t` is defined as follows:

```sql
CREATE TABLE t(a INT, b INT, KEY(a), KEY(b));
```

Perform the following query on table `t`:

```sql
SELECT * FROM t WHERE a < 100 AND b < 100;
```

In the table defined above, few rows meet the `a < 100` condition. But for some reason, the optimizer mistakenly selects the full table scan instead of the optimal execution plan that uses index `a`. You can first use the following statement to create a binding:

```sql
CREATE GLOBAL BINDING for SELECT * FROM t WHERE a < 100 AND b < 100 USING SELECT * FROM t use index(a) WHERE a < 100 AND b < 100;
```

When the query above is executed again, the optimizer selects index `a` (influenced by the binding created above) to reduce the query time.

Assuming that as insertions and deletions are performed on table `t`, an increasing number of rows meet the `a < 100` condition and a decreasing number of rows meet the `b < 100` condition. At this time, using index `a` under the binding might no longer be the optimal plan.

The binding evolution can address this kind of issues. When the optimizer recognizes data change in a table, it generates an execution plan for the query that uses index `b`. However, because the binding of the current plan exists, this query plan is not adopted and executed. Instead, this plan is stored in the backend evolution list. During the evolution process, if this plan is verified to have an obviously shorter execution time than that of the current execution plan that uses index `a`, index `b` is added into the available binding list. After this, when the query is executed again, the optimizer first generates the execution plan that uses index `b` and makes sure that this plan is in the binding list. Then the optimizer adopts and executes this plan to reduce the query time after data changes.

To reduce the impact that the automatic evolution has on clusters, use the following configurations:

- Set `tidb_evolve_plan_task_max_time` to limit the maximum execution time of each execution plan. The default value is `600s`. In the actual verification process, the maximum execution time is also limited to no more than twice the time of the verified execution plan.
- Set `tidb_evolve_plan_task_start_time` (`00:00 +0000` by default) and `tidb_evolve_plan_task_end_time` (`23:59 +0000` by default) to limit the time window.
