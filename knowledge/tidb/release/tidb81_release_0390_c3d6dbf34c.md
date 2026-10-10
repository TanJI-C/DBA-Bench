# Release overview and compatibility changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.2.md`
- Source Title: `TiDB 6.5.2 Release Notes`
- Source Heading Path: `TiDB 6.5.2 Release Notes | TiDB 6.5.2 Release Notes > Compatibility changes`
- Source Line Ranges: `5-21`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `ticdc`
- Topic Tags: `release-notes`, `compatibility`, `upgrade`, `avro`, `schema-registry`, `changefeed`, `partitioned-tables`, `data-loss-warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0390_c3d6dbf34c`
- Source ID: `tidb-docs-8.1:releases/release-6.5.2.md#tidb-6-5-2-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7bfcb03139a1009a8d1da41ba41df5cccc50929b7b624970a7a8315effc27f30`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.2#tidb-6-5-2-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.2.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiDB 6.5.2 compatibility changes for TiCDC, especially Avro FLOAT encoding, Confluent Schema Registry compatibility policy, or sink behavior for partitioned tables.
- Retrieval Keywords: TiDB 6.5.2 Release Notes, Compatibility changes, TiCDC, Avro, FLOAT, Confluent Schema Registry, compatibility policy, None, changefeed, schema update, error state, sink.enable-partition-separator, partitioned tables, data loss, storage services
- Follow-up Guidance: The content states that after upgrading to v6.5.2 or a later v6.5.x version, a changefeed using Avro with FLOAT columns might be unable to update schema unless the Confluent Schema Registry compatibility policy is manually adjusted to None before upgrading.
- Classification Note: This is a release compatibility chunk because it describes behavior changes and upgrade implications for TiCDC configuration and changefeed schema handling in TiDB 6.5.2.

## Official Source Content

# TiDB 6.5.2 Release Notes

Release date: April 21, 2023

TiDB version: 6.5.2

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.5/production-deployment-using-tiup)
## Compatibility changes

- TiCDC fixes the issue of incorrect encoding of `FLOAT` data in Avro [#8490](https://github.com/pingcap/tiflow/issues/8490) @[3AceShowHand](https://github.com/3AceShowHand)

    When upgrading the TiCDC cluster to v6.5.2 or a later v6.5.x version, if a table replicated using Avro contains the `FLOAT` data type, you need to manually adjust the compatibility policy of Confluent Schema Registry to `None` before upgrading so that the changefeed can successfully update the schema. Otherwise, after upgrading, the changefeed will be unable to update the schema and enter an error state.

- To fix the potential issue of data loss during replication of partitioned tables to storage services, the default value of the TiCDC [`sink.enable-partition-separator`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#changefeed-configuration-parameters) configuration item is changed from `false` to `true`. This means that partitions in a table are stored in separate directories by default. It is recommended that you keep the value as `true` to avoid the data loss issue. [#8724](https://github.com/pingcap/tiflow/issues/8724) @[CharlesCheung96](https://github.com/CharlesCheung96)
