# EXPLAIN examples for brief, dot, and tidb_json formats

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-explain.md`
- Source Title: `EXPLAIN | TiDB SQL Statement Reference`
- Source Heading Path: ``EXPLAIN` > Examples`
- Source Line Ranges: `195-299`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `explain`, `execution-plan`, `format`, `brief`, `dot`, `graphviz`, `tidb_json`, `plan-cache`, `verbose`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0590_90f76791c3`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-explain.md#examples`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b5e4d9bc81763a477cf43dc388b47ca30d8925c8d439d41fd5f7953b8722d328`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain#examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-explain.md

## Retrieval Guidance

- Use When: Use this chunk when looking for EXPLAIN output format options and examples for brief, dot, row, tidb_json, verbose, or plan_cache in TiDB.
- Retrieval Keywords: EXPLAIN FORMAT = "brief", EXPLAIN FORMAT = "dot", EXPLAIN FORMAT = "tidb_json", EXPLAIN FORMAT, brief, dot, row, verbose, plan_cache, default format row, DOT execution plans, graphviz, dot program, dot xx.dot -T png -O, JSON array, estCost, Plan Cache, Delete, TableReader, Selection, TableFullScan, HashJoin, Projection
- Follow-up Guidance: The content also notes that dot output can be rendered with the dot program in the graphviz package or copied to the referenced website to get a tree diagram.
- Classification Note: This is reference content because it enumerates EXPLAIN FORMAT descriptions and provides example outputs for brief, dot, and tidb_json formats.

## Official Source Content

| FORMAT | Description |
| ------ | ------ |
| Not specified  | If the format is not specified, `EXPLAIN` uses the default format `row`. |
| `brief`        | The operator IDs in the output of the `EXPLAIN` statement are simplified, compared with those when `FORMAT` is left unspecified. |
| `dot`          | The `EXPLAIN` statement outputs DOT execution plans, which can be used to generate PNG files through a `dot` program (in the `graphviz` package). |
| `row`          | The `EXPLAIN` statement outputs results in a tabular format. See [Understand the Query Execution Plan](https://docs.pingcap.com/tidb/stable/explain-overview) for more information. |
| `tidb_json`    | The `EXPLAIN` statement outputs execution plans in JSON and stores the operator information in a JSON array. |
| `verbose`      | The `EXPLAIN` statement outputs results in the `row` format, with an additional `estCost` column for the estimated cost of the query in the results. For more information about how to use this format, see [SQL Plan Management](https://docs.pingcap.com/tidb/stable/sql-plan-management). |
| `plan_cache`   | The `EXPLAIN` statement outputs results in the `row` format, with the [Plan Cache](https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache#diagnostics) information as a warning. |

<div label="brief">

The following is an example when `FORMAT` is `"brief"` in `EXPLAIN`:

```sql
EXPLAIN FORMAT = "brief" DELETE FROM t1 WHERE c1 = 3;
```

```sql
+-------------------------+---------+-----------+---------------+--------------------------------+
| id                      | estRows | task      | access object | operator info                  |
+-------------------------+---------+-----------+---------------+--------------------------------+
| Delete                  | N/A     | root      |               | N/A                            |
| └─TableReader           | 0.00    | root      |               | data:Selection                 |
|   └─Selection           | 0.00    | cop[tikv] |               | eq(test.t1.c1, 3)              |
|     └─TableFullScan     | 3.00    | cop[tikv] | table:t1      | keep order:false, stats:pseudo |
+-------------------------+---------+-----------+---------------+--------------------------------+
4 rows in set (0.001 sec)
```

</div>

<div label="DotGraph">

In addition to the MySQL standard result format, TiDB also supports DotGraph and you need to specify `FORMAT = "dot"` as in the following example:

```sql
CREATE TABLE t(a bigint, b bigint);
EXPLAIN format = "dot" SELECT A.a, B.b FROM t A JOIN t B ON A.a > B.b WHERE A.a < 10;
```
```sql
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| dot contents                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|
digraph Projection_8 {
subgraph cluster8{
node [style=filled, color=lightgrey]
color=black
label = "root"
"Projection_8" -> "HashJoin_9"
"HashJoin_9" -> "TableReader_13"
"HashJoin_9" -> "Selection_14"
"Selection_14" -> "TableReader_17"
}
subgraph cluster12{
node [style=filled, color=lightgrey]
color=black
label = "cop"
"Selection_12" -> "TableFullScan_11"
}
subgraph cluster16{
node [style=filled, color=lightgrey]
color=black
label = "cop"
"Selection_16" -> "TableFullScan_15"
}
"TableReader_13" -> "Selection_12"
"TableReader_17" -> "Selection_16"
}
 |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

If your computer has a `dot` program, you can generate a PNG file using the following method:

```bash
dot xx.dot -T png -O

The xx.dot is the result returned by the above statement.
```

If your computer has no `dot` program, copy the result to [this website](http://www.webgraphviz.com/) to get a tree diagram:

![Explain Dot](/media/explain_dot.png)

</div>

<div label="JSON">

To get the output in JSON, specify `FORMAT = "tidb_json"` in the `EXPLAIN` statement. The following is an example:

```sql
CREATE TABLE t(id int primary key, a int, b int, key(a));
EXPLAIN FORMAT = "tidb_json" SELECT id FROM t WHERE a = 1;
```
