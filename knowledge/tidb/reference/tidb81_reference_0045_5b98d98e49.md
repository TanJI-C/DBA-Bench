# Multi-valued index supported scenarios with IndexMerge semantics examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/choose-index.md`
- Source Title: `Index Selection`
- Source Heading Path: `Index Selection > Use multi-valued indexes > Supported scenarios`
- Source Line Ranges: `374-404`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `index-selection`, `multi-valued-indexes`, `indexmerge`, `json_contains`, `json_overlaps`, `explain-plans`, `supported-scenarios`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0045_5b98d98e49`
- Source ID: `tidb-docs-8.1:choose-index.md#supported-scenarios`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f077d6ecde5ba23f324c314bf255885a95d8f29cd875589fac8a73f8683c5e65`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/choose-index#supported-scenarios
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/choose-index.md

## Retrieval Guidance

- Use When: Use this chunk when checking whether multi-valued indexes can be used with IndexMerge for JSON predicates involving json_contains or json_overlaps and interpreting the EXPLAIN output.
- Retrieval Keywords: multi-valued index, IndexMerge, use_index_merge(t4, mvi1, mvi2), json_contains, json_overlaps, EXPLAIN SELECT, IndexMerge_9, IndexRangeScan_5(Build), IndexRangeScan_6(Build), IndexRangeScan_7(Build), TableRowIDScan_8(Probe), TableFullScan_5, Selection_6, type: intersection, cast(json_extract(`j`, _utf8'$.a') as unsigned array), cast(json_extract(`j`, _utf8'$.b') as unsigned array), OR semantics, AND semantics, supported scenarios
- Follow-up Guidance: The chunk contrasts a case where TiDB cannot use IndexMerge because the conditions do not match the semantics with examples showing json_overlaps connected by OR or AND in EXPLAIN statements.
- Classification Note: This is reference content because it documents supported multi-valued index scenarios and shows exact EXPLAIN plan patterns for IndexMerge semantics.

## Official Source Content

+-------------------------------+---------+-----------+-----------------------------------------------------------------------------+---------------------------------------------+
        | IndexMerge_9                  | 0.00    | root      |                                                                             | type: intersection                          |
        | ├─IndexRangeScan_5(Build)     | 10.00   | cop[tikv] | table:t4, index:mvi1(cast(json_extract(`j`, _utf8'$.a') as unsigned array)) | range:[1,1], keep order:false, stats:pseudo |
        | ├─IndexRangeScan_6(Build)     | 10.00   | cop[tikv] | table:t4, index:mvi2(cast(json_extract(`j`, _utf8'$.b') as unsigned array)) | range:[2,2], keep order:false, stats:pseudo |
        | ├─IndexRangeScan_7(Build)     | 10.00   | cop[tikv] | table:t4, index:mvi2(cast(json_extract(`j`, _utf8'$.b') as unsigned array)) | range:[3,3], keep order:false, stats:pseudo |
        | └─TableRowIDScan_8(Probe)     | 0.00    | cop[tikv] | table:t4                                                                    | keep order:false, stats:pseudo              |
        +-------------------------------+---------+-----------+-----------------------------------------------------------------------------+---------------------------------------------+

        -- The conditions do not match the semantics, so TiDB cannot use IndexMerge for this SQL statement as explained above.
        > EXPLAIN SELECT /*+ use_index_merge(t4, mvi1, mvi2) */ * FROM t4 WHERE json_contains(j->'$.a', '[1]') OR json_contains(j->'$.b', '[2, 3]');
        +-------------------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        | id                      | estRows  | task      | access object | operator info                                                                                                                                           |
        +-------------------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        | TableReader_7           | 10.01    | root      |               | data:Selection_6                                                                                                                                        |
        | └─Selection_6           | 10.01    | cop[tikv] |               | or(json_contains(json_extract(test.t4.j, "$.a"), cast("[1]", json BINARY)), json_contains(json_extract(test.t4.j, "$.b"), cast("[2, 3]", json BINARY))) |
        |   └─TableFullScan_5     | 10000.00 | cop[tikv] | table:t4      | keep order:false, stats:pseudo                                                                                                                          |
        +-------------------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        ```

    - If `json_overlaps` is connected with `OR`, it matches the semantics. For example:

        ```sql
        EXPLAIN SELECT /*+ use_index_merge(t4, mvi1, mvi2) */ * FROM t4 WHERE json_overlaps(j->'$.a', '[1]') OR json_overlaps(j->'$.b', '[2, 3]');
        EXPLAIN SELECT /*+ use_index_merge(t4, mvi1, mvi2) */ * FROM t4 WHERE json_overlaps(j->'$.a', '[1]') AND json_overlaps(j->'$.b', '[2, 3]');
        ```

        ```sql
        > EXPLAIN SELECT /*+ use_index_merge(t4, mvi1, mvi2) */ * FROM t4 WHERE json_overlaps(j->'$.a', '[1]') OR json_overlaps(j->'$.b', '[2, 3]');
        +---------------------------------+---------+-----------+-----------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        | id                              | estRows | task      | access object                                                               | operator info                                                                                                                                           |
        +---------------------------------+---------+-----------+-----------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
