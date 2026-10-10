# Optimizer pushdown for prefix index scan and projection

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_opt_prefix_index_single_scan <span class="version-mark">New in v6.4.0</span> | System Variables > Variable reference > tidb_opt_projection_push_down <span class="version-mark">New in v6.1.0</span>`
- Source Line Ranges: `4459-4530`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `tiflash`
- Topic Tags: `system-variables`, `optimizer`, `prefix-index`, `single-scan`, `projection-pushdown`, `coprocessor`, `query-performance`, `execution-plan`, `set-var`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0734_c951c3f4f8`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-opt-prefix-index-single-scan-span-class-version-mark-new-in-v6-4-0-span`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `620b9f8ecfaaa51cc00cc55869d43353aad1486cb05821895fe18a85719f0183`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-opt-prefix-index-single-scan-span-class-version-mark-new-in-v6-4-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB system variables that control prefix index single-scan optimization or Projection pushdown to TiKV or TiFlash coprocessors, including EXPLAIN plan differences and SET_VAR applicability.
- Retrieval Keywords: tidb_opt_prefix_index_single_scan, tidb_opt_projection_push_down, SET_VAR, prefix index, single scan, projection pushdown, TiKV coprocessor, TiFlash coprocessor, IndexLookUp, IndexReader, IndexRangeScan, TableRowIDScan, b IS NOT NULL, col is null, col is not null, EXPLAIN FORMAT='brief'
- Follow-up Guidance: The content includes an example showing how setting tidb_opt_prefix_index_single_scan to OFF or ON changes the EXPLAIN FORMAT='brief' plan from IndexLookUp with TableRowIDScan to IndexReader without table lookup.
- Classification Note: This is reference content because it defines the scope, persistence, default value, hint applicability, and behavior of the system variables tidb_opt_prefix_index_single_scan and tidb_opt_projection_push_down.

## Official Source Content

### tidb_opt_prefix_index_single_scan New in v6.4.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Default value: `ON`
- This variable controls whether the TiDB optimizer pushes down some filter conditions to the prefix index to avoid unnecessary table lookup and to improve query performance.
- When this variable value is set to `ON`, some filter conditions are pushed down to the prefix index. Suppose that the `col` column is the index prefix column in a table. The `col is null` or `col is not null` condition in the query is handled as a filter condition on the index instead of a filter condition for the table lookup, so that unnecessary table lookup is avoided.

<details>
<summary>Usage example of <code>tidb_opt_prefix_index_single_scan</code></summary>

Create a table with a prefix index:

```sql
CREATE TABLE t (a INT, b VARCHAR(10), c INT, INDEX idx_a_b(a, b(5)));
```

Disable `tidb_opt_prefix_index_single_scan`:

```sql
SET tidb_opt_prefix_index_single_scan = 'OFF';
```

For the following query, the execution plan uses the prefix index `idx_a_b` but requires a table lookup (the `IndexLookUp` operator appears).

```sql
EXPLAIN FORMAT='brief' SELECT COUNT(1) FROM t WHERE a = 1 AND b IS NOT NULL;
+-------------------------------+---------+-----------+------------------------------+-------------------------------------------------------+
| id                            | estRows | task      | access object                | operator info                                         |
+-------------------------------+---------+-----------+------------------------------+-------------------------------------------------------+
| HashAgg                       | 1.00    | root      |                              | funcs:count(Column#8)->Column#5                       |
| └─IndexLookUp                 | 1.00    | root      |                              |                                                       |
|   ├─IndexRangeScan(Build)     | 99.90   | cop[tikv] | table:t, index:idx_a_b(a, b) | range:[1 -inf,1 +inf], keep order:false, stats:pseudo |
|   └─HashAgg(Probe)            | 1.00    | cop[tikv] |                              | funcs:count(1)->Column#8                              |
|     └─Selection               | 99.90   | cop[tikv] |                              | not(isnull(test.t.b))                                 |
|       └─TableRowIDScan        | 99.90   | cop[tikv] | table:t                      | keep order:false, stats:pseudo                        |
+-------------------------------+---------+-----------+------------------------------+-------------------------------------------------------+
6 rows in set (0.00 sec)
```

Enable `tidb_opt_prefix_index_single_scan`:

```sql
SET tidb_opt_prefix_index_single_scan = 'ON';
```

After enabling this variable, for the following query, the execution plan uses the prefix index `idx_a_b` but does not require a table lookup.

```sql
EXPLAIN FORMAT='brief' SELECT COUNT(1) FROM t WHERE a = 1 AND b IS NOT NULL;
+--------------------------+---------+-----------+------------------------------+-------------------------------------------------------+
| id                       | estRows | task      | access object                | operator info                                         |
+--------------------------+---------+-----------+------------------------------+-------------------------------------------------------+
| StreamAgg                | 1.00    | root      |                              | funcs:count(Column#7)->Column#5                       |
| └─IndexReader            | 1.00    | root      |                              | index:StreamAgg                                       |
|   └─StreamAgg            | 1.00    | cop[tikv] |                              | funcs:count(1)->Column#7                              |
|     └─IndexRangeScan     | 99.90   | cop[tikv] | table:t, index:idx_a_b(a, b) | range:[1 -inf,1 +inf], keep order:false, stats:pseudo |
+--------------------------+---------+-----------+------------------------------+-------------------------------------------------------+
4 rows in set (0.00 sec)
```

</details>
### tidb_opt_projection_push_down New in v6.1.0

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- Specifies whether to allow the optimizer to push `Projection` down to the TiKV or TiFlash coprocessor.
