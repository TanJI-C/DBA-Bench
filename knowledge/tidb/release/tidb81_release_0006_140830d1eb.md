# TiDB 1.0.2 release updates across TiDB, PD, and TiKV

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-1.0.2.md`
- Source Title: `TiDB 1.0.2 Release Notes`
- Source Heading Path: `TiDB 1.0.2 Release Notes | TiDB 1.0.2 Release Notes > TiDB | TiDB 1.0.2 Release Notes > Placement Driver (PD) | TiDB 1.0.2 Release Notes > TiKV`
- Source Line Ranges: `5-29`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `release-notes`, `query-optimization`, `ddl`, `scheduling`, `region-splitting`, `key-length`, `traffic-statistics`, `bug-fixes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0006_140830d1eb`
- Source ID: `tidb-docs-8.1:releases/release-1.0.2.md#tidb-1-0-2-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4813f8e235d9b6c9a30203ee3e24f0ffe4f0c086fb0022072f5adb14f802af8e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-1.0.2#tidb-1-0-2-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-1.0.2.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the specific updates included in TiDB 1.0.2 across TiDB, PD, and TiKV release notes.
- Retrieval Keywords: TiDB 1.0.2 Release Notes, TiDB 1.0.2, Optimize the cost estimation of index point query, Alter Table Add Column (ColumnDef ColumnPosition), where conditions are contradictory, Add Index operation, Index Look Join, prefix index judgment, Placement Driver (PD), Improve the stability of scheduling under exceptional situations, Support splitting table, one region does not contain data from multiple tables, Limit the length of a key to be no more than 4 KB, More accurate read traffic statistics, deep protection on the coprocessor stack, LIKE behavior, do_div_mod bug
- Follow-up Guidance: The content groups the TiDB 1.0.2 changes by component under TiDB, Placement Driver (PD), and TiKV.
- Classification Note: This is classified as a release chunk because the official content is a versioned release note enumerating component-specific fixes, optimizations, and feature updates for TiDB 1.0.2.

## Official Source Content

# TiDB 1.0.2 Release Notes

On November 13, 2017, TiDB 1.0.2 is released with the following updates:
## TiDB

- Optimize the cost estimation of index point query
- Support the `Alter Table Add Column (ColumnDef ColumnPosition)` syntax
- Optimize the queries whose `where` conditions are contradictory
- Optimize the `Add Index` operation to rectify the progress and reduce repetitive operations
- Optimize the `Index Look Join` operator to accelerate the query speed for small data size
- Fix the issue with prefix index judgment
## Placement Driver (PD)

- Improve the stability of scheduling under exceptional situations
## TiKV

- Support splitting table to ensure one region does not contain data from multiple tables
- Limit the length of a key to be no more than 4 KB
- More accurate read traffic statistics
- Implement deep protection on the coprocessor stack
- Fix the `LIKE` behavior and the `do_div_mod` bug
