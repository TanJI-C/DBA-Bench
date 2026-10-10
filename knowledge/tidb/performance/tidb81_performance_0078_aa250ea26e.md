# Multi-valued indexes with IndexMerge supported scenarios

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/choose-index.md`
- Source Title: `Index Selection`
- Source Heading Path: `Index Selection > Use multi-valued indexes > Supported scenarios`
- Source Line Ranges: `248-293`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `indexmerge`, `multi-valued-indexes`, `json`, `member-of`, `json-contains`, `json-overlaps`, `explain`, `query-optimization`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0078_aa250ea26e`
- Source ID: `tidb-docs-8.1:choose-index.md#supported-scenarios`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d9c7161d8bb919672d6e0051d119baeaf3dafaf9d71057c330bf9ab6bbf8b9f0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/choose-index#supported-scenarios
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/choose-index.md

## Retrieval Guidance

- Use When: Use this when looking up how TiDB supports IndexMerge with multi-valued indexes and normal indexes for JSON predicates such as member of, json_contains, or json_overlaps connected by OR or AND.
- Retrieval Keywords: IndexMerge, multi-valued indexes, use_index_merge, member of, json_member_of, json_contains, json_overlaps, EXPLAIN, IndexRangeScan, TableRowIDScan, type: union, type: intersection, CAST(j1->'$.path' AS SIGNED ARRAY), CAST(j2->'$.path' AS SIGNED ARRAY), json_overlaps(j->'$.a', '[1, 2]') OR json_overlaps(j->'$.a', '[3, 4]'), SHOW WARNINGS
- Follow-up Guidance: For conditions connected with OR, each condition needs to be able to be accessed with IndexMerge respectively, and the examples include checking the plan with EXPLAIN and SHOW WARNINGS.
- Classification Note: This is classified as performance because the content explains optimizer index selection behavior and supported query optimization scenarios for IndexMerge on TiDB and TiKV.

## Official Source Content

TiDB can also use IndexMerge to access both multi-valued indexes and normal indexes. For example:

```sql
CREATE TABLE t3(j1 JSON, j2 JSON, a INT, INDEX k1((CAST(j1->'$.path' AS SIGNED ARRAY))), INDEX k2((CAST(j2->'$.path' AS SIGNED ARRAY))), INDEX ka(a));
EXPLAIN SELECT /*+ use_index_merge(t3, k1, k2, ka) */ * FROM t3 WHERE 1 member of (j1->'$.path') OR a = 3;
EXPLAIN SELECT /*+ use_index_merge(t3, k1, k2, ka) */ * FROM t3 WHERE 1 member of (j1->'$.path') AND 2 member of (j2->'$.path') AND (a = 3);
```

```sql
> EXPLAIN SELECT /*+ use_index_merge(t3, k1, k2, ka) */ * FROM t3 WHERE 1 member of (j1->'$.path') OR a = 3;
+-------------------------------+---------+-----------+-----------------------------------------------------------------------------+---------------------------------------------+
| id                            | estRows | task      | access object                                                               | operator info                               |
+-------------------------------+---------+-----------+-----------------------------------------------------------------------------+---------------------------------------------+
| IndexMerge_8                  | 19.99   | root      |                                                                             | type: union                                 |
| ├─IndexRangeScan_5(Build)     | 10.00   | cop[tikv] | table:t3, index:k1(cast(json_extract(`j1`, _utf8'$.path') as signed array)) | range:[1,1], keep order:false, stats:pseudo |
| ├─IndexRangeScan_6(Build)     | 10.00   | cop[tikv] | table:t3, index:ka(a)                                                       | range:[3,3], keep order:false, stats:pseudo |
| └─TableRowIDScan_7(Probe)     | 19.99   | cop[tikv] | table:t3                                                                    | keep order:false, stats:pseudo              |
+-------------------------------+---------+-----------+-----------------------------------------------------------------------------+---------------------------------------------+

> EXPLAIN SELECT /*+ use_index_merge(t3, k1, k2, ka) */ * FROM t3 WHERE 1 member of (j1->'$.path') AND 2 member of (j2->'$.path') AND (a = 3);
+-------------------------------+---------+-----------+-----------------------------------------------------------------------------+---------------------------------------------+
| id                            | estRows | task      | access object                                                               | operator info                               |
+-------------------------------+---------+-----------+-----------------------------------------------------------------------------+---------------------------------------------+
| IndexMerge_9                  | 0.00    | root      |                                                                             | type: intersection                          |
| ├─IndexRangeScan_5(Build)     | 10.00   | cop[tikv] | table:t3, index:ka(a)                                                       | range:[3,3], keep order:false, stats:pseudo |
| ├─IndexRangeScan_6(Build)     | 10.00   | cop[tikv] | table:t3, index:k1(cast(json_extract(`j1`, _utf8'$.path') as signed array)) | range:[1,1], keep order:false, stats:pseudo |
| ├─IndexRangeScan_7(Build)     | 10.00   | cop[tikv] | table:t3, index:k2(cast(json_extract(`j2`, _utf8'$.path') as signed array)) | range:[2,2], keep order:false, stats:pseudo |
| └─TableRowIDScan_8(Probe)     | 0.00    | cop[tikv] | table:t3                                                                    | keep order:false, stats:pseudo              |
+-------------------------------+---------+-----------+-----------------------------------------------------------------------------+---------------------------------------------+
```

If several `json_member_of`, `json_contains` or `json_overlaps` conditions are connected with `OR` or `AND`, they need to meet the following requirements to access multi-valued indexes with IndexMerge:

```sql
CREATE TABLE t4(a INT, j JSON, INDEX mvi1((CAST(j->'$.a' AS UNSIGNED ARRAY))), INDEX mvi2((CAST(j->'$.b' AS UNSIGNED ARRAY))));
```

- For conditions connected with `OR`, each of them needs to be able to be accessed with IndexMerge respectively. For example:

    ```sql
    EXPLAIN SELECT /*+ use_index_merge(t4, mvi1) */ * FROM t4 WHERE json_overlaps(j->'$.a', '[1, 2]') OR json_overlaps(j->'$.a', '[3, 4]');
    EXPLAIN SELECT /*+ use_index_merge(t4, mvi1) */ * FROM t4 WHERE json_overlaps(j->'$.a', '[1, 2]') OR json_length(j->'$.a') = 3;
    SHOW WARNINGS;
    ```
