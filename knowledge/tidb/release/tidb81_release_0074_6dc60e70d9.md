# TiKV monitoring and scan request fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.3.md`
- Source Title: `TiDB 2.1.3 Release Notes`
- Source Heading Path: `TiDB 2.1.3 Release Notes > TiKV`
- Source Line Ranges: `46-51`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`
- Topic Tags: `monitoring`, `http`, `data_format`, `scan-request`, `range-check`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0074_6dc60e70d9`
- Source ID: `tidb-docs-8.1:releases/release-2.1.3.md#tikv`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8f876e56e315808176209b183f07dfb0ae8f81c06f8e40706bec90b6e807c3c4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.3#tikv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.3.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiKV 2.1.3 changes for monitoring over HTTP, the data_format NULL issue, or scan request range verification.
- Retrieval Keywords: TiKV, monitoring information using the HTTP method, data_format NULL issue, verifying the range for scan requests
- Follow-up Guidance: The chunk lists three TiKV changes: HTTP access to monitoring information, a fix for the NULL issue of data_format, and range verification for scan requests.
- Classification Note: This is classified as a TiKV release chunk because it contains TiKV-specific monitoring and request validation changes from the release notes.

## Official Source Content

## TiKV

- Support obtaining the monitoring information using the HTTP method [#3855](https://github.com/tikv/tikv/pull/3855)
- Fix the NULL issue of `data_format` [#4075](https://github.com/tikv/tikv/pull/4075)
- Add verifying the range for scan requests [#4124](https://github.com/tikv/tikv/pull/4124)
