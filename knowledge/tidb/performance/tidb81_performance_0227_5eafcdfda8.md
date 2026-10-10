# v8.5.0 performance highlights overview

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v8.5-performance-highlights.md`
- Source Title: `TiDB Cloud Performance Highlights for TiDB v8.5.0`
- Source Heading Path: `TiDB Cloud Performance Highlights for TiDB v8.5.0 | TiDB Cloud Performance Highlights for TiDB v8.5.0 > General performance`
- Source Line Ranges: `5-24`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `performance`, `lts`, `general`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0227_5eafcdfda8`
- Source ID: `tidb-docs-8.1:tidb-cloud/v8.5-performance-highlights.md#tidb-cloud-performance-highlights-for-tidb-v8-5-0`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0820cfe954af341d9fb501e6203db07f4afc24b21cbbf08be68826d7ae147b3b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v8.5-performance-highlights#tidb-cloud-performance-highlights-for-tidb-v8-5-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v8.5-performance-highlights.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving a high-level summary of TiDB Cloud performance improvements in TiDB v8.5.0, especially general performance gains and the default Region size change.
- Retrieval Keywords: TiDB Cloud Performance Highlights for TiDB v8.5.0, General performance, Long-Term Support (LTS), default Region size increased from 96 MiB to 256 MiB, oltp_insert performance improves by 27%, Analyze performance approximately 45%
- Follow-up Guidance: The document also outlines improvements in hotspot reads with excessive MVCC versions, IO latency jitter, batch processing, and TiKV scaling performance.
- Classification Note: This is classified as cloud performance content because it summarizes TiDB Cloud performance highlights for TiDB v8.5.0 and includes benchmark-style improvement figures.

## Official Source Content

# TiDB Cloud Performance Highlights for TiDB v8.5.0

[TiDB v8.5.0](https://docs.pingcap.com/tidb/v8.5/release-8.5.0) is an important Long-Term Support (LTS) release, which delivers notable improvements in performance, scalability, and operational efficiency.

This document outlines the performance improvements in v8.5.0 across the following areas:

- General performance
- Hotspot reads with excessive MVCC versions
- IO latency jitter
- Batch processing
- TiKV scaling performance
## General performance

With the default Region size increased from 96 MiB to 256 MiB and some other improvements in v8.5.0, significant performance improvements are observed:

- `oltp_insert` performance improves by 27%.
- `Analyze` performance shows a major boost of approximately 45%.
