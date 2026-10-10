# IndexFullScan explain examples and limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-indexes.md`
- Source Title: `Explain Statements That Use Indexes`
- Source Heading Path: `Explain Statements That Use Indexes > IndexFullScan`
- Source Line Ranges: `297-340`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tikv`
- Topic Tags: `explain`, `indexes`, `indexfullscan`, `tablefullscan`, `indexreader`, `streamagg`, `query-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0254_5bd55c6f6f`
- Source ID: `tidb-docs-8.1:explain-indexes.md#indexfullscan`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b7c78d6f34997498c55cf45cd74db28dabc7405f9f7a71028ea89e71686cf039`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-indexes#indexfullscan
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-indexes.md

## Retrieval Guidance

- Use When: Use this chunk when interpreting EXPLAIN output that shows IndexFullScan versus TableFullScan for aggregate queries on an indexed column and understanding why IndexFullScan might not be used.
- Retrieval Keywords: IndexFullScan, TableFullScan, EXPLAIN, IndexReader, StreamAgg, cop[tikv], table:t1, index:intkey(intkey), keep order:false, AVG(intkey), SUM(intkey), ANY_VALUE(pad1), EXPLAIN SELECT AVG(intkey), ANY_VALUE(pad1) FROM t1;, width of the value in the (intkey + RowID) index, additional columns are required from the table
- Follow-up Guidance: The source also shows that when additional columns such as `pad1` are needed, the plan uses `TableReader`, `StreamAgg`, and `TableFullScan` instead of `IndexFullScan`.
- Classification Note: This is reference content because it provides concrete EXPLAIN plan examples, operator names, and the stated limitation that `IndexFullScan` is not supported when extra table columns are required.

## Official Source Content

```sql
+----------------------------+---------+-----------+--------------------------------+-------------------------------------+
| id                         | estRows | task      | access object                  | operator info                       |
+----------------------------+---------+-----------+--------------------------------+-------------------------------------+
| StreamAgg_20               | 1.00    | root      |                                | funcs:sum(Column#6)->Column#4       |
| └─IndexReader_21           | 1.00    | root      |                                | index:StreamAgg_8                   |
|   └─StreamAgg_8            | 1.00    | cop[tikv] |                                | funcs:sum(test.t1.intkey)->Column#6 |
|     └─IndexFullScan_19     | 1010.00 | cop[tikv] | table:t1, index:intkey(intkey) | keep order:false                    |
+----------------------------+---------+-----------+--------------------------------+-------------------------------------+
4 rows in set (0.00 sec)

+----------------------------+---------+-----------+--------------------------------+----------------------------------------------------------------------------+
| id                         | estRows | task      | access object                  | operator info                                                              |
+----------------------------+---------+-----------+--------------------------------+----------------------------------------------------------------------------+
| StreamAgg_20               | 1.00    | root      |                                | funcs:avg(Column#7, Column#8)->Column#4                                    |
| └─IndexReader_21           | 1.00    | root      |                                | index:StreamAgg_8                                                          |
|   └─StreamAgg_8            | 1.00    | cop[tikv] |                                | funcs:count(test.t1.intkey)->Column#7, funcs:sum(test.t1.intkey)->Column#8 |
|     └─IndexFullScan_19     | 1010.00 | cop[tikv] | table:t1, index:intkey(intkey) | keep order:false                                                           |
+----------------------------+---------+-----------+--------------------------------+----------------------------------------------------------------------------+
4 rows in set (0.00 sec)
```

In the above examples, `IndexFullScan` is more efficient than `TableFullScan` because the width of the value in the `(intkey + RowID)` index is less than the width of the full row.

The following statement does not support using an `IndexFullScan` operator because additional columns are required from the table:

```sql
EXPLAIN SELECT AVG(intkey), ANY_VALUE(pad1) FROM t1;
```

```sql
+------------------------------+---------+-----------+---------------+-----------------------------------------------------------------------------------------------------------------------+
| id                           | estRows | task      | access object | operator info                                                                                                         |
+------------------------------+---------+-----------+---------------+-----------------------------------------------------------------------------------------------------------------------+
| Projection_4                 | 1.00    | root      |               | Column#4, any_value(test.t1.pad1)->Column#5                                                                           |
| └─StreamAgg_16               | 1.00    | root      |               | funcs:avg(Column#10, Column#11)->Column#4, funcs:firstrow(Column#12)->test.t1.pad1                                    |
|   └─TableReader_17           | 1.00    | root      |               | data:StreamAgg_8                                                                                                      |
|     └─StreamAgg_8            | 1.00    | cop[tikv] |               | funcs:count(test.t1.intkey)->Column#10, funcs:sum(test.t1.intkey)->Column#11, funcs:firstrow(test.t1.pad1)->Column#12 |
|       └─TableFullScan_15     | 1010.00 | cop[tikv] | table:t1      | keep order:false                                                                                                      |
+------------------------------+---------+-----------+---------------+-----------------------------------------------------------------------------------------------------------------------+
5 rows in set (0.00 sec)
```
