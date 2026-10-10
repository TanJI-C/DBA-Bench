# ROLLUP execution plan and Expand operator interpretation

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/group-by-modifier.md`
- Source Title: `GROUP BY Modifiers`
- Source Heading Path: `GROUP BY Modifiers > How to interpret the ROLLUP execution plan`
- Source Line Ranges: `163-220`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tiflash`
- Topic Tags: `group-by`, `rollup`, `execution-plan`, `expand-operator`, `mpp`, `grouping-function`, `gid`, `aggregation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0311_a63297fbc5`
- Source ID: `tidb-docs-8.1:functions-and-operators/group-by-modifier.md#how-to-interpret-the-rollup-execution-plan`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `550114d7c1beb6945edb1a71c1d60243867892aca22671839be7a3fdc3d0a98f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/group-by-modifier#how-to-interpret-the-rollup-execution-plan
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/group-by-modifier.md

## Retrieval Guidance

- Use When: Use this chunk when interpreting an EXPLAIN plan for a WITH ROLLUP query that shows the Expand operator, gid, GROUPING function rewrites, or MPP execution on TiFlash.
- Retrieval Keywords: WITH ROLLUP, Expand operator, How to interpret the ROLLUP execution plan, GROUPING function, gid, grouping set, EXPLAIN SELECT year, month, grouping(year), grouping(month), SUM(profit) AS profit FROM bank GROUP BY year, month WITH ROLLUP, mpp[tiflash], ExchangeSender, HashAgg, level-projection, schema: [test.bank.profit,Column#6,Column#7,gid], Projection_8, Expand_20, group by year, month with rollup
- Follow-up Guidance: The content includes a worked example showing how `Expand` replicates one raw row into multiple rows with different `gid` values and how `GROUPING` is rewritten to use `GID` metadata during logical optimization.
- Classification Note: This is classified as reference content because it explains how to read official execution-plan fields and identifiers such as `Expand`, `gid`, `level-projection`, and rewritten `GROUPING` expressions for ROLLUP.

## Official Source Content

## How to interpret the ROLLUP execution plan

To meet the requirements of multidimensional grouping, multidimensional data aggregation uses the `Expand` operator to replicate data. Each replica corresponds to a group at a specific dimension. With the data shuffling capability of MPP, the `Expand` operator can rapidly reorganize and calculate a large volume of data between multiple TiFlash nodes, fully utilizing the computational power of each node.

The implementation of the `Expand` operator is similar to that of the `Projection` operator. The difference is that `Expand` is a multi-level `Projection`, which contains multiple levels of projection operation expressions. For each row of the raw data, the `Projection` operator generates only one row in results, whereas the `Expand` operator generates multiple rows in results (the number of rows is equal to the number of levels in projection operation expressions).

The following is an example of an execution plan:

```sql
explain SELECT year, month, grouping(year), grouping(month), SUM(profit) AS profit FROM bank GROUP BY year, month WITH ROLLUP;
+----------------------------------------+---------+--------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| id                                     | estRows | task         | access object | operator info                                                                                                                                                                                                                        |
+----------------------------------------+---------+--------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| TableReader_44                         | 2.40    | root         |               | MppVersion: 2, data:ExchangeSender_43                                                                                                                                                                                                |
| └─ExchangeSender_43                    | 2.40    | mpp[tiflash] |               | ExchangeType: PassThrough                                                                                                                                                                                                            |
|   └─Projection_8                       | 2.40    | mpp[tiflash] |               | Column#6->Column#12, Column#7->Column#13, grouping(gid)->Column#14, grouping(gid)->Column#15, Column#9->Column#16                                                                                                                    |
|     └─Projection_38                    | 2.40    | mpp[tiflash] |               | Column#9, Column#6, Column#7, gid                                                                                                                                                                                                    |
|       └─HashAgg_36                     | 2.40    | mpp[tiflash] |               | group by:Column#6, Column#7, gid, funcs:sum(test.bank.profit)->Column#9, funcs:firstrow(Column#6)->Column#6, funcs:firstrow(Column#7)->Column#7, funcs:firstrow(gid)->gid, stream_count: 8                                           |
|         └─ExchangeReceiver_22          | 3.00    | mpp[tiflash] |               | stream_count: 8                                                                                                                                                                                                                      |
|           └─ExchangeSender_21          | 3.00    | mpp[tiflash] |               | ExchangeType: HashPartition, Compression: FAST, Hash Cols: [name: Column#6, collate: binary], [name: Column#7, collate: utf8mb4_bin], [name: gid, collate: binary], stream_count: 8                                                  |
|             └─Expand_20                | 3.00    | mpp[tiflash] |               | level-projection:[test.bank.profit, <nil>->Column#6, <nil>->Column#7, 0->gid],[test.bank.profit, Column#6, <nil>->Column#7, 1->gid],[test.bank.profit, Column#6, Column#7, 3->gid]; schema: [test.bank.profit,Column#6,Column#7,gid] |
|               └─Projection_16          | 3.00    | mpp[tiflash] |               | test.bank.profit, test.bank.year->Column#6, test.bank.month->Column#7                                                                                                                                                                |
|                 └─TableFullScan_17     | 3.00    | mpp[tiflash] | table:bank    | keep order:false, stats:pseudo                                                                                                                                                                                                       |
+----------------------------------------+---------+--------------+---------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
10 rows in set (0.05 sec)
```

In this example execution plan, you can view the multiple-level expression of the `Expand` operator in the `operator info` column of the `Expand_20` row. It consists of 2-dimensional expressions, and you can view the schema information of the `Expand` operator at the end of the row, which is `schema: [test.bank.profit, Column#6, Column#7, gid]`.

In the schema information of the `Expand` operator, `GID` is generated as an additional column. Its value is calculated by the `Expand` operator based on the grouping logic of different dimensions, and the value reflects the relationship between the current data replica and the `grouping set`. In most cases, the `Expand` operator uses a Bit-And operation, which can represent 63 combinations of grouping items for ROLLUP, corresponding to 64 dimensions of grouping. In this mode, TiDB generates the `GID` value depending on whether the `grouping set` of the required dimension contains grouping expressions when the current data replica is replicated, and it fills a 64-bit UINT64 value in the order of columns to be grouped.

In the preceding example, the order of columns in the grouping list is `[year, month]`, and the dimension groups generated by the ROLLUP syntax are `{year, month}`, `{year}`, and `{}`. For the dimension group `{year, month}`, both `year` and `month` are required columns, so TiDB fills the bit positions for them with 1 and 1 correspondingly. This forms a UINT64 of `11...0`, which is 3 in decimal. Therefore, the projection expression is `[test.bank.profit, Column#6, Column#7, 3->gid]` (where `column#6` corresponds to `year`, and `column#7` corresponds to `month`).

The following is an example row of the raw data:

```sql
+------+-------+------+------------+
| year | month | day  | profit     |
+------+-------+------+------------+
| 2000 | Jan   |    1 | 10.3000000 |
+------+-------+------+------------+
```
After the `Expand` operator is applied, you can get the following three rows of results:

```sql
+------------+------+-------+-----+
| profit     | year | month | gid |
+------------+------+-------+-----+
| 10.3000000 | 2000 | Jan   |  3  |
+------------+------+-------+-----+
| 10.3000000 | 2000 | NULL  |  1  |
+------------+------+-------+-----+
| 10.3000000 | NULL | NULL  |  0  |
+------------+------+-------+-----+
```

Note that the `SELECT` clause in the query uses the `GROUPING` function. When the `GROUPING` function is used in the `SELECT`, `HAVING`, or `ORDER BY` clauses, TiDB rewrites it during the logical optimization phase, transforms the relationship between the `GROUPING` function and the `GROUP BY` items into a `GID` related to the logic of dimension group (also known as `grouping set`), and fills this `GID` as metadata into the new `GROUPING` function.
