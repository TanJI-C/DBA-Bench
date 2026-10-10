# ROLLUP aggregation EXPLAIN in TiFlash MPP mode

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-aggregation.md`
- Source Title: `Explain Statements That Use Aggregation`
- Source Heading Path: `Explain Statements Using Aggregation > Multidimensional data aggregation with ROLLUP`
- Source Line Ranges: `174-205`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tiflash`
- Topic Tags: `explain`, `aggregation`, `rollup`, `group-by`, `mpp`, `tiflash`, `hash-aggregation`, `execution-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0246_0e4a59ff1c`
- Source ID: `tidb-docs-8.1:explain-aggregation.md#multidimensional-data-aggregation-with-rollup`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b85ea43298441d60d48e5ac6b2e38395c44aedbdea0fe5a54d8b1ad6a7146b39`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-aggregation#multidimensional-data-aggregation-with-rollup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-aggregation.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how `GROUP BY ... WITH ROLLUP` appears in an EXPLAIN plan and the note that valid execution plans for `WITH ROLLUP` are currently generated only in TiFlash MPP mode.
- Retrieval Keywords: WITH ROLLUP, GROUP BY year, month WITH ROLLUP, grouping(year), grouping(month), TiFlash MPP mode, HashAgg_36, Expand_20, ExchangeSender_21, ExchangeReceiver_22, MppVersion: 2, mpp[tiflash], multidimensional data aggregation with ROLLUP, Cube syntax, group by modifiers
- Follow-up Guidance: The content also states that the aggregation results for `GROUP BY year, month WITH ROLLUP` are calculated and concatenated in three groups: `{year, month}`, `{year}`, and `{}`.
- Classification Note: This is reference content because it documents the EXPLAIN output and support note for `WITH ROLLUP`, including TiFlash MPP operators such as `Expand`, `HashAgg`, and `ExchangeSender`.

## Official Source Content

## Multidimensional data aggregation with ROLLUP

Starting from v7.4.0, the `GROUP BY` clause of TiDB supports the `WITH ROLLUP` modifier.

In the `GROUP BY` clause, you can specify one or more columns as a group list and append the `WITH ROLLUP` modifier after the list. Then, TiDB will conduct multidimensional descending grouping based on the columns in the group list and provide you with summary results for each group in the output.

> **Note:**
>
> Currently, TiDB does not support the Cube syntax, and TiDB supports generating valid execution plans for the `WITH ROLLUP` syntax only in TiFlash MPP mode.

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

According to the `GROUP BY year, month WITH ROLLUP` syntax in the preceding statement, the SQL aggregation results for this statement can be calculated and concatenated in three groups: `{year, month}`, `{year}`, and `{}` respectively.

For more information, see [GROUP BY modifiers](https://docs.pingcap.com/tidb/stable/functions-and-operators/group-by-modifier).
