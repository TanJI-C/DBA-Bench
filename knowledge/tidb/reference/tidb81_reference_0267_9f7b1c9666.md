# EXPLAIN operators, range queries, tasks, and operator info

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-overview.md`
- Source Title: `TiDB Query Execution Plan Overview`
- Source Heading Path: `TiDB Query Execution Plan Overview > Understand EXPLAIN output > Operator overview | TiDB Query Execution Plan Overview > Understand EXPLAIN output > Operator overview > Range query | TiDB Query Execution Plan Overview > Understand EXPLAIN output > Task overview | TiDB Query Execution Plan Overview > Understand EXPLAIN output > Operator info overview`
- Source Line Ranges: `133-180`
- Source Scope: `shared`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `tiflash`, `shared`
- Topic Tags: `explain`, `execution-plan`, `operators`, `table-scan`, `index-scan`, `range-query`, `sargable`, `coprocessor`, `task-types`, `pushdown`, `operator-info`, `optimizer-hints`, `statistics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0267_9f7b1c9666`
- Source ID: `tidb-docs-8.1:explain-overview.md#operator-overview`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f3153949cb68dc9835db001fff41f3dc0caa66b5c8f48e004cb504432118eab1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-overview#operator-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-overview.md

## Retrieval Guidance

- Use When: Use this chunk when interpreting TiDB EXPLAIN output for scan operators, range query sargability, task types such as cop[tikv] and root, or operator info fields like range, keep order, and stats:pseudo.
- Retrieval Keywords: EXPLAIN, Operator overview, TableFullScan, TableRangeScan, TableRowIDScan, IndexFullScan, IndexRangeScan, TableReader, IndexReader, IndexLookUp, IndexMerge, Build, Probe, Range query, sargable, YEAR(date_column) < 1992, date_column < '1992-01-01', composite index (a, b, c), cop[tikv], root task, TiKV coprocessor, operator info, range: [1,1], keep order:false, keep order:true, stats:pseudo, ANALYZE TABLE t, optimizer hints, HASH_JOIN(t1, t2)
- Follow-up Guidance: The source also notes that optimizer hints can control physical operator selection, for example `/*+ HASH_JOIN(t1, t2) */`, and that `stats:pseudo` means `estRows` estimates might be inaccurate until statistics are updated or `ANALYZE TABLE t` is run.
- Classification Note: This chunk is reference material because it defines EXPLAIN operator names, explains range-query and task concepts, and describes operator info fields shown in official query plans.

## Official Source Content

### Operator overview

An operator is a particular step that is executed as part of returning query results. The operators that perform table scans (of the disk or the TiKV Block Cache) are listed as follows:

- **TableFullScan**: Full table scan
- **TableRangeScan**: Table scans with the specified range
- **TableRowIDScan**: Scans the table data based on the RowID. Usually follows an index read operation to retrieve the matching data rows.
- **IndexFullScan**: Similar to a "full table scan", except that an index is scanned, rather than the table data.
- **IndexRangeScan**: Index scans with the specified range.

TiDB aggregates the data or calculation results scanned from TiKV/TiFlash. The data aggregation operators can be divided into the following categories:

- **TableReader**: Aggregates the data obtained by the underlying operators like `TableFullScan` or `TableRangeScan` in TiKV.
- **IndexReader**: Aggregates the data obtained by the underlying operators like `IndexFullScan` or `IndexRangeScan` in TiKV.
- **IndexLookUp**: First aggregates the RowID (in TiKV) scanned by the `Build` side. Then at the `Probe` side, accurately reads the data from TiKV based on these RowIDs. At the `Build` side, there are operators like `IndexFullScan` or `IndexRangeScan`; at the `Probe` side, there is the `TableRowIDScan` operator.
- **IndexMerge**: Similar to `IndexLookUp`. `IndexMerge` can be seen as an extension of `IndexLookupReader`. `IndexMerge` supports reading multiple indexes at the same time. There are many `Build`s and one `Probe`. The execution process of `IndexMerge` the same as that of `IndexLookUp`.

While the structure appears as a tree, executing the query does not strictly require the child nodes to be completed before the parent nodes. TiDB supports intra-query parallelism, so a more accurate way to describe the execution is that the child nodes _flow into_ their parent nodes. Parent, child and sibling operators _might_ potentially be executing parts of the query in parallel.

In the previous example, the `├─IndexRangeScan_8(Build)` operator finds the internal `RowID` for rows that match the `a(a)` index. The `└─TableRowIDScan_9(Probe)` operator then retrieves these rows from the table.
#### Range query

In the `WHERE`/`HAVING`/`ON` conditions, the TiDB optimizer analyzes the result returned by the primary key query or the index key query. For example, these conditions might include comparison operators of the numeric and date type, such as `>`, `<`, `=`, `>=`, `<=`, and the character type such as `LIKE`.

> **Note:**
>
> - In order to use an index, the condition must be _sargable_. For example, the condition `YEAR(date_column) < 1992` cannot use an index, but `date_column < '1992-01-01` can.
> - It is recommended to compare data of the same type and [character set and collation](https://docs.pingcap.com/tidb/stable/character-set-and-collation). Mixing types may require additional `cast` operations, or prevent indexes from being used.
> - You can also use `AND` (intersection) and `OR` (union) to combine the range query conditions of one column. For a multi-dimensional composite index, you can use conditions in multiple columns. For example, regarding the composite index `(a, b, c)`:
>     - When `a` is an equivalent query, continue to figure out the query range of `b`; when `b` is also an equivalent query, continue to figure out the query range of `c`.
>     - Otherwise, if `a` is a non-equivalent query, you can only figure out the range of `a`.
### Task overview

Currently, calculation tasks of TiDB can be divided into two categories: cop tasks and root tasks. A `cop[tikv]` task indicates that the operator is performed inside the TiKV coprocessor. A `root` task indicates that it will be completed inside of TiDB.

One of the goals of SQL optimization is to push the calculation down to TiKV as much as possible. The Coprocessor in TiKV supports most of the built-in SQL functions (including the aggregate functions and the scalar functions), SQL `LIMIT` operations, index scans, and table scans.
### Operator info overview

The `operator info` can show useful information such as which conditions were able to be pushed down:

* `range: [1,1]` shows that the predicate from the where clause of the query (`a = 1`) was pushed right down to TiKV (the task is of `cop[tikv]`).
* `keep order:false` shows that the semantics of this query did not require TiKV to return the results in order. If the query were to be modified to require an order (such as `SELECT * FROM t WHERE a = 1 ORDER BY id`), then this condition would be `keep order:true`.
* `stats:pseudo` shows that the estimates shown in `estRows` might not be accurate. TiDB periodically updates statistics as part of a background operation. A manual update can also be performed by running `ANALYZE TABLE t`.

Different operators output different information after the `EXPLAIN` statement is executed. You can use optimizer hints to control the behavior of the optimizer, and thereby controlling the selection of the physical operators. For example, `/*+ HASH_JOIN(t1, t2) */` means that the optimizer uses the `Hash Join` algorithm. For more details, see [Optimizer Hints](https://docs.pingcap.com/tidb/stable/optimizer-hints).
