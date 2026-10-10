# Multi-valued index supported scenarios with IndexMerge examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/choose-index.md`
- Source Title: `Index Selection`
- Source Heading Path: `Index Selection > Use multi-valued indexes > Supported scenarios`
- Source Line Ranges: `405-436`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `multi-valued-indexes`, `indexmerge`, `json_overlaps`, `json_member_of`, `explain`, `query-plans`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0046_8a9642baec`
- Source ID: `tidb-docs-8.1:choose-index.md#supported-scenarios`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `73004550d931c8513532f7b3ff276e85520f727fa7cbf04d1191c4e98fe6e613`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/choose-index#supported-scenarios
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/choose-index.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how TiDB uses multi-valued indexes with IndexMerge for JSON predicates such as json_overlaps and member of, including EXPLAIN plans and cases where only part of the conditions match the semantics.
- Retrieval Keywords: multi-valued indexes, IndexMerge, use_index_merge(t4, mvi1, mvi2), json_overlaps, json_member_of, member of, EXPLAIN SELECT, Selection_5, IndexMerge_10, IndexRangeScan, TableRowIDScan, mvi1, mvi2, cast(json_extract(`j`, _utf8'$.a') as unsigned array), cast(json_extract(`j`, _utf8'$.b') as unsigned array), type: union, The conditions do not match the semantics, TiDB can only use IndexMerge for part of the conditions
- Follow-up Guidance: The chunk also shows example EXPLAIN statements for `1 member of (j->'$.a') AND 2 member of (j->'$.b') AND 3 member of (j->'$.a')` and the corresponding `OR` form.
- Classification Note: This is reference content because it documents supported scenarios, exact SQL examples, and EXPLAIN operator details for multi-valued index and IndexMerge behavior in TiDB.

## Official Source Content

| Selection_5                     | 23.98   | root      |                                                                             | or(json_overlaps(json_extract(test.t4.j, "$.a"), cast("[1]", json BINARY)), json_overlaps(json_extract(test.t4.j, "$.b"), cast("[2, 3]", json BINARY))) |
        | └─IndexMerge_10                 | 29.97   | root      |                                                                             | type: union                                                                                                                                             |
        |   ├─IndexRangeScan_6(Build)     | 10.00   | cop[tikv] | table:t4, index:mvi1(cast(json_extract(`j`, _utf8'$.a') as unsigned array)) | range:[1,1], keep order:false, stats:pseudo                                                                                                             |
        |   ├─IndexRangeScan_7(Build)     | 10.00   | cop[tikv] | table:t4, index:mvi2(cast(json_extract(`j`, _utf8'$.b') as unsigned array)) | range:[2,2], keep order:false, stats:pseudo                                                                                                             |
        |   ├─IndexRangeScan_8(Build)     | 10.00   | cop[tikv] | table:t4, index:mvi2(cast(json_extract(`j`, _utf8'$.b') as unsigned array)) | range:[3,3], keep order:false, stats:pseudo                                                                                                             |
        |   └─TableRowIDScan_9(Probe)     | 29.97   | cop[tikv] | table:t4                                                                    | keep order:false, stats:pseudo                                                                                                                          |
        +---------------------------------+---------+-----------+-----------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        
        -- The conditions do not match the semantics, so TiDB can only use IndexMerge for part of the conditions of this SQL statement as explained above.
        > EXPLAIN SELECT /*+ use_index_merge(t4, mvi1, mvi2) */ * FROM t4 WHERE json_overlaps(j->'$.a', '[1]') AND json_overlaps(j->'$.b', '[2, 3]');
        +---------------------------------+---------+-----------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------+
        | id                              | estRows | task      | access object                                                               | operator info                                                                                                                                       |
        +---------------------------------+---------+-----------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------+
        | Selection_5                     | 15.99   | root      |                                                                             | json_overlaps(json_extract(test.t4.j, "$.a"), cast("[1]", json BINARY)), json_overlaps(json_extract(test.t4.j, "$.b"), cast("[2, 3]", json BINARY)) |
        | └─IndexMerge_8                  | 10.00   | root      |                                                                             | type: union                                                                                                                                         |
        |   ├─IndexRangeScan_6(Build)     | 10.00   | cop[tikv] | table:t4, index:mvi1(cast(json_extract(`j`, _utf8'$.a') as unsigned array)) | range:[1,1], keep order:false, stats:pseudo                                                                                                         |
        |   └─TableRowIDScan_7(Probe)     | 10.00   | cop[tikv] | table:t4                                                                    | keep order:false, stats:pseudo                                                                                                                      |
        +---------------------------------+---------+-----------+-----------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------+
        ```

    - If `json_member_of` is connected with `OR` or `AND`, it matches the semantics. For example:
        
        ```sql
        EXPLAIN SELECT /*+ use_index_merge(t4, mvi1, mvi2) */ * FROM t4 WHERE 1 member of (j->'$.a') AND 2 member of (j->'$.b') AND 3 member of (j->'$.a');
        EXPLAIN SELECT /*+ use_index_merge(t4, mvi1, mvi2) */ * FROM t4 WHERE 1 member of (j->'$.a') OR 2 member of (j->'$.b') OR 3 member of (j->'$.a');
        ```

        ```sql
        > EXPLAIN SELECT /*+ use_index_merge(t4, mvi1, mvi2) */ * FROM t4 WHERE 1 member of (j->'$.a') AND 2 member of (j->'$.b') AND 3 member of (j->'$.a');
        +-------------------------------+---------+-----------+-----------------------------------------------------------------------------+---------------------------------------------+
        | id                            | estRows | task      | access object                                                               | operator info                               |
        +-------------------------------+---------+-----------+-----------------------------------------------------------------------------+---------------------------------------------+
