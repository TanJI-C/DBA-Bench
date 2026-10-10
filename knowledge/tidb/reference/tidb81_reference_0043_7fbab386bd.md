# Multi-valued index supported scenarios EXPLAIN examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/choose-index.md`
- Source Title: `Index Selection`
- Source Heading Path: `Index Selection > Use multi-valued indexes > Supported scenarios`
- Source Line Ranges: `205-247`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `multi-valued-indexes`, `index-merge`, `explain`, `json`, `member-of`, `json-contains`, `json-overlaps`, `range-scan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0043_7fbab386bd`
- Source ID: `tidb-docs-8.1:choose-index.md#supported-scenarios`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `708dc0a307e4aea15d231e27b056b367b61d799c2fcb649b199308605901c050`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/choose-index#supported-scenarios
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/choose-index.md

## Retrieval Guidance

- Use When: Use this chunk when looking for EXPLAIN examples that show how multi-valued indexes participate in IndexMerge plans for MEMBER OF, JSON_CONTAINS, JSON_OVERLAPS, and combined predicates on t2.
- Retrieval Keywords: multi-valued index supported scenarios, EXPLAIN SELECT /*+ use_index_merge(t2, idx) */, EXPLAIN SELECT /*+ use_index_merge(t2, idx, idx2) */, IndexMerge_7, IndexMerge_9, IndexMerge_10, type: union, type: intersection, 1 MEMBER OF (j->'$.path'), JSON_CONTAINS((j->'$.path'), '[1, 2, 3]'), JSON_OVERLAPS((j->'$.path'), '[1, 2, 3]'), IndexRangeScan, TableRowIDScan, table:t2, index:idx(a, cast(json_extract(`j`, _utf8'$.path') as signed array), b), table:t2, index:idx2(b, cast(json_extract(`k`, _utf8'$.path') as signed array)), range:[1 1 2,1 1 2], range:[1 1,1 1], range:[1 2,1 2], range:[1 3,1 3], Selection_5 json_overlaps
- Follow-up Guidance: The examples distinguish union and intersection IndexMerge plans and show that the JSON_OVERLAPS example includes a root Selection above IndexMerge.
- Classification Note: This is reference content because it consists of concrete EXPLAIN outputs and exact SQL examples for supported multi-valued index scenarios.

## Official Source Content

```sql
> EXPLAIN SELECT /*+ use_index_merge(t2, idx) */ * FROM t2 WHERE a=1 AND (1 MEMBER OF (j->'$.path')) AND b=2;
+-------------------------------+---------+-----------+-----------------------------------------------------------------------------------+-----------------------------------------------------+
| id                            | estRows | task      | access object                                                                     | operator info                                       |
+-------------------------------+---------+-----------+-----------------------------------------------------------------------------------+-----------------------------------------------------+
| IndexMerge_7                  | 0.00    | root      |                                                                                   | type: union                                         |
| ├─IndexRangeScan_5(Build)     | 0.00    | cop[tikv] | table:t2, index:idx(a, cast(json_extract(`j`, _utf8'$.path') as signed array), b) | range:[1 1 2,1 1 2], keep order:false, stats:pseudo |
| └─TableRowIDScan_6(Probe)     | 0.00    | cop[tikv] | table:t2                                                                          | keep order:false, stats:pseudo                      |
+-------------------------------+---------+-----------+-----------------------------------------------------------------------------------+-----------------------------------------------------+

> EXPLAIN SELECT /*+ use_index_merge(t2, idx) */ * FROM t2 WHERE a=1 AND JSON_CONTAINS((j->'$.path'), '[1, 2, 3]');
+-------------------------------+---------+-----------+-----------------------------------------------------------------------------------+-------------------------------------------------+
| id                            | estRows | task      | access object                                                                     | operator info                                   |
+-------------------------------+---------+-----------+-----------------------------------------------------------------------------------+-------------------------------------------------+
| IndexMerge_9                  | 0.00    | root      |                                                                                   | type: intersection                              |
| ├─IndexRangeScan_5(Build)     | 0.10    | cop[tikv] | table:t2, index:idx(a, cast(json_extract(`j`, _utf8'$.path') as signed array), b) | range:[1 1,1 1], keep order:false, stats:pseudo |
| ├─IndexRangeScan_6(Build)     | 0.10    | cop[tikv] | table:t2, index:idx(a, cast(json_extract(`j`, _utf8'$.path') as signed array), b) | range:[1 2,1 2], keep order:false, stats:pseudo |
| ├─IndexRangeScan_7(Build)     | 0.10    | cop[tikv] | table:t2, index:idx(a, cast(json_extract(`j`, _utf8'$.path') as signed array), b) | range:[1 3,1 3], keep order:false, stats:pseudo |
| └─TableRowIDScan_8(Probe)     | 0.00    | cop[tikv] | table:t2                                                                          | keep order:false, stats:pseudo                  |
+-------------------------------+---------+-----------+-----------------------------------------------------------------------------------+-------------------------------------------------+

> EXPLAIN SELECT /*+ use_index_merge(t2, idx) */ * FROM t2 WHERE a=1 AND JSON_OVERLAPS((j->'$.path'), '[1, 2, 3]');
+---------------------------------+---------+-----------+-----------------------------------------------------------------------------------+----------------------------------------------------------------------------------+
| id                              | estRows | task      | access object                                                                     | operator info                                                                    |
+---------------------------------+---------+-----------+-----------------------------------------------------------------------------------+----------------------------------------------------------------------------------+
| Selection_5                     | 0.24    | root      |                                                                                   | json_overlaps(json_extract(test.t2.j, "$.path"), cast("[1, 2, 3]", json BINARY)) |
| └─IndexMerge_10                 | 0.30    | root      |                                                                                   | type: union                                                                      |
|   ├─IndexRangeScan_6(Build)     | 0.10    | cop[tikv] | table:t2, index:idx(a, cast(json_extract(`j`, _utf8'$.path') as signed array), b) | range:[1 1,1 1], keep order:false, stats:pseudo                                  |
|   ├─IndexRangeScan_7(Build)     | 0.10    | cop[tikv] | table:t2, index:idx(a, cast(json_extract(`j`, _utf8'$.path') as signed array), b) | range:[1 2,1 2], keep order:false, stats:pseudo                                  |
|   ├─IndexRangeScan_8(Build)     | 0.10    | cop[tikv] | table:t2, index:idx(a, cast(json_extract(`j`, _utf8'$.path') as signed array), b) | range:[1 3,1 3], keep order:false, stats:pseudo                                  |
|   └─TableRowIDScan_9(Probe)     | 0.30    | cop[tikv] | table:t2                                                                          | keep order:false, stats:pseudo                                                   |
+---------------------------------+---------+-----------+-----------------------------------------------------------------------------------+----------------------------------------------------------------------------------+

> EXPLAIN SELECT /*+ use_index_merge(t2, idx, idx2) */ * FROM t2 WHERE (a=1 AND 1 member of (j->'$.path')) AND (b=1 AND 2 member of (k->'$.path'));
+-------------------------------+---------+-----------+-----------------------------------------------------------------------------------+-----------------------------------------------------+
| id                            | estRows | task      | access object                                                                     | operator info                                       |
+-------------------------------+---------+-----------+-----------------------------------------------------------------------------------+-----------------------------------------------------+
| IndexMerge_8                  | 0.00    | root      |                                                                                   | type: intersection                                  |
| ├─IndexRangeScan_5(Build)     | 0.00    | cop[tikv] | table:t2, index:idx(a, cast(json_extract(`j`, _utf8'$.path') as signed array), b) | range:[1 1 1,1 1 1], keep order:false, stats:pseudo |
| ├─IndexRangeScan_6(Build)     | 0.10    | cop[tikv] | table:t2, index:idx2(b, cast(json_extract(`k`, _utf8'$.path') as signed array))   | range:[1 2,1 2], keep order:false, stats:pseudo     |
| └─TableRowIDScan_7(Probe)     | 0.00    | cop[tikv] | table:t2                                                                          | keep order:false, stats:pseudo                      |
+-------------------------------+---------+-----------+-----------------------------------------------------------------------------------+-----------------------------------------------------+
```
