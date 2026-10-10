# Configuring output-raw-change-event and release compatibility

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-split-update-behavior.md`
- Source Title: `TiCDC Behavior in Splitting UPDATE Events`
- Source Heading Path: `TiCDC Behavior in Splitting UPDATE Events > Split primary or unique key `UPDATE` events for non-MySQL sinks > Control whether to split primary or unique key `UPDATE` events | TiCDC Behavior in Splitting UPDATE Events > Split primary or unique key `UPDATE` events for non-MySQL sinks > Control whether to split primary or unique key `UPDATE` events > Release 6.5 compatibility | TiCDC Behavior in Splitting UPDATE Events > Split primary or unique key `UPDATE` events for non-MySQL sinks > Control whether to split primary or unique key `UPDATE` events > Release 7.1 compatibility | TiCDC Behavior in Splitting UPDATE Events > Split primary or unique key `UPDATE` events for non-MySQL sinks > Control whether to split primary or unique key `UPDATE` events > Release 7.5 compatibility | TiCDC Behavior in Splitting UPDATE Events > Split primary or unique key `UPDATE` events for non-MySQL sinks > Control whether to split primary or unique key `UPDATE` events > Release 8.1 compatibility`
- Source Line Ranges: `115-159`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`
- Topic Tags: `output-raw-change-event`, `non-mysql-sinks`, `compatibility`, `version-behavior`, `primary-key`, `unique-key`, `clustered-index`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0194_ba30203f5d`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-split-update-behavior.md#control-whether-to-split-primary-or-unique-key-update-events`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dc00433969977866616c9b49468b0fb86dccc89bf68f606b5f3e3f37c2a70e4e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-split-update-behavior#control-whether-to-split-primary-or-unique-key-update-events
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-split-update-behavior.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about the output-raw-change-event parameter, whether non-MySQL sinks split primary or unique key UPDATE events, or release compatibility across 6.5, 7.1, 7.5, and 8.1.
- Retrieval Keywords: output-raw-change-event, non-MySQL sink, split primary key UPDATE events, split unique key UPDATE events, raw change event, release 6.5 compatibility, release 7.1 compatibility, release 7.5 compatibility, release 8.1 compatibility, CSV, Avro, Canal, Open, clustered index, #11211
- Follow-up Guidance: The content states that when output-raw-change-event is true, TiCDC does not split UPDATE events, while updates to a clustered-index primary key are still split into DELETE and INSERT events in TiDB.
- Classification Note: This is classified as configuration because it centers on the output-raw-change-event parameter and compatibility tables that define the resulting behavior.

## Official Source Content

### Control whether to split primary or unique key `UPDATE` events

Starting from v6.5.10, v7.1.6, v7.5.3, and v8.1.1, when using a non-MySQL sink, TiCDC supports controlling whether to split primary or unique key `UPDATE` events via the `output-raw-change-event` parameter, as described in the GitHub issue [#11211]( https://github.com/pingcap/tiflow/issues/11211). The specific behavior of this parameter is as follows:

- When you set `output-raw-change-event = false`, if the primary key or non-null unique index value is modified in an `UPDATE` event, TiCDC splits the event into `DELETE` and `INSERT` events and ensures that all events follow the sequence of `DELETE` events preceding `INSERT` events.
- When you set `output-raw-change-event = true`, TiCDC does not split `UPDATE` events, and the consumer side is responsible for dealing with the problems described in [Split primary or unique key `UPDATE` events for non-MySQL sinks](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-split-update-behavior#split-primary-or-unique-key-update-events-for-non-mysql-sinks). Otherwise there might be a risk of data inconsistency. Note that when the primary key of a table is a clustered index, updates to the primary key are still split into `DELETE` and `INSERT` events in TiDB, and such behavior is not affected by the `output-raw-change-event` parameter.

> **Note**
>
> In the following tables, UK/PK stands for primary key or unique key.
#### Release 6.5 compatibility

| Version | Protocol | Split UK/PK `UPDATE` events | Not split UK/PK `UPDATE` events  | Comments |
| -- | -- | -- | -- | -- |
| <= v6.5.2 | ALL | ✗ | ✓ |  |
| v6.5.3 / v6.5.4 | Canal/Open | ✗ | ✓ |  |
| v6.5.3 | CSV/Avro | ✗ | ✗ | Split but does not sort. See [#9086](https://github.com/pingcap/tiflow/issues/9658) |
| v6.5.4 | Canal/Open | ✗ | ✗ | Only split and sort transactions that contain multiple changes |
| v6.5.5 ～ v6.5.9 | ALL | ✓ | ✗ |
| \>= v6.5.10 | ALL | ✓ (Default value: `output-raw-change-event = false`) | ✓ (Optional: `output-raw-change-event = true`) | |
#### Release 7.1 compatibility

| Version | Protocol | Split UK/PK `UPDATE` events | Not split UK/PK `UPDATE` events  | Comments |
| -- | -- | -- | -- | -- |
| v7.1.0 | ALL | ✗ | ✓ |  |
| v7.1.1 | Canal/Open | ✗ | ✓ |  |
| v7.1.1 | CSV/Avro | ✗ | ✗ | Split but does not sort. See [#9086](https://github.com/pingcap/tiflow/issues/9658) |
| v7.1.2  ~ v7.1.5 | ALL | ✓ | ✗ |  |
| \>= v7.1.6 | ALL | ✓ (Default value: `output-raw-change-event = false`) | ✓ (Optional: `output-raw-change-event = true`)  | |
#### Release 7.5 compatibility

| Version | Protocol | Split UK/PK `UPDATE` events | Not split UK/PK `UPDATE` events  | Comments |
| -- | -- | -- | -- | -- |
| <= v7.5.2 | ALL | ✓ | ✗ |
| \>= v7.5.3 | ALL | ✓ (Default value:`output-raw-change-event = false`) | ✓  (Optional: `output-raw-change-event = true`) | |
#### Release 8.1 compatibility

| Version | Protocol | Split UK/PK `UPDATE` events | Not split UK/PK `UPDATE` events  | Comments |
| -- | -- | -- | -- | -- |
| v8.1.0 | ALL | ✓ | ✗ |
| \>= v8.1.1 | ALL | ✓ (Default value:`output-raw-change-event = false`) | ✓  (Optional: `output-raw-change-event = true`) | |
