# TiDB 4.0.4 release summary and TiDB bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.4.md`
- Source Title: `TiDB 4.0.4 Release Notes`
- Source Heading Path: `TiDB 4.0.4 Release Notes | TiDB 4.0.4 Release Notes > Bug Fixes`
- Source Line Ranges: `5-19`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `release-notes`, `bug-fixes`, `information-schema`, `pointget`, `batchpointget`, `hashjoin`, `query-results`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0183_eb27f76845`
- Source ID: `tidb-docs-8.1:releases/release-4.0.4.md#tidb-4-0-4-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9258c78bac6e8413dd3646166fdf53a367589101b4a5f2e51d4fccd346da0254`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.4#tidb-4-0-4-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 4.0.4 bug fixes related to information_schema query hangs, PointGet or BatchPointGet errors or wrong results, or HashJoin incorrect results with set or enum types.
- Retrieval Keywords: TiDB 4.0.4 Release Notes, 4.0.4 bug fixes, information_schema.columns getting stuck, #18849, PointGet in null error, #18848, BatchPointGet in null error, BatchPointGet wrong result, #18815, HashJoin set enum incorrect query result, #18859, TiDB bug fixes July 31 2020
- Follow-up Guidance: The chunk lists the related pull request identifiers #18849, #18848, #18815, and #18859 for these TiDB fixes.
- Classification Note: The official content is classified as a self-managed TiDB release note because it summarizes TiDB 4.0.4 bug fixes under the Release Notes and Bug Fixes headings.

## Official Source Content

# TiDB 4.0.4 Release Notes

Release date: July 31, 2020

TiDB version: 4.0.4
## Bug Fixes

+ TiDB

    - Fix the issue of getting stuck when querying `information_schema.columns` [#18849](https://github.com/pingcap/tidb/pull/18849)
    - Fix the errors that occur when the `PointGet` and `BatchPointGet` operators encounter `in null` [#18848](https://github.com/pingcap/tidb/pull/18848)
    - Fix the wrong result of `BatchPointGet` [#18815](https://github.com/pingcap/tidb/pull/18815)
    - Fix the issue of incorrect query result that occurs when the `HashJoin` operator encounters the `set` or `enum` type [#18859](https://github.com/pingcap/tidb/pull/18859)
