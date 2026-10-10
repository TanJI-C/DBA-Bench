# Release overview and compatibility changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.2.md`
- Source Title: `TiDB 7.1.2 Release Notes`
- Source Heading Path: `TiDB 7.1.2 Release Notes | TiDB 7.1.2 Release Notes > Compatibility changes | TiDB 7.1.2 Release Notes > Compatibility changes > Behavior changes`
- Source Line Ranges: `5-26`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `ticdc`
- Topic Tags: `release-notes`, `compatibility`, `behavior-changes`, `upgrade`, `security`, `optimizer`, `compaction`, `changefeed`, `kafka`, `csv`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0458_81b0d4c27e`
- Source ID: `tidb-docs-8.1:releases/release-7.1.2.md#tidb-7-1-2-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `263f29ab4323d01a79f2cbc4890ca5bf818c8df52f79865bd61a724aca20a000`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.2#tidb-7-1-2-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.2.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiDB 7.1.2 compatibility changes or behavior changes involving require_secure_transport, smooth upgrade, hash join selection, TiKV periodic compaction, or TiCDC Kafka and CSV changefeed settings.
- Retrieval Keywords: TiDB 7.1.2 Release Notes, Compatibility changes, Behavior changes, require_secure_transport, Security Enhanced Mode, SEM, smooth upgrade, /upgrade/start, upgrade/finish, tidb_opt_enable_hash_join, RocksDB periodic compaction, rocksdb.defaultcf.periodic-compaction-seconds, rocksdb.writecf.periodic-compaction-seconds, rocksdb.lockcf.periodic-compaction-seconds, rocksdb.defaultcf.ttl, rocksdb.writecf.ttl, rocksdb.lockcf.ttl, sink.csv.binary-encoding-method, base64, large-message-handle-option, handle-key-only, Kafka topic limit, TiCDC split update behavior, delete events preceding insert events
- Follow-up Guidance: The chunk points to documentation for TiCDC split update behavior for transactions containing multiple update changes.
- Classification Note: This is a release-notes compatibility and behavior-changes chunk because it lists 7.1.2 changes that affect defaults, configuration items, and TiCDC event ordering.

## Official Source Content

# TiDB 7.1.2 Release Notes

Release date: October 25, 2023

TiDB version: 7.1.2

Quick access: [Quick start](https://docs.pingcap.com/tidb/v7.1/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v7.1/production-deployment-using-tiup)
## Compatibility changes

- Prohibit setting [`require_secure_transport`](https://docs.pingcap.com/tidb/v7.1/system-variables#require_secure_transport-new-in-v610) to `ON` in Security Enhanced Mode (SEM) to prevent potential connectivity issues for users [#47665](https://github.com/pingcap/tidb/issues/47665) @[tiancaiamao](https://github.com/tiancaiamao)
- Disable the [smooth upgrade](https://docs.pingcap.com/tidb/stable/smooth-upgrade-tidb) feature by default. You can enable it by sending the `/upgrade/start` and `upgrade/finish` HTTP requests [#47172](https://github.com/pingcap/tidb/issues/47172) @[zimulala](https://github.com/zimulala)
- Introduce the [`tidb_opt_enable_hash_join`](https://docs.pingcap.com/tidb/v7.1/system-variables#tidb_opt_enable_hash_join-new-in-v712) system variable to control whether the optimizer selects hash joins for tables [#46695](https://github.com/pingcap/tidb/issues/46695) @[coderplay](https://github.com/coderplay)
- Disable periodic compaction of RocksDB by default, so that the default behavior of TiKV RocksDB is now consistent with that in versions before v6.5.0. This change prevents potential performance impact caused by a significant number of compactions after upgrading. In addition, TiKV introduces two new configuration items [`rocksdb.[defaultcf|writecf|lockcf].periodic-compaction-seconds`](https://docs.pingcap.com/tidb/v7.1/tikv-configuration-file#periodic-compaction-seconds-new-in-v712) and [`rocksdb.[defaultcf|writecf|lockcf].ttl`](https://docs.pingcap.com/tidb/v7.1/tikv-configuration-file#ttl-new-in-v712), enabling you to manually configure periodic compaction of RocksDB [#15355](https://github.com/tikv/tikv/issues/15355) @[LykxSassinator](https://github.com/LykxSassinator)
- TiCDC introduces the [`sink.csv.binary-encoding-method`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config#changefeed-configuration-parameters) configuration item to control the encoding method of binary data in the CSV protocol. The default value is `'base64'` [#9373](https://github.com/pingcap/tiflow/issues/9373) @[CharlesCheung96](https://github.com/CharlesCheung96)
- TiCDC introduces the [`large-message-handle-option`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#handle-messages-that-exceed-the-kafka-topic-limit) configuration item. It is empty by default, which means that the changefeed fails when the message size exceeds the limit of the Kafka topic. When this configuration is set to `"handle-key-only"`, if the message exceeds the size limit, only the handle key will be sent to reduce the message size; if the reduced message still exceeds the limit, then the changefeed fails [#9680](https://github.com/pingcap/tiflow/issues/9680) @[3AceShowHand](https://github.com/3AceShowHand)
### Behavior changes

- For transactions containing multiple changes, if the primary key or non-null unique index value is modified in the update event, TiCDC splits an event into delete and insert events and ensures that all events follow the sequence of delete events preceding insert events. For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-split-update-behavior#transactions-containing-multiple-update-changes).
