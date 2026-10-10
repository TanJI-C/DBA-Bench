# IndexLookup and table row fetch

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-indexes.md`
- Source Title: `Explain Statements That Use Indexes`
- Source Heading Path: `Explain Statements That Use Indexes > IndexLookup`
- Source Line Ranges: `96-140`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `indexlookup`, `tablefullscan`, `indexfullscan`, `limit`, `rowid`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0250_bd503fb0db`
- Source ID: `tidb-docs-8.1:explain-indexes.md#indexlookup`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8834aea6dd8401c939d22fe4033f13fef5ceca692fd44fe75a6e7644d7db2a24`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-indexes#indexlookup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-indexes.md

## Retrieval Guidance

- Use When: Use this chunk when interpreting an EXPLAIN plan with IndexLookUp, IndexRangeScan, TableRowIDScan, TableFullScan, or LIMIT on an indexed column such as intkey.
- Retrieval Keywords: IndexLookUp, IndexRangeScan_8(Build), TableRowIDScan_9(Probe), TableFullScan_5, IndexFullScan_18, LIMIT, ORDER BY intkey DESC LIMIT 10, EXPLAIN SELECT * FROM t1 WHERE intkey > 100, EXPLAIN SELECT * FROM t1 ORDER BY intkey DESC LIMIT 10, RowID, intkey
- Follow-up Guidance: The content also notes that the SQL Optimizer might choose TableFullScan based on statistics when a large number of rows match.
- Classification Note: This is reference content because it explains how EXPLAIN operators IndexLookUp, TableFullScan, IndexFullScan, and TableRowIDScan appear and what they mean in query plans.

## Official Source Content

* The `├─IndexRangeScan_8(Build)` operator performs a range scan on the `intkey` index and retrieves the values of the internal `RowID` (for this table, the primary key).
* The `└─TableRowIDScan_9(Probe)` operator then retrieves the full row from the table data.

Because an `IndexLookup` task requires two steps, the SQL Optimizer might choose the `TableFullScan` operator based on [statistics](https://docs.pingcap.com/tidb/stable/statistics) in scenarios where a large number of rows match. In the following example, a large number of rows match the condition of `intkey > 100`, and a `TableFullScan` is chosen:

```sql
EXPLAIN SELECT * FROM t1 WHERE intkey > 100;
```

```sql
+-------------------------+---------+-----------+---------------+-------------------------+
| id                      | estRows | task      | access object | operator info           |
+-------------------------+---------+-----------+---------------+-------------------------+
| TableReader_7           | 898.50  | root      |               | data:Selection_6        |
| └─Selection_6           | 898.50  | cop[tikv] |               | gt(test.t1.intkey, 100) |
|   └─TableFullScan_5     | 1010.00 | cop[tikv] | table:t1      | keep order:false        |
+-------------------------+---------+-----------+---------------+-------------------------+
3 rows in set (0.00 sec)
```

The `IndexLookup` operator can also be used to efficiently optimize `LIMIT` on an indexed column:

```sql
EXPLAIN SELECT * FROM t1 ORDER BY intkey DESC LIMIT 10;
```

```sql
+--------------------------------+---------+-----------+--------------------------------+------------------------------------+
| id                             | estRows | task      | access object                  | operator info                      |
+--------------------------------+---------+-----------+--------------------------------+------------------------------------+
| IndexLookUp_21                 | 10.00   | root      |                                | limit embedded(offset:0, count:10) |
| ├─Limit_20(Build)              | 10.00   | cop[tikv] |                                | offset:0, count:10                 |
| │ └─IndexFullScan_18           | 10.00   | cop[tikv] | table:t1, index:intkey(intkey) | keep order:true, desc              |
| └─TableRowIDScan_19(Probe)     | 10.00   | cop[tikv] | table:t1                       | keep order:false, stats:pseudo     |
+--------------------------------+---------+-----------+--------------------------------+------------------------------------+
4 rows in set (0.00 sec)

```

In the above example, the last 10 rows are read from the index `intkey`. These `RowID` values are then retrieved from the table data.
