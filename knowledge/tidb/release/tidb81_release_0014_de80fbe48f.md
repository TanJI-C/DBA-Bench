# TiDB 1.0.8 PD changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-1.0.8.md`
- Source Title: `TiDB 1.0.8 Release Notes`
- Source Heading Path: `TiDB 1.0.8 Release Notes > PD`
- Source Line Ranges: `24-28`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `shared`
- Topic Tags: `lock overheat`, `region heartbeat`, `hot region scheduler`, `leader selection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0014_de80fbe48f`
- Source ID: `tidb-docs-8.1:releases/release-1.0.8.md#pd`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `11fa697721a917e056da5c23cfab1b39f64d07b1ecd381aa45d9da807f186e43`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-1.0.8#pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-1.0.8.md

## Retrieval Guidance

- Use When: Use this chunk when looking for PD 1.0.8 fixes involving region heartbeats, lock overheat, or hot region scheduler leader selection.
- Retrieval Keywords: PD, lock overheat, region heartbeats, hot region scheduler, wrong Leader, leader selection
- Follow-up Guidance: The chunk lists PD changes that reduce lock overheat of region heartbeats and fix wrong Leader selection by a hot region scheduler.
- Classification Note: This is classified as a PD release change list because the content contains two PD-specific fixes in TiDB 1.0.8 release notes.

## Official Source Content

## PD

- [Reduce the lock overheat of the region heartbeats](https://github.com/pingcap/pd/pull/932)
- [Fix the issue that a hot region scheduler selects the wrong Leader](https://github.com/pingcap/pd/pull/939)
