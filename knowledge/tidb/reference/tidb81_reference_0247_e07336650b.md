# Index Merge overview, enablement, and union plan example

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-index-merge.md`
- Source Title: `Explain Statements Using Index Merge`
- Source Heading Path: `Explain Statements Using Index Merge | Explain Statements Using Index Merge > Enable index merge | Explain Statements Using Index Merge > Examples`
- Source Line Ranges: `5-54`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `index-merge`, `explain`, `optimizer`, `union`, `execution-plan`, `session-variable`, `sql-hints`, `range-scan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0247_e07336650b`
- Source ID: `tidb-docs-8.1:explain-index-merge.md#explain-statements-using-index-merge`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1c68e196dbc1c56e71b4748f28732c853eb9ccdf097766ed98eac012c36426b0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-index-merge#explain-statements-using-index-merge
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-index-merge.md

## Retrieval Guidance

- Use When: Use this chunk when explaining how to enable Index Merge and read an EXPLAIN plan that shows a union-type IndexMerge for an OR predicate.
- Retrieval Keywords: Index Merge, tidb_enable_index_merge, SET session tidb_enable_index_merge = ON, USE_INDEX_MERGE(t), NO_INDEX_MERGE(), EXPLAIN SELECT, type: union, IndexMerge_8, IndexRangeScan, TableRowIDScan, WHERE a > 1 OR b > 1, range:(1,+inf]
- Follow-up Guidance: The chunk also shows how the operator info fields such as `type: union` and `range:(1,+inf]` identify the union index merge and scan ranges in EXPLAIN output.
- Classification Note: This is reference content because it defines Index Merge, states enablement conditions, and provides exact EXPLAIN and SQL examples for the union-type plan.

## Official Source Content

# Explain Statements Using Index Merge

Index merge is a method introduced in TiDB v4.0 to access tables. Using this method, the TiDB optimizer can use multiple indexes per table and merge the results returned by each index. In some scenarios, this method makes the query more efficient by avoiding full table scans.

Index merge in TiDB has two types: the intersection type and the union type. The former applies to the `AND` expression, while the latter applies to the `OR` expression. The union-type index merge is introduced in TiDB v4.0 as an experimental feature and has become GA in v5.4.0. The intersection type is introduced in TiDB v6.5.0, and can be used only when the [`USE_INDEX_MERGE`](https://docs.pingcap.com/tidb/stable/optimizer-hints#use_index_merget1_name-idx1_name--idx2_name-) hint is specified.
## Enable index merge

In v5.4.0 or a later TiDB version, index merge is enabled by default. In other situations, if index merge is not enabled, you need to set the variable [`tidb_enable_index_merge`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_index_merge-new-in-v40) to `ON` to enable this feature.

```sql
SET session tidb_enable_index_merge = ON;
```
## Examples

```sql
CREATE TABLE t(a int, b int, c int, d int, INDEX idx_a(a), INDEX idx_b(b), INDEX idx_c(c), INDEX idx_d(d));
```

```sql
EXPLAIN SELECT /*+ NO_INDEX_MERGE() */ * FROM t WHERE a = 1 OR b = 1;

+-------------------------+----------+-----------+---------------+--------------------------------------+
| id                      | estRows  | task      | access object | operator info                        |
+-------------------------+----------+-----------+---------------+--------------------------------------+
| TableReader_7           | 19.99    | root      |               | data:Selection_6                     |
| └─Selection_6           | 19.99    | cop[tikv] |               | or(eq(test.t.a, 1), eq(test.t.b, 1)) |
|   └─TableFullScan_5     | 10000.00 | cop[tikv] | table:t       | keep order:false, stats:pseudo       |
+-------------------------+----------+-----------+---------------+--------------------------------------+
EXPLAIN SELECT /*+ USE_INDEX_MERGE(t) */ * FROM t WHERE a > 1 OR b > 1;
+-------------------------------+---------+-----------+-------------------------+------------------------------------------------+
| id                            | estRows | task      | access object           | operator info                                  |
+-------------------------------+---------+-----------+-------------------------+------------------------------------------------+
| IndexMerge_8                  | 5555.56 | root      |                         | type: union                                    |
| ├─IndexRangeScan_5(Build)     | 3333.33 | cop[tikv] | table:t, index:idx_a(a) | range:(1,+inf], keep order:false, stats:pseudo |
| ├─IndexRangeScan_6(Build)     | 3333.33 | cop[tikv] | table:t, index:idx_b(b) | range:(1,+inf], keep order:false, stats:pseudo |
| └─TableRowIDScan_7(Probe)     | 5555.56 | cop[tikv] | table:t                 | keep order:false, stats:pseudo                 |
+-------------------------------+---------+-----------+-------------------------+------------------------------------------------+
```

In the preceding query, the filter condition is a `WHERE` clause that uses `OR` as the connector. Without index merge, you can use only one index per table. `a = 1` cannot be pushed down to the index `a`; neither can `b = 1` be pushed down to the index `b`. The full table scan is inefficient when a huge volume of data exists in `t`. To handle such a scenario, index merge is introduced in TiDB to access tables.

For the preceding query, the optimizer chooses the union-type index merge to access the table. Index merge allows the optimizer to use multiple indexes per table, to merge the results returned by each index, and to generate the latter execution plan in the preceding output.

In the output, the `type: union` information in `operator info` of the `IndexMerge_8` operator indicates that this operator is a union-type index merge. It has three child nodes. `IndexRangeScan_5` and `IndexRangeScan_6` scan the `RowID`s that meet the condition according to the range, and then the `TableRowIDScan_7` operator accurately reads all the data that meets the condition according to these `RowID`s.

For the scan operation that is performed on a specific range of data, such as `IndexRangeScan`/`TableRangeScan`, the `operator info` column in the result has additional information about the scan range compared with other scan operations like `IndexFullScan`/`TableFullScan`. In the above example, the `range:(1,+inf]` in the `IndexRangeScan_5` operator indicates that the operator scans the data from 1 to positive infinity.
