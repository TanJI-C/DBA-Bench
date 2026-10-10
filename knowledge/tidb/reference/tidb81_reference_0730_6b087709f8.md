# Optimizer system variables for aggregation, joins, CTEs, and fix controls

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_opt_distinct_agg_push_down | System Variables > Variable reference > tidb_opt_enable_correlation_adjustment | System Variables > Variable reference > tidb_opt_enable_hash_join <span class="version-mark">New in v6.5.6, v7.1.2, and v7.4.0</span> | System Variables > Variable reference > tidb_opt_enable_non_eval_scalar_subquery <span class="version-mark">New in v7.3.0</span> | System Variables > Variable reference > tidb_opt_enable_late_materialization <span class="version-mark">New in v7.0.0</span> | System Variables > Variable reference > tidb_opt_enable_mpp_shared_cte_execution <span class="version-mark">New in v7.2.0</span> | System Variables > Variable reference > tidb_opt_enable_fuzzy_binding <span class="version-mark">New in v7.6.0</span> | System Variables > Variable reference > tidb_opt_fix_control <span class="version-mark">New in v6.5.3 and v7.1.0</span> | System Variables > Variable reference > tidb_opt_force_inline_cte <span class="version-mark">New in v6.3.0</span> | System Variables > Variable reference > tidb_opt_advanced_join_hint <span class="version-mark">New in v7.0.0</span>`
- Source Line Ranges: `4044-4190`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`, `tiflash`
- Topic Tags: `system-variables`, `optimizer`, `aggregation-pushdown`, `hash-join`, `scalar-subquery`, `late-materialization`, `mpp`, `cte`, `plan-binding`, `optimizer-fix-controls`, `join-hints`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0730_6b087709f8`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-opt-distinct-agg-push-down`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `46a879a6daa0c354ada50781795fbca4c6297f2ffb103e03e3e496e0685ef8a5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-opt-distinct-agg-push-down
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB optimizer system variables for distinct aggregation pushdown, correlation row-count estimation, hash join selection, EXPLAIN scalar subquery expansion, TiFlash late materialization, MPP shared CTE execution, cross-database binding, optimizer fix controls, CTE inlining, or advanced join hint behavior.
- Retrieval Keywords: tidb_opt_distinct_agg_push_down, count(distinct a), Coprocessor, cop[tikv], tidb_opt_enable_correlation_adjustment, column order correlation, tidb_opt_enable_hash_join, HASH_JOIN hint, hash joins, tidb_opt_enable_non_eval_scalar_subquery, EXPLAIN, disable subquery expansion, constant subqueries, tidb_opt_enable_late_materialization, TiFlash late materialization, fast scan mode, TableScan, tidb_opt_enable_mpp_shared_cte_execution, Common Table Expressions, CTE, TiFlash MPP, non-recursive CTE, tidb_opt_enable_fuzzy_binding, Cross-database binding, tidb_opt_fix_control, Optimizer Fix Controls, tidb_opt_force_inline_cte, MERGE() hint, recursive CTE, tidb_opt_advanced_join_hint, MERGE_JOIN() hint, LEADING() hint, Join Reorder
- Follow-up Guidance: The source points to related documentation for Disable subquery expansion, TiFlash late materialization, fast scan mode, Cross-database binding, and Optimizer Fix Controls.
- Classification Note: This is reference content because it enumerates optimizer-related system variables with scope, persistence, hint applicability, type, default value, and behavior details.

## Official Source Content

### tidb_opt_distinct_agg_push_down

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- This variable is used to set whether the optimizer executes the optimization operation of pushing down the aggregate function with `distinct` (such as `select count(distinct a) from t`) to Coprocessor.
- When the aggregate function with the `distinct` operation is slow in the query, you can set the variable value to `1`.

In the following example, before `tidb_opt_distinct_agg_push_down` is enabled, TiDB needs to read all data from TiKV and execute `distinct` on the TiDB side. After `tidb_opt_distinct_agg_push_down` is enabled, `distinct a` is pushed down to Coprocessor, and a `group by` column `test.t.a` is added to `HashAgg_5`.

```sql
mysql> desc select count(distinct a) from test.t;
+-------------------------+----------+-----------+---------------+------------------------------------------+
| id                      | estRows  | task      | access object | operator info                            |
+-------------------------+----------+-----------+---------------+------------------------------------------+
| StreamAgg_6             | 1.00     | root      |               | funcs:count(distinct test.t.a)->Column#4 |
| └─TableReader_10        | 10000.00 | root      |               | data:TableFullScan_9                     |
|   └─TableFullScan_9     | 10000.00 | cop[tikv] | table:t       | keep order:false, stats:pseudo           |
+-------------------------+----------+-----------+---------------+------------------------------------------+
3 rows in set (0.01 sec)

mysql> set session tidb_opt_distinct_agg_push_down = 1;
Query OK, 0 rows affected (0.00 sec)

mysql> desc select count(distinct a) from test.t;
+---------------------------+----------+-----------+---------------+------------------------------------------+
| id                        | estRows  | task      | access object | operator info                            |
+---------------------------+----------+-----------+---------------+------------------------------------------+
| HashAgg_8                 | 1.00     | root      |               | funcs:count(distinct test.t.a)->Column#3 |
| └─TableReader_9           | 1.00     | root      |               | data:HashAgg_5                           |
|   └─HashAgg_5             | 1.00     | cop[tikv] |               | group by:test.t.a,                       |
|     └─TableFullScan_7     | 10000.00 | cop[tikv] | table:t       | keep order:false, stats:pseudo           |
+---------------------------+----------+-----------+---------------+------------------------------------------+
4 rows in set (0.00 sec)
```
### tidb_opt_enable_correlation_adjustment

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `ON`
- This variable is used to control whether the optimizer estimates the number of rows based on column order correlation
### tidb_opt_enable_hash_join New in v6.5.6, v7.1.2, and v7.4.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is used to control whether the optimizer selects hash joins for tables. The value is `ON` by default. If it is set to `OFF`, the optimizer avoids selecting hash joins when generating execution plans, unless no other join algorithm is available.
- If both the system variable `tidb_opt_enable_hash_join` and the `HASH_JOIN` hint are configured, the `HASH_JOIN` hint takes precedence. Even if `tidb_opt_enable_hash_join` is set to `OFF`, when you specify a `HASH_JOIN` hint in a query, the TiDB optimizer still enforces a hash join plan.
### tidb_opt_enable_non_eval_scalar_subquery New in v7.3.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to control whether the `EXPLAIN` statement disables the execution of constant subqueries that can be expanded at the optimization stage. When this variable is set to `OFF`, the `EXPLAIN` statement expands the subquery in advance at the optimization stage. When this variable is set to `ON`, the `EXPLAIN` statement does not expand the subquery at the optimization stage. For more information, see [Disable subquery expansion](https://docs.pingcap.com/tidb/stable/explain-walkthrough#disable-the-early-execution-of-subqueries).
### tidb_opt_enable_late_materialization New in v7.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `ON`
- This variable is used to control whether to enable the [TiFlash late materialization](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-late-materialization) feature. Note that TiFlash late materialization does not take effect in the [fast scan mode](https://docs.pingcap.com/tidb/stable/tiflash/use-fastscan).
- When this variable is set to `OFF` to disable the TiFlash late materialization feature, to process a `SELECT` statement with filter conditions (`WHERE` clause), TiFlash scans all the data of the required columns before filtering. When this variable is set to `ON` to enable the TiFlash late materialization feature, TiFlash can first scan the column data related to the filter conditions that are pushed down to the TableScan operator, filter the rows that meet the conditions, and then scan the data of other columns of these rows for further calculations, thereby reducing IO scans and computations of data processing.
### tidb_opt_enable_mpp_shared_cte_execution New in v7.2.0

> **Warning:**
>
> The feature controlled by this variable is experimental. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- This variable controls whether the non-recursive [Common Table Expressions (CTE)](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-with) can be executed on TiFlash MPP. By default, when this variable is disabled, CTE is executed on TiDB, which has a large performance gap compared with enabling this feature.
### tidb_opt_enable_fuzzy_binding New in v7.6.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- This variable controls whether to enable the [Cross-database binding](https://docs.pingcap.com/tidb/stable/sql-plan-management#cross-database-binding) feature.
### tidb_opt_fix_control New in v6.5.3 and v7.1.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: String
- Default value: `""`
- This variable is used to control some internal behaviors of the optimizer.
- The optimizer's behavior might vary depending on user scenarios or SQL statements. This variable provides a more fine-grained control over the optimizer and helps to prevent performance regression after upgrading caused by behavior changes in the optimizer.
- For a more detailed introduction, see [Optimizer Fix Controls](https://docs.pingcap.com/tidb/stable/optimizer-fix-controls).

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: String
- Default value: `""`
- This variable is used to control some internal behaviors of the optimizer.
- The optimizer's behavior might vary depending on user scenarios or SQL statements. This variable provides a more fine-grained control over the optimizer and helps to prevent performance regression after upgrading caused by behavior changes in the optimizer.
- For a more detailed introduction, see [Optimizer Fix Controls](https://docs.pingcap.com/tidb/stable/optimizer-fix-controls).
### tidb_opt_force_inline_cte New in v6.3.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- This variable is used to control whether common table expressions (CTEs) in the entire session are inlined or not. The default value is `OFF`, which means that inlining CTE is not enforced by default. However, you can still inline CTE by specifying the `MERGE()` hint. If the variable is set to `ON`, all CTEs (except recursive CTE) in this session are forced to be inlined.
### tidb_opt_advanced_join_hint New in v7.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `ON`
- This variable is used to control whether the Join Method hint, such as [`HASH_JOIN()` hint](https://docs.pingcap.com/tidb/stable/optimizer-hints#hash_joint1_name--tl_name-) and [`MERGE_JOIN()` hint](https://docs.pingcap.com/tidb/stable/optimizer-hints#merge_joint1_name--tl_name-), affects the Join Reorder optimization process, including the use of [`LEADING()` hint](https://docs.pingcap.com/tidb/stable/optimizer-hints#leadingt1_name--tl_name-). The default value is `ON`, which means that it does not affect. If it is set to `OFF`, there might be conflicts in some scenarios where both Join Method hint and `LEADING()` hint are used at the same time.

> **Note:**
>
> The behavior of versions earlier than v7.0.0 is consistent with that of setting this variable to `OFF`. To ensure forward compatibility, when you upgrade from an earlier version to a v7.0.0 or later cluster, this variable is set to `OFF`. To obtain more flexible hint behavior, it is strongly recommended to switch this variable to `ON` under the condition that there is no performance regression.
