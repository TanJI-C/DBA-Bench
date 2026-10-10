# Multi-valued indexes supported scenarios with nested OR/AND and IndexMerge examples

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/choose-index.md`
- Source Title: `Index Selection`
- Source Heading Path: `Index Selection > Use multi-valued indexes > Supported scenarios`
- Source Line Ranges: `505-534`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `index-selection`, `multi-valued-indexes`, `indexmerge`, `query-plans`, `or-and-conditions`, `explain`, `json`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0080_d60f9c5f34`
- Source ID: `tidb-docs-8.1:choose-index.md#supported-scenarios`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `127bcf1268c3e1d413b45db04c15015b2953ea767df8b32a8d9b4434dda80532`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/choose-index#supported-scenarios
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/choose-index.md

## Retrieval Guidance

- Use When: Use this chunk when checking whether TiDB can use IndexMerge with multi-valued indexes for queries that have nested OR/AND conditions and MEMBER OF predicates on JSON arrays.
- Retrieval Keywords: IndexMerge, multi-valued indexes, nested OR/AND, MEMBER OF, json_extract, use_index_merge, EXPLAIN SELECT, IndexRangeScan, TableRowIDScan, Selection_8(Probe), t4, mvi1, mvi2, t5, t6, multi-column index, CAST(j AS SIGNED ARRAY), CAST(k as SIGNED ARRAY)
- Follow-up Guidance: The content notes that TiDB might not be able to use IndexMerge or fully use all conditions after transformations such as expansion, and recommends verifying each specific case with examples like EXPLAIN SELECT /*+ use_index_merge(t5, idx, idx2) */ * FROM t5 WHERE (a=1 AND 1 member of (j)) OR (b=2 AND 2 member of (k));
- Classification Note: This is classified as performance for TiDB because it explains index selection behavior and EXPLAIN plan patterns for IndexMerge with multi-valued indexes in SQL queries.

## Official Source Content

+-------------------------------+---------+-----------+-----------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        -- Only 1 member of (j->'$.a') and 2 member of (j->'$.a') that match the semantics of OR constitute the IndexMerge. 2 member of (j->'$.b') that matches the semantics of AND is not included.
        > EXPLAIN SELECT /*+ use_index_merge(t4, mvi1, mvi2) */ * FROM t4 WHERE 1 member of (j->'$.a') OR (2 member of (j->'$.b') AND 3 member of (j->'$.a'));
        +-------------------------------+---------+-----------+-----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | id                            | estRows | task      | access object                                                               | operator info                                                                                                                                                                                                          |
        +-------------------------------+---------+-----------+-----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | IndexMerge_9                  | 0.02    | root      |                                                                             | type: union                                                                                                                                                                                                            |
        | ├─IndexRangeScan_5(Build)     | 10.00   | cop[tikv] | table:t4, index:mvi1(cast(json_extract(`j`, _utf8'$.a') as unsigned array)) | range:[1,1], keep order:false, stats:pseudo                                                                                                                                                                            |
        | ├─IndexRangeScan_6(Build)     | 10.00   | cop[tikv] | table:t4, index:mvi1(cast(json_extract(`j`, _utf8'$.a') as unsigned array)) | range:[3,3], keep order:false, stats:pseudo                                                                                                                                                                            |
        | └─Selection_8(Probe)          | 0.02    | cop[tikv] |                                                                             | or(json_memberof(cast(1, json BINARY), json_extract(test.t4.j, "$.a")), and(json_memberof(cast(2, json BINARY), json_extract(test.t4.j, "$.b")), json_memberof(cast(3, json BINARY), json_extract(test.t4.j, "$.a")))) |
        |   └─TableRowIDScan_7          | 19.99   | cop[tikv] | table:t4                                                                    | keep order:false, stats:pseudo                                                                                                                                                                                         |
        +-------------------------------+---------+-----------+-----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        ```

If conditions contain nested `OR`/`AND`, or if conditions correspond to only indexed columns after transformations, such as expansion, TiDB might not be able to use IndexMerge or make full use of all conditions. It is recommended to verify the behavior of each specific case.

The following are some examples:

```sql
CREATE TABLE t5 (a INT, j JSON, b INT, k JSON, INDEX idx(a, (CAST(j AS SIGNED ARRAY))), INDEX idx2(b, (CAST(k as SIGNED ARRAY))));
CREATE TABLE t6 (a INT, j JSON, b INT, k JSON, INDEX idx(a, (CAST(j AS SIGNED ARRAY)), b), INDEX idx2(a, (CAST(k as SIGNED ARRAY)), b));
```

If `AND` is nested in conditions connected by `OR` and subconditions connected by `AND` correspond to the exact columns of a multi-column index, TiDB can usually make full use of the conditions. For example:

```sql
EXPLAIN SELECT /*+ use_index_merge(t5, idx, idx2) */ * FROM t5 WHERE (a=1 AND 1 member of (j)) OR (b=2 AND 2 member of (k));
```
