# EXPLAIN execution plan overview and output columns

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-overview.md`
- Source Title: `TiDB Query Execution Plan Overview`
- Source Heading Path: `TiDB Query Execution Plan Overview | TiDB Query Execution Plan Overview > Understand EXPLAIN output`
- Source Line Ranges: `5-58`
- Source Scope: `shared`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `explain`, `execution-plan`, `sql-optimization`, `operator`, `estrows`, `task`, `access-object`, `operator-info`, `explain-analyze`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0265_8c241002cc`
- Source ID: `tidb-docs-8.1:explain-overview.md#tidb-query-execution-plan-overview`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b2c9ac39b085f297201053ae9b29ce21d07960d52f36b14dbc60c8c2f01f6ed1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-overview#tidb-query-execution-plan-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants an overview of the `EXPLAIN` execution plan output in TiDB, including what the columns `id`, `estRows`, `task`, `access object`, and `operator info` mean or how `EXPLAIN` differs from `EXPLAIN ANALYZE`.
- Retrieval Keywords: EXPLAIN, EXPLAIN ANALYZE, TiDB Query Execution Plan Overview, Understand EXPLAIN output, id, estRows, task, access object, operator info, IndexLookUp_10, IndexRangeScan_8(Build), TableRowIDScan_9(Probe), cop[tikv], root, table:t, index:a(a), range:[1,1], stats:pseudo, SQL optimization
- Follow-up Guidance: The source also points to related `EXPLAIN` examples for indexes, joins, subqueries, aggregation, views, and partitions.
- Classification Note: This is reference content because it defines the purpose of `EXPLAIN`, shows a sample execution plan, and explains the meaning of each output column for SQL execution plans in TiDB and TiKV.

## Official Source Content

# TiDB Query Execution Plan Overview

> **Note:**
>
> When you use the MySQL client to connect to TiDB, to read the output result in a clearer way without line wrapping, you can use the `pager less -S` command. Then, after the `EXPLAIN` result is output, you can press the right arrow <kbd>→</kbd> button on your keyboard to horizontally scroll through the output.

SQL is a declarative language. It describes what the results of a query should look like, **not the methodology** to actually retrieve those results. TiDB considers all the possible ways in which a query could be executed, including using what order to join tables and whether any potential indexes can be used. The process of _considering query execution plans_ is known as SQL optimization.

The `EXPLAIN` statement shows the selected execution plan for a given statement. That is, after considering hundreds or thousands of ways in which the query could be executed, TiDB believes that this _plan_ will consume the least resources and execute in the shortest amount of time:

```sql
CREATE TABLE t (id INT NOT NULL PRIMARY KEY auto_increment, a INT NOT NULL, pad1 VARCHAR(255), INDEX(a));
INSERT INTO t VALUES (1, 1, 'aaa'),(2,2, 'bbb');
EXPLAIN SELECT * FROM t WHERE a = 1;
```

```sql
Query OK, 0 rows affected (0.96 sec)

Query OK, 2 rows affected (0.02 sec)
Records: 2  Duplicates: 0  Warnings: 0

+-------------------------------+---------+-----------+---------------------+---------------------------------------------+
| id                            | estRows | task      | access object       | operator info                               |
+-------------------------------+---------+-----------+---------------------+---------------------------------------------+
| IndexLookUp_10                | 10.00   | root      |                     |                                             |
| ├─IndexRangeScan_8(Build)     | 10.00   | cop[tikv] | table:t, index:a(a) | range:[1,1], keep order:false, stats:pseudo |
| └─TableRowIDScan_9(Probe)     | 10.00   | cop[tikv] | table:t             | keep order:false, stats:pseudo              |
+-------------------------------+---------+-----------+---------------------+---------------------------------------------+
3 rows in set (0.00 sec)
```

`EXPLAIN` does not execute the actual query. [`EXPLAIN ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze) can be used to execute the query and show `EXPLAIN` information. This can be useful in diagnosing cases where the execution plan selected is suboptimal. For additional examples of using `EXPLAIN`, see the following documents:

* [Indexes](https://docs.pingcap.com/tidb/stable/explain-indexes)
* [Joins](https://docs.pingcap.com/tidb/stable/explain-joins)
* [Subqueries](https://docs.pingcap.com/tidb/stable/explain-subqueries)
* [Aggregation](https://docs.pingcap.com/tidb/stable/explain-aggregation)
* [Views](https://docs.pingcap.com/tidb/stable/explain-views)
* [Partitions](https://docs.pingcap.com/tidb/stable/explain-partitions)
## Understand EXPLAIN output

The following describes the output of the `EXPLAIN` statement above:

* `id` describes the name of an operator, or sub-task that is required to execute the SQL statement. See [Operator overview](#operator-overview) for additional details.
* `estRows` shows an estimate of the number of rows TiDB expects to process. This number might be based on dictionary information, such as when the access method is based on a primary or unique key, or it could be based on statistics such as a CMSketch or histogram.
* `task` shows where an operator is performing the work. See [Task overview](#task-overview) for additional details.
* `access object` shows the table, partition and index that is being accessed. The parts of the index are also shown, as in the case above that the column `a` from the index was used. This can be useful in cases where you have composite indexes.
* `operator info` shows additional details about the access. See [Operator info overview](#operator-info-overview) for additional details.
