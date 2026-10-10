# Cartesian join identification and optimizer issue analysis

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/analyze-slow-queries.md`
- Source Title: `Analyze Slow Queries`
- Source Heading Path: `Analyze Slow Queries > Analyze system issues > TiDB is slow in execution > Join operations with Cartesian product | Analyze Slow Queries > Analyze optimizer issues`
- Source Line Ranges: `214-255`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `slow-queries`, `execution-plan`, `cartesian-join`, `optimizer`, `table-scan`, `index-reader`, `index-lookup`, `index-full-scan`, `sql-tuning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0006_03b6a387aa`
- Source ID: `tidb-docs-8.1:analyze-slow-queries.md#join-operations-with-cartesian-product`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ffe7918cea40bee35ffa9d1eb72a45d19b63b1391597c56b0304fa00f8c7b33d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/analyze-slow-queries#join-operations-with-cartesian-product
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/analyze-slow-queries.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing slow queries by checking whether an execution plan shows a Cartesian join or whether operators such as TableFullScan, IndexReader, IndexLookup, or IndexFullScan are reasonable for the SQL.
- Retrieval Keywords: CARTESIAN, Cartesian join, HashJoin_8, TableFullScan, IndexReader, IndexLookup, IndexFullScan, execution plan, EXPLAIN, select * from t t1, t t2 where t1.a>t2.a, select * from t, select a from t where a=2, select * from t where a=2, select b from t where c=3, optimizer issues, Wrong Index Solution, Wrong join order, Expressions are not pushed down, SQL Tuning Overview, Understand TiDB Execution Plan
- Follow-up Guidance: The source points to Understand TiDB Execution Plan, SQL Tuning Overview, Wrong Index Solution, Wrong join order, and Expressions are not pushed down for more operator details and related optimizer issue solutions.
- Classification Note: This chunk is classified as diagnosis for SQL because it explains how to judge whether a query execution plan is reasonable and how to identify Cartesian joins and data read operators in slow query analysis.

## Official Source Content

#### Join operations with Cartesian product

Join operations with Cartesian product generate data volume as large as `left child row count * right child row count`. This is inefficient and should be avoided.

This type of join operations is marked `CARTESIAN` in the execution plan. For example:

```sql
mysql> explain select * from t t1, t t2 where t1.a>t2.a;
+------------------------------+-------------+-----------+---------------+---------------------------------------------------------+
| id                           | estRows     | task      | access object | operator info                                           |
+------------------------------+-------------+-----------+---------------+---------------------------------------------------------+
| HashJoin_8                   | 99800100.00 | root      |               | CARTESIAN inner join, other cond:gt(test.t.a, test.t.a) |
| ├─TableReader_15(Build)      | 9990.00     | root      |               | data:Selection_14                                       |
| │ └─Selection_14             | 9990.00     | cop[tikv] |               | not(isnull(test.t.a))                                   |
| │   └─TableFullScan_13       | 10000.00    | cop[tikv] | table:t2      | keep order:false, stats:pseudo                          |
| └─TableReader_12(Probe)      | 9990.00     | root      |               | data:Selection_11                                       |
|   └─Selection_11             | 9990.00     | cop[tikv] |               | not(isnull(test.t.a))                                   |
|     └─TableFullScan_10       | 10000.00    | cop[tikv] | table:t1      | keep order:false, stats:pseudo                          |
+------------------------------+-------------+-----------+---------------+---------------------------------------------------------+
```
## Analyze optimizer issues

To analyze optimizer issues, you need to determine whether the execution plan is reasonable or not. You need to have some understanding of the optimization process and each operator.

For the following examples, assume that the table schema is `create table t (id int, a int, b int, c int, primary key(id), key(a), key(b, c))`.

1. `select * from t`: There is no filter condition and a full table scan is performed. So the `TableFullScan` operator is used to read data.
2. `select a from t where a=2`: There is a filter condition and only the index columns are read, so the `IndexReader` operator is used to read data.
3. `select * from t where a=2`: There is a filter condition for `a` but the `a` index cannot fully cover the data to be read, so the `IndexLookup` operator is used.
4. `select b from t where c=3`: Without the prefix condition, the multi-column index cannot be used. So the `IndexFullScan` is used.
5. ...

The examples above are operators used for data reads. For more operators, see [Understand TiDB Execution Plan](https://docs.pingcap.com/tidb/stable/explain-overview).

In addition, reading [SQL Tuning Overview](https://docs.pingcap.com/tidb/stable/sql-tuning-overview) helps you better understand the TiDB optimizer and determine whether the execution plan is reasonable or not.

Most optimizer issues are explained in [SQL Tuning Overview](https://docs.pingcap.com/tidb/stable/sql-tuning-overview). For the solutions, see the following documents:

1. [Wrong Index Solution](https://docs.pingcap.com/tidb/stable/wrong-index-solution)
2. [Wrong join order](https://docs.pingcap.com/tidb/stable/join-reorder)
3. [Expressions are not pushed down](https://docs.pingcap.com/tidb/stable/blocklist-control-plan)
