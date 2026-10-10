# Optimizer index selection and range scan preference variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_opt_ordering_index_selectivity_threshold <span class="version-mark">New in v7.0.0</span> | System Variables > Variable reference > tidb_opt_prefer_range_scan <span class="version-mark">New in v5.0</span>`
- Source Line Ranges: `4384-4458`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `system-variables`, `optimizer`, `index-selection`, `order-by`, `limit`, `range-scan`, `explain`, `set-var`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0733_9a3f96c80d`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-opt-ordering-index-selectivity-threshold-span-class-version-mark-new-in-v7-0-0-span`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1414496473ac6a66adb42fe16e14b0af69fea4524a5802f5141d4612477d09a8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-opt-ordering-index-selectivity-threshold-span-class-version-mark-new-in-v7-0-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB system variables that change optimizer index choice for queries with ORDER BY and LIMIT plus filter conditions, or that make the optimizer prefer range scans over full table scans.
- Retrieval Keywords: tidb_opt_ordering_index_selectivity_threshold, tidb_opt_prefer_range_scan, ORDER BY LIMIT index selection, optimizer selects index for filter conditions, selectivity threshold, range scan over full table scan, SET_VAR, EXPLAIN SELECT * FROM t WHERE b <= 9000 ORDER BY a LIMIT 1, SET SESSION tidb_opt_ordering_index_selectivity_threshold = 0.01, EXPLAIN SELECT * FROM t WHERE age=5, set session tidb_opt_prefer_range_scan = 1, IndexFullScan, IndexRangeScan, TableFullScan, TopN, keep order:true
- Follow-up Guidance: The content includes EXPLAIN examples showing plan changes after setting tidb_opt_ordering_index_selectivity_threshold to 0.01 and tidb_opt_prefer_range_scan to 1.
- Classification Note: This is reference content because it defines the scope, persistence, type, default value, range, and optimizer behavior of the system variables tidb_opt_ordering_index_selectivity_threshold and tidb_opt_prefer_range_scan.

## Official Source Content

### tidb_opt_ordering_index_selectivity_threshold New in v7.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Float
- Default value: `0`
- Range: `[0, 1]`
- This variable is used to control how the optimizer selects an index when there are `ORDER BY` and `LIMIT` clauses with filter conditions in a SQL statement.
- For such queries, the optimizer considers selecting the corresponding index to satisfy the `ORDER BY` and `LIMIT` clauses (even if this index does not satisfy any filter conditions). However, due to the complexity of data distribution, the optimizer might select a suboptimal index in this scenario.
- This variable represents a threshold. When an index exists that can satisfy filtering conditions and its selectivity estimate is lower than this threshold, the optimizer will avoid selecting an index used to satisfy `ORDER BY` and `LIMIT`. Instead, it prioritizes an index that satisfies the filtering conditions.
- For example, when the variable is set to `0`, the optimizer maintains its default behavior; when it is set to `1`, the optimizer always prioritizes selecting indexes that satisfy the filter conditions and avoids selecting indexes that satisfy both `ORDER BY` and `LIMIT` clauses.
- In the following example, table `t` has a total of 1,000,000 rows. When using an index on column `b`, its estimated row count is approximately 8,748, so its selectivity estimate value is about 0.0087. By default, the optimizer selects an index on column `a`. However, after setting this variable to 0.01, since the selectivity of an index on column `b` (0.0087) is less than 0.01, the optimizer selects an index on column `b`.

```sql
> EXPLAIN SELECT * FROM t WHERE b <= 9000 ORDER BY a LIMIT 1;
+-----------------------------------+---------+-----------+----------------------+--------------------+
| id                                | estRows | task      | access object        | operator info      |
+-----------------------------------+---------+-----------+----------------------+--------------------+
| Limit_12                          | 1.00    | root      |                      | offset:0, count:1  |
| └─Projection_25                   | 1.00    | root      |                      | test.t.a, test.t.b |
|   └─IndexLookUp_24                | 1.00    | root      |                      |                    |
|     ├─IndexFullScan_21(Build)     | 114.30  | cop[tikv] | table:t, index:ia(a) | keep order:true    |
|     └─Selection_23(Probe)         | 1.00    | cop[tikv] |                      | le(test.t.b, 9000) |
|       └─TableRowIDScan_22         | 114.30  | cop[tikv] | table:t              | keep order:false   |
+-----------------------------------+---------+-----------+----------------------+--------------------+

> SET SESSION tidb_opt_ordering_index_selectivity_threshold = 0.01;

> EXPLAIN SELECT * FROM t WHERE b <= 9000 ORDER BY a LIMIT 1;
+----------------------------------+---------+-----------+----------------------+-------------------------------------+
| id                               | estRows | task      | access object        | operator info                       |
+----------------------------------+---------+-----------+----------------------+-------------------------------------+
| TopN_9                           | 1.00    | root      |                      | test.t.a, offset:0, count:1         |
| └─IndexLookUp_20                 | 1.00    | root      |                      |                                     |
|   ├─IndexRangeScan_17(Build)     | 8748.62 | cop[tikv] | table:t, index:ib(b) | range:[-inf,9000], keep order:false |
|   └─TopN_19(Probe)               | 1.00    | cop[tikv] |                      | test.t.a, offset:0, count:1         |
|     └─TableRowIDScan_18          | 8748.62 | cop[tikv] | table:t              | keep order:false                    |
+----------------------------------+---------+-----------+----------------------+-------------------------------------+
```
### tidb_opt_prefer_range_scan New in v5.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- After you set the value of this variable to `ON`, the optimizer always prefers range scans over full table scans.
- In the following example, before you enable `tidb_opt_prefer_range_scan`, the TiDB optimizer performs a full table scan. After you enable `tidb_opt_prefer_range_scan`, the optimizer selects an index range scan.

```sql
explain select * from t where age=5;
+-------------------------+------------+-----------+---------------+-------------------+
| id                      | estRows    | task      | access object | operator info     |
+-------------------------+------------+-----------+---------------+-------------------+
| TableReader_7           | 1048576.00 | root      |               | data:Selection_6  |
| └─Selection_6           | 1048576.00 | cop[tikv] |               | eq(test.t.age, 5) |
|   └─TableFullScan_5     | 1048576.00 | cop[tikv] | table:t       | keep order:false  |
+-------------------------+------------+-----------+---------------+-------------------+
3 rows in set (0.00 sec)

set session tidb_opt_prefer_range_scan = 1;

explain select * from t where age=5;
+-------------------------------+------------+-----------+-----------------------------+-------------------------------+
| id                            | estRows    | task      | access object               | operator info                 |
+-------------------------------+------------+-----------+-----------------------------+-------------------------------+
| IndexLookUp_7                 | 1048576.00 | root      |                             |                               |
| ├─IndexRangeScan_5(Build)     | 1048576.00 | cop[tikv] | table:t, index:idx_age(age) | range:[5,5], keep order:false |
| └─TableRowIDScan_6(Probe)     | 1048576.00 | cop[tikv] | table:t                     | keep order:false              |
+-------------------------------+------------+-----------+-----------------------------+-------------------------------+
3 rows in set (0.00 sec)
```
