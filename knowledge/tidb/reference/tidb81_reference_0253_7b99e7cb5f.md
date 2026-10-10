# IndexFullScan plans for MIN, MAX, and full index scans

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-indexes.md`
- Source Title: `Explain Statements That Use Indexes`
- Source Heading Path: `Explain Statements That Use Indexes > IndexFullScan`
- Source Line Ranges: `229-296`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `explain`, `execution-plan`, `indexfullscan`, `min`, `max`, `tablefullscan`, `topn`, `stream-aggregation`, `indexreader`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0253_7b99e7cb5f`
- Source ID: `tidb-docs-8.1:explain-indexes.md#indexfullscan`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3bbe72781ac4f819c00d222179bafc5100001e02759ca7543fc2f8d7bee290ee`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-indexes#indexfullscan
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-indexes.md

## Retrieval Guidance

- Use When: Use this chunk when interpreting EXPLAIN output for MIN, MAX, SUM, or AVG queries and you need to understand why TiDB shows IndexFullScan versus TableFullScan on indexed or unindexed columns.
- Retrieval Keywords: IndexFullScan, EXPLAIN SELECT MIN(intkey) FROM t1;, EXPLAIN SELECT MAX(intkey) FROM t1;, EXPLAIN SELECT MIN(pad1) FROM t1;, EXPLAIN SELECT SUM(intkey) FROM t1;, EXPLAIN SELECT AVG(intkey) FROM t1;, StreamAgg, IndexReader, Limit, TopN, TableFullScan, keep order:true, desc, table:t1, index:intkey(intkey), not(isnull(test.t1.pad1))
- Follow-up Guidance: The content also shows that SUM(intkey) and AVG(intkey) use the IndexFullScan operator to scan every row in the index.
- Classification Note: This is reference content because it explains the meaning of specific EXPLAIN operators and plan shapes, including IndexFullScan, TableFullScan, StreamAgg, TopN, and IndexReader, with concrete SQL examples.

## Official Source Content

## IndexFullScan

Because indexes are ordered, the `IndexFullScan` operator can be used to optimize common queries such as the `MIN` or `MAX` values for an indexed value:

```sql
EXPLAIN SELECT MIN(intkey) FROM t1;
EXPLAIN SELECT MAX(intkey) FROM t1;
```

```sql
+------------------------------+---------+-----------+--------------------------------+-------------------------------------+
| id                           | estRows | task      | access object                  | operator info                       |
+------------------------------+---------+-----------+--------------------------------+-------------------------------------+
| StreamAgg_12                 | 1.00    | root      |                                | funcs:min(test.t1.intkey)->Column#4 |
| └─Limit_16                   | 1.00    | root      |                                | offset:0, count:1                   |
|   └─IndexReader_29           | 1.00    | root      |                                | index:Limit_28                      |
|     └─Limit_28               | 1.00    | cop[tikv] |                                | offset:0, count:1                   |
|       └─IndexFullScan_27     | 1.00    | cop[tikv] | table:t1, index:intkey(intkey) | keep order:true                     |
+------------------------------+---------+-----------+--------------------------------+-------------------------------------+
5 rows in set (0.00 sec)

+------------------------------+---------+-----------+--------------------------------+-------------------------------------+
| id                           | estRows | task      | access object                  | operator info                       |
+------------------------------+---------+-----------+--------------------------------+-------------------------------------+
| StreamAgg_12                 | 1.00    | root      |                                | funcs:max(test.t1.intkey)->Column#4 |
| └─Limit_16                   | 1.00    | root      |                                | offset:0, count:1                   |
|   └─IndexReader_29           | 1.00    | root      |                                | index:Limit_28                      |
|     └─Limit_28               | 1.00    | cop[tikv] |                                | offset:0, count:1                   |
|       └─IndexFullScan_27     | 1.00    | cop[tikv] | table:t1, index:intkey(intkey) | keep order:true, desc               |
+------------------------------+---------+-----------+--------------------------------+-------------------------------------+
5 rows in set (0.00 sec)
```

In the above statements, an `IndexFullScan` task is performed on each TiKV Region. Despite the name `FullScan`, only the first row needs to be read (`└─Limit_28`). Each TiKV Region returns its `MIN` or `MAX` value to TiDB, which then performs Stream Aggregation to filter for a single row. Stream Aggregation with the aggregation function `MAX` or `MIN` also ensures that `NULL` is returned if the table is empty.

By contrast, executing the `MIN` function on an unindexed value will result in `TableFullScan`. The query will require all rows to be scanned in TiKV, but a `TopN` calculation is performed to ensure each TiKV Region only returns one row to TiDB. Although `TopN` prevents excessive rows from being transferred between TiKV and TiDB, this statement is still considered far less efficient than the above example where `MIN` is able to make use of an index.

```sql
EXPLAIN SELECT MIN(pad1) FROM t1;
```

```sql
+--------------------------------+---------+-----------+---------------+-----------------------------------+
| id                             | estRows | task      | access object | operator info                     |
+--------------------------------+---------+-----------+---------------+-----------------------------------+
| StreamAgg_13                   | 1.00    | root      |               | funcs:min(test.t1.pad1)->Column#4 |
| └─TopN_14                      | 1.00    | root      |               | test.t1.pad1, offset:0, count:1   |
|   └─TableReader_23             | 1.00    | root      |               | data:TopN_22                      |
|     └─TopN_22                  | 1.00    | cop[tikv] |               | test.t1.pad1, offset:0, count:1   |
|       └─Selection_21           | 1008.99 | cop[tikv] |               | not(isnull(test.t1.pad1))         |
|         └─TableFullScan_20     | 1010.00 | cop[tikv] | table:t1      | keep order:false                  |
+--------------------------------+---------+-----------+---------------+-----------------------------------+
6 rows in set (0.00 sec)
```

The following statements will use the `IndexFullScan` operator to scan every row in the index:

```sql
EXPLAIN SELECT SUM(intkey) FROM t1;
EXPLAIN SELECT AVG(intkey) FROM t1;
```
