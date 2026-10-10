# IndexReader covering index example

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-indexes.md`
- Source Title: `Explain Statements That Use Indexes`
- Source Heading Path: `Explain Statements That Use Indexes > IndexReader`
- Source Line Ranges: `141-173`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `indexreader`, `covering index`, `indexrangescan`, `projection`, `rowid`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0251_b45e767469`
- Source ID: `tidb-docs-8.1:explain-indexes.md#indexreader`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `90ddc86d6a979adb640c9e8dffd8d79c14cba59ff4547dd10c0feab195c94d6c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-indexes#indexreader
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-indexes.md

## Retrieval Guidance

- Use When: Use this chunk when identifying a covering index optimization in EXPLAIN output and distinguishing IndexReader from IndexLookUp for queries on intkey that return id.
- Retrieval Keywords: IndexReader, covering index optimization, IndexLookUp_10, IndexReader_6, IndexRangeScan_5, Projection_4, EXPLAIN SELECT * FROM t1 WHERE intkey = 123, EXPLAIN SELECT id FROM t1 WHERE intkey = 123, range:[123,123], RowID, id, intkey
- Follow-up Guidance: The content explains that id is also the internal RowID, so after IndexRangeScan on intkey the RowID value can be returned directly.
- Classification Note: This is reference content because it documents EXPLAIN behavior for covering index optimization and the operator difference between IndexLookUp and IndexReader.

## Official Source Content

## IndexReader

TiDB supports the _covering index optimization_. If all rows can be retrieved from an index, TiDB will skip the second step that is usually required in an `IndexLookup`. Consider the following two examples:

```sql
EXPLAIN SELECT * FROM t1 WHERE intkey = 123;
EXPLAIN SELECT id FROM t1 WHERE intkey = 123;
```

```sql
+-------------------------------+---------+-----------+--------------------------------+-----------------------------------+
| id                            | estRows | task      | access object                  | operator info                     |
+-------------------------------+---------+-----------+--------------------------------+-----------------------------------+
| IndexLookUp_10                | 1.00    | root      |                                |                                   |
| ├─IndexRangeScan_8(Build)     | 1.00    | cop[tikv] | table:t1, index:intkey(intkey) | range:[123,123], keep order:false |
| └─TableRowIDScan_9(Probe)     | 1.00    | cop[tikv] | table:t1                       | keep order:false                  |
+-------------------------------+---------+-----------+--------------------------------+-----------------------------------+
3 rows in set (0.00 sec)

+--------------------------+---------+-----------+--------------------------------+-----------------------------------+
| id                       | estRows | task      | access object                  | operator info                     |
+--------------------------+---------+-----------+--------------------------------+-----------------------------------+
| Projection_4             | 1.00    | root      |                                | test.t1.id                        |
| └─IndexReader_6          | 1.00    | root      |                                | index:IndexRangeScan_5            |
|   └─IndexRangeScan_5     | 1.00    | cop[tikv] | table:t1, index:intkey(intkey) | range:[123,123], keep order:false |
+--------------------------+---------+-----------+--------------------------------+-----------------------------------+
3 rows in set (0.00 sec)
```

Because `id` is also the internal `RowID`, it is stored in the `intkey` index. After using the `intkey` index as part of `└─IndexRangeScan_5`, the value of the `RowID` can be returned directly.
