# Release overview, compatibility change, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.6.md`
- Source Title: `TiDB 6.1.6 Release Notes`
- Source Heading Path: `TiDB 6.1.6 Release Notes | TiDB 6.1.6 Release Notes > Compatibility changes | TiDB 6.1.6 Release Notes > Improvements`
- Source Line Ranges: `5-30`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `ticdc`, `tidb`, `tikv`
- Topic Tags: `release-notes`, `compatibility`, `upgrade`, `avro`, `schema-registry`, `plan-cache`, `batchpointget`, `index-join`, `cpu`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0317_cf8745005e`
- Source ID: `tidb-docs-8.1:releases/release-6.1.6.md#tidb-6-1-6-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `330127d1f2117736a176d42e7765dc10a568c5cf6d2cd197dc608889bee3d1e2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.6#tidb-6-1-6-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.1.6 release-note information about the TiCDC Avro FLOAT compatibility change during upgrade or the listed TiDB and TiKV improvements.
- Retrieval Keywords: TiDB 6.1.6 Release Notes, Compatibility changes, TiCDC, Avro, FLOAT, Confluent Schema Registry, compatibility policy, None, changefeed, schema update, Prepared Plan Cache, BatchPointGet, Index Join, Support more SQL formats for Index Join, TiKV CPU with less than 1 core
- Follow-up Guidance: The content states that when upgrading a TiCDC cluster to v6.1.6 or a later v6.1.x version, if a table replicated using Avro contains the FLOAT data type, you need to manually adjust the compatibility policy of Confluent Schema Registry to None before upgrading; otherwise the changefeed will be unable to update the schema and enter an error state.
- Classification Note: This chunk is classified as a release note because it summarizes TiDB 6.1.6 compatibility changes and improvements across TiCDC, TiDB, and TiKV.

## Official Source Content

# TiDB 6.1.6 Release Notes

Release date: April 12, 2023

TiDB version: 6.1.6

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.1/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.1/production-deployment-using-tiup)
## Compatibility changes

- TiCDC fixes the issue of incorrect encoding of FLOAT data in Avro [#8490](https://github.com/pingcap/tiflow/issues/8490) @[3AceShowHand](https://github.com/3AceShowHand)

    When upgrading the TiCDC cluster to v6.1.6 or a later v6.1.x version, if a table replicated using Avro contains the `FLOAT` data type, you need to manually adjust the compatibility policy of Confluent Schema Registry to `None` before upgrading so that the changefeed can successfully update the schema. Otherwise, after upgrading, the changefeed will be unable to update the schema and enter an error state.
## Improvements

+ TiDB

    - Supports caching the execution plan for `BatchPointGet` in Prepared Plan Cache [#42125](https://github.com/pingcap/tidb/issues/42125) @[qw4990](https://github.com/qw4990)
    - Support more SQL formats for Index Join [#40505](https://github.com/pingcap/tidb/issues/40505) @[Yisaer](https://github.com/Yisaer)

+ TiKV

    - Support starting TiKV on a CPU with less than 1 core [#13586](https://github.com/tikv/tikv/issues/13586) [#13752](https://github.com/tikv/tikv/issues/13752) [#14017](https://github.com/tikv/tikv/issues/14017) @[andreid-db](https://github.com/andreid-db) @[andreid-db](https://github.com/andreid-db)
