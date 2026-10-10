# TiDB and TiKV bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.13.md`
- Source Title: `TiDB 3.0.13 Release Notes`
- Source Heading Path: `TiDB 3.0.13 Release Notes > Bug Fixes`
- Source Line Ranges: `12-20`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `bug fixes`, `insert on duplicate key update`, `region merge`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0105_1ec6eb26dd`
- Source ID: `tidb-docs-8.1:releases/release-3.0.13.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8ae3e791dc2bb42a9e180f5bdccaa99b1b5c26fa2710a26e0d5eef33aa072c7a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.13#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.13.md

## Retrieval Guidance

- Use When: Use this chunk when looking for bug fixes in TiDB 3.0.13 related to incorrect `INSERT ... ON DUPLICATE KEY UPDATE` behavior in transactions or TiKV service unavailability during repeated `Region Merge`.
- Retrieval Keywords: Bug Fixes, TiDB bug fix, TiKV bug fix, INSERT ... ON DUPLICATE KEY UPDATE, unchecked MemBuffer, multiple rows of duplicate data, transaction executed incorrectly, Region Merge, system might get stuck, service is unavailable, #16690, #7612
- Follow-up Guidance: The chunk separates the fixes by component, covering one TiDB issue and one TiKV issue in the TiDB 3.0.13 release notes.
- Classification Note: This is classified as a bug fixes chunk because the content lists resolved issues for TiDB and TiKV and names the affected statements and operational condition.

## Official Source Content

## Bug Fixes

+ TiDB

    - Fix the issue caused by unchecked `MemBuffer` that the `INSERT ... ON DUPLICATE KEY UPDATE` statement might be executed incorrectly within a transaction when users need to insert multiple rows of duplicate data [#16690](https://github.com/pingcap/tidb/pull/16690)

+ TiKV

    - Fix the issue that the system might get stuck and the service is unavailable if `Region Merge` is executed repeatedly [#7612](https://github.com/tikv/tikv/pull/7612)
