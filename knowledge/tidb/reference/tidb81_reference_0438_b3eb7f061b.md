# Join Reorder selection and limits

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/join-reorder.md`
- Source Title: `Introduction to Join Reorder`
- Source Heading Path: `Introduction to Join Reorder > Selection of the Join Reorder algorithms | Introduction to Join Reorder > Limitations of Join Reorder algorithms`
- Source Line Ranges: `58-70`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `system variable`, `threshold`, `outer join`, `straight_join`, `limitation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0438_b3eb7f061b`
- Source ID: `tidb-docs-8.1:join-reorder.md#selection-of-the-join-reorder-algorithms`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b3287dd790fb245094a9d969fe7ecaecfe0b14b00dde963f9902db47d3551f6d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/join-reorder#selection-of-the-join-reorder-algorithms
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/join-reorder.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how TiDB chooses between Join Reorder algorithms, what variables control join reorder behavior, or what limitations exist for outer join and STRAIGHT_JOIN.
- Retrieval Keywords: tidb_opt_join_reorder_threshold, Selection of the Join Reorder algorithms, tidb_enable_outer_join_reorder, Outer Join, dynamic programming algorithm cannot perform Join Reorder for outer join, STRAIGHT_JOIN, force a join order, limitations of Join Reorder algorithms
- Follow-up Guidance: It states that `tidb_opt_join_reorder_threshold` controls whether TiDB uses the greedy algorithm or the dynamic programming algorithm, and that `STRAIGHT_JOIN` is supported to force a join order.
- Classification Note: This is reference content because it lists the controlling system variables, selection rule, and documented limitations of Join Reorder algorithms.

## Official Source Content

## Selection of the Join Reorder algorithms

The selection of the TiDB Join Reorder algorithms is controlled by the [`tidb_opt_join_reorder_threshold`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_join_reorder_threshold) variable. If the number of nodes participating in Join Reorder is greater than this threshold, TiDB uses the greedy algorithm. Otherwise, TiDB uses the dynamic programming algorithm.
## Limitations of Join Reorder algorithms

The current Join Reorder algorithms have the following limitations:

- Limited by the calculation methods of the result sets, the algorithm cannot ensure it selects the optimum join order.
- The Join Reorder algorithm's support for Outer Join is controlled by the [`tidb_enable_outer_join_reorder`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_outer_join_reorder-new-in-v610) system variable. 
- Currently, the dynamic programming algorithm cannot perform Join Reorder for outer join.

Currently, the `STRAIGHT_JOIN` syntax is supported in TiDB to force a join order. For more information, refer to [Description of the syntax elements](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select#description-of-the-syntax-elements).
