# Multi-valued index IndexMerge supported and unsupported conditions

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/choose-index.md`
- Source Title: `Index Selection`
- Source Heading Path: `Index Selection > Use multi-valued indexes > Supported scenarios`
- Source Line Ranges: `294-332`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `index-selection`, `multi-valued-indexes`, `indexmerge`, `json-overlaps`, `json-contains`, `explain`, `show-warnings`, `query-optimization`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0079_11dcdd86b6`
- Source ID: `tidb-docs-8.1:choose-index.md#supported-scenarios`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e1e8b225067296bffc69bd16733788b9974d56a8461cd56439dc8bdbe369fd8f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/choose-index#supported-scenarios
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/choose-index.md

## Retrieval Guidance

- Use When: Use this chunk when checking whether TiDB can use IndexMerge with a multi-valued index for JSON predicates combined with OR or AND, especially with EXPLAIN and SHOW WARNINGS output.
- Retrieval Keywords: multi-valued index, IndexMerge, use_index_merge(t4, mvi1), json_overlaps, json_contains, json_length, EXPLAIN SELECT, SHOW WARNINGS, IndexMerge is inapplicable, Warning 1105, Selection_5, IndexMerge_11, IndexRangeScan, TableFullScan, mvi1, cast(json_extract(`j`, _utf8'$.a') as unsigned array)
- Follow-up Guidance: The content shows that when a predicate such as json_length(j->'$.a') = 3 cannot be accessed with IndexMerge directly in an OR condition, EXPLAIN falls back to TableFullScan and SHOW WARNINGS returns "IndexMerge is inapplicable".
- Classification Note: This is classified as performance for TiDB because the official content explains index selection behavior and execution plan differences for multi-valued index IndexMerge queries on TiKV.

## Official Source Content

```sql
    > EXPLAIN SELECT /*+ use_index_merge(t4, mvi1) */ * FROM t4 WHERE json_overlaps(j->'$.a', '[1, 2]') OR json_overlaps(j->'$.a', '[3, 4]');
    +----------------------------------+---------+-----------+-----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | id                               | estRows | task      | access object                                                               | operator info                                                                                                                                              |
    +----------------------------------+---------+-----------+-----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Selection_5                      | 31.95   | root      |                                                                             | or(json_overlaps(json_extract(test.t4.j, "$.a"), cast("[1, 2]", json BINARY)), json_overlaps(json_extract(test.t4.j, "$.a"), cast("[3, 4]", json BINARY))) |
    | └─IndexMerge_11                  | 39.94   | root      |                                                                             | type: union                                                                                                                                                |
    |   ├─IndexRangeScan_6(Build)      | 10.00   | cop[tikv] | table:t4, index:mvi1(cast(json_extract(`j`, _utf8'$.a') as unsigned array)) | range:[1,1], keep order:false, stats:pseudo                                                                                                                |
    |   ├─IndexRangeScan_7(Build)      | 10.00   | cop[tikv] | table:t4, index:mvi1(cast(json_extract(`j`, _utf8'$.a') as unsigned array)) | range:[2,2], keep order:false, stats:pseudo                                                                                                                |
    |   ├─IndexRangeScan_8(Build)      | 10.00   | cop[tikv] | table:t4, index:mvi1(cast(json_extract(`j`, _utf8'$.a') as unsigned array)) | range:[3,3], keep order:false, stats:pseudo                                                                                                                |
    |   ├─IndexRangeScan_9(Build)      | 10.00   | cop[tikv] | table:t4, index:mvi1(cast(json_extract(`j`, _utf8'$.a') as unsigned array)) | range:[4,4], keep order:false, stats:pseudo                                                                                                                |
    |   └─TableRowIDScan_10(Probe)     | 39.94   | cop[tikv] | table:t4                                                                    | keep order:false, stats:pseudo                                                                                                                             |
    +----------------------------------+---------+-----------+-----------------------------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------+
    
    -- json_length(j->'$.a') = 3 cannot be accessed with IndexMerge directly, so TiDB cannot use IndexMerge for this SQL statement.
    > EXPLAIN SELECT /*+ use_index_merge(t4, mvi1) */ * FROM t4 WHERE json_overlaps(j->'$.a', '[1, 2]') OR json_length(j->'$.a') = 3;
    +-------------------------+----------+-----------+---------------+------------------------------------------------------------------------------------------------------------------------------------+
    | id                      | estRows  | task      | access object | operator info                                                                                                                      |
    +-------------------------+----------+-----------+---------------+------------------------------------------------------------------------------------------------------------------------------------+
    | Selection_5             | 8000.00  | root      |               | or(json_overlaps(json_extract(test.t4.j, "$.a"), cast("[1, 2]", json BINARY)), eq(json_length(json_extract(test.t4.j, "$.a")), 3)) |
    | └─TableReader_7         | 10000.00 | root      |               | data:TableFullScan_6                                                                                                               |
    |   └─TableFullScan_6     | 10000.00 | cop[tikv] | table:t4      | keep order:false, stats:pseudo                                                                                                     |
    +-------------------------+----------+-----------+---------------+------------------------------------------------------------------------------------------------------------------------------------+
    
    > SHOW WARNINGS;
    +---------+------+----------------------------+
    | Level   | Code | Message                    |
    +---------+------+----------------------------+
    | Warning | 1105 | IndexMerge is inapplicable |
    +---------+------+----------------------------+
    ```

- For conditions connected with `AND`, some of them need to be able to be accessed with IndexMerge respectively. TiDB can only use IndexMerge to access multi-valued indexes with these conditions. For example:

    ```sql
    EXPLAIN SELECT /*+ use_index_merge(t4, mvi1) */ * FROM t4 WHERE json_contains(j->'$.a', '[1, 2]') AND json_contains(j->'$.a', '[3, 4]');
    EXPLAIN SELECT /*+ use_index_merge(t4, mvi1) */ * FROM t4 WHERE json_contains(j->'$.a', '[1, 2]') AND json_contains(j->'$.a', '[3, 4]') AND json_length(j->'$.a') = 2;
    ```
