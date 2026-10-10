# TiDB 4.0.8 release overview and new features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.8.md`
- Source Title: `TiDB 4.0.8 Release Notes`
- Source Heading Path: `TiDB 4.0.8 Release Notes | TiDB 4.0.8 Release Notes > New Features`
- Source Line Ranges: `5-27`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiflash`, `ticdc`
- Topic Tags: `release-date`, `version`, `new-features`, `aggregate-functions`, `pushdown`, `consistent-replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0190_bca42a5b3d`
- Source ID: `tidb-docs-8.1:releases/release-4.0.8.md#tidb-4-0-8-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5c041ac85121a8591edd4df541d2a6aab98795ef49c0859bd012196ac96d4f44`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.8#tidb-4-0-8-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.8.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 4.0.8 release date, version, or newly added features in TiDB, TiFlash, and TiCDC.
- Retrieval Keywords: TiDB 4.0.8 Release Notes, Release date October 30 2020, TiDB version 4.0.8, APPROX_PERCENTILE, Support the new aggregate function APPROX_PERCENTILE, TiFlash support pushing down CAST functions, TiCDC support snapshot-level consistent replication, New Features
- Follow-up Guidance: For broader changes in the same release, see the Improvements and Bug Fixes sections of the TiDB 4.0.8 release notes.
- Classification Note: This is classified as a release overview because the official content states the release date and version and lists new features added in TiDB, TiFlash, and TiCDC.

## Official Source Content

# TiDB 4.0.8 Release Notes

Release date: October 30, 2020

TiDB version: 4.0.8
## New Features

+ TiDB

    - Support the new aggregate function `APPROX_PERCENTILE` [#20197](https://github.com/pingcap/tidb/pull/20197)

+ TiFlash

    - Support pushing down `CAST` functions

+ Tools

    + TiCDC

        - Support snapshot-level consistent replication [#932](https://github.com/pingcap/tiflow/pull/932)
