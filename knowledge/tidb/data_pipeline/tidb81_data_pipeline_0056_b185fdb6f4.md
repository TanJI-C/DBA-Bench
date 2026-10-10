# Replication event filtering

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.2.0.md`
- Source Title: `TiDB 6.2.0 Release Notes`
- Source Heading Path: `TiDB 6.2.0 Release Notes > New features > TiDB data share subscription`
- Source Line Ranges: `232-245`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tikv`
- Topic Tags: `rawkv replication`, `change data capture`, `ddl filtering`, `dml filtering`, `sql expressions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0056_b185fdb6f4`
- Source ID: `tidb-docs-8.1:releases/release-6.2.0.md#tidb-data-share-subscription`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f18b287c76575ce497799e88e377607d4c8c0ed6103db74861c3be6fca7363ec`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.2.0#tidb-data-share-subscription
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.2.0 change replication features such as RawKV cross-cluster replication or TiCDC filtering of DDL and DML events.
- Retrieval Keywords: TiDB data share subscription, cross-cluster RawKV replication, experimental, TiKV-CDC, subscribing to the data change of RawKV, downstream TiKV cluster, real-time, filtering DDL and DML events, TiCDC, filter rules for incremental data change logs, DROP TABLE, filtering DDL events of specified types, filtering DML events based on SQL expressions, ticdc-filter
- Follow-up Guidance: The source links to user documents for TiKV API version and TiCDC event filtering.
- Classification Note: This is classified under the data pipeline category because the content describes change data capture and replication event filtering features.

## Official Source Content

### TiDB data share subscription

* Support cross-cluster RawKV replication (experimental)

    Support subscribing to the data change of RawKV and replicating the data change to a downstream TiKV cluster in real-time using a new component TiKV-CDC, which makes the cross-cluster replication possible.

    [User document](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#api-version-new-in-v610) [#11965](https://github.com/tikv/tikv/issues/11965) @[pingyu](https://github.com/pingyu)

* Support filtering DDL and DML events

    In some special occasions, you might want to set filter rules for incremental data change logs. For example, filtering high risk DDL events such as DROP TABLE. Starting from v6.2.0, TiCDC supports filtering DDL events of specified types and filtering DML events based on SQL expressions. This makes TiCDC applicable to more data replication scenarios.

    [User document](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-filter) [#6160](https://github.com/pingcap/tiflow/issues/6160) @[asddongmen](https://github.com/asddongmen)
