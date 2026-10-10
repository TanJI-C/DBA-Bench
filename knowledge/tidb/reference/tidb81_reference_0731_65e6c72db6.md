# Optimizer rule and cost model system variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_opt_insubq_to_join_and_agg | System Variables > Variable reference > tidb_opt_join_reorder_threshold | System Variables > Variable reference > tidb_opt_limit_push_down_threshold | System Variables > Variable reference > tidb_opt_memory_factor | System Variables > Variable reference > tidb_opt_mpp_outer_join_fixed_build_side <span class="version-mark">New in v5.1.0</span> | System Variables > Variable reference > tidb_opt_network_factor | System Variables > Variable reference > tidb_opt_objective <span class="version-mark">New in v7.4.0</span>`
- Source Line Ranges: `4191-4279`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`, `tiflash`
- Topic Tags: `system-variables`, `optimizer`, `join-reorder`, `limit-pushdown`, `cost-model`, `mpp`, `execution-plans`, `statistics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0731_65e6c72db6`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-opt-insubq-to-join-and-agg`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a38cb369d37e4ea920a20763e9766f611e543c130f577d973968ec198e3afdd6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-opt-insubq-to-join-and-agg
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB optimizer-related system variables that control subquery-to-join conversion, join reorder algorithm selection, Limit or TopN pushdown to TiKV, cost model factors, MPP outer join build side behavior, or optimizer objective and execution plan stability.
- Retrieval Keywords: tidb_opt_insubq_to_join_and_agg, subquery to join and aggregation, select * from t where t.a in (select aa from t1), select t.* from t, (select aa from t1 group by aa) tmp_t where t.a = tmp_t.aa, tidb_opt_join_reorder_threshold, Join Reorder algorithm, greedy algorithm, dynamic programming algorithm, tidb_opt_limit_push_down_threshold, Limit or TopN push down to TiKV, wrong estimation, tidb_opt_memory_factor, Cost Model, memory cost for TiDB to store one row, tidb_opt_mpp_outer_join_fixed_build_side, left join operator build side, right join operator build side, tidb_opt_network_factor, net cost of transferring 1 byte of data through the network, tidb_opt_objective, moderate, determinate, real-time statistics, execution plan more stable, LOCK STATS, SET_VAR
- Follow-up Guidance: The content also notes OLAP guidance for tidb_opt_join_reorder_threshold, that tidb_opt_memory_factor and tidb_opt_network_factor are internally used in the Cost Model and are not recommended to modify, and that LOCK STATS can further stabilize execution plans when tidb_opt_objective is set to determinate.
- Classification Note: This chunk is classified as reference content because it enumerates optimizer rule and cost model system variables with their scope, type, default values, ranges, possible values, and behavior descriptions from TiDB official documentation.

## Official Source Content

### tidb_opt_insubq_to_join_and_agg

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `ON`
- This variable is used to set whether to enable the optimization rule that converts a subquery to join and aggregation.
- For example, after you enable this optimization rule, the subquery is converted as follows:

    ```sql
    select * from t where t.a in (select aa from t1);
    ```

    The subquery is converted to join as follows:

    ```sql
    select t.* from t, (select aa from t1 group by aa) tmp_t where t.a = tmp_t.aa;
    ```

    If `t1` is limited to be `unique` and `not null` in the `aa` column. You can use the following statement, without aggregation.

    ```sql
    select t.* from t, t1 where t.a=t1.aa;
    ```
### tidb_opt_join_reorder_threshold

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `0`
- Range: `[0, 2147483647]`
- This variable is used to control the selection of the TiDB Join Reorder algorithm. When the number of nodes participating in Join Reorder is greater than this threshold, TiDB selects the greedy algorithm, and when it is less than this threshold, TiDB selects the dynamic programming algorithm.
- Currently, for OLTP queries, it is recommended to keep the default value. For OLAP queries, it is recommended to set the variable value to 10~15 to get better connection orders in OLAP scenarios.
### tidb_opt_limit_push_down_threshold

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `100`
- Range: `[0, 2147483647]`
- This variable is used to set the threshold that determines whether to push the Limit or TopN operator down to TiKV.
- If the value of the Limit or TopN operator is smaller than or equal to this threshold, these operators are forcibly pushed down to TiKV. This variable resolves the issue that the Limit or TopN operator cannot be pushed down to TiKV partly due to wrong estimation.
### tidb_opt_memory_factor

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Float
- Range: `[0, 2147483647]`
- Default value: `0.001`
- Indicates the memory cost for TiDB to store one row. This variable is internally used in the [Cost Model](https://docs.pingcap.com/tidb/stable/cost-model), and it is **NOT** recommended to modify its value.
### tidb_opt_mpp_outer_join_fixed_build_side New in v5.1.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- When the variable value is `ON`, the left join operator always uses inner table as the build side and the right join operator always uses outer table as the build side. If you set the value to `OFF`, the outer join operator can use either side of the tables as the build side.
### tidb_opt_network_factor

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Float
- Range: `[0, 2147483647]`
- Default value: `1.0`
- Indicates the net cost of transferring 1 byte of data through the network. This variable is internally used in the [Cost Model](https://docs.pingcap.com/tidb/stable/cost-model), and it is **NOT** recommended to modify its value.
### tidb_opt_objective New in v7.4.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Enumeration
- Default value: `moderate`
- Possible values: `moderate`, `determinate`
- This variable controls the objective of the optimizer. `moderate` maintains the default behavior in versions prior to TiDB v7.4.0, where the optimizer tries to use more information to generate better execution plans. `determinate` mode tends to be more conservative and makes the execution plan more stable.
- The real-time statistics are the total number of rows and the number of modified rows that are automatically updated based on DML statements. When this variable is set to `moderate` (default), TiDB generates the execution plan based on real-time statistics. When this variable is set to `determinate`, TiDB does not use real-time statistics for generating the execution plan, which will make execution plans more stable.
- For long-term stable OLTP workload, or if the user is affirmative on the existing execution plans, it is recommended to use the `determinate` mode to reduce the possibility of unexpected execution plan changes. Additionally, you can use the [`LOCK STATS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-lock-stats) to prevent the statistics from being modified and further stabilize the execution plan.
