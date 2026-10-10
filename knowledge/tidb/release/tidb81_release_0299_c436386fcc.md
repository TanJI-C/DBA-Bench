# MySQL compatibility, migration, and data sharing updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.0.md`
- Source Title: `TiDB 6.1.0 Release Notes`
- Source Heading Path: `TiDB 6.1.0 Release Notes > New Features > MySQL compatibility | TiDB 6.1.0 Release Notes > New Features > Data migration | TiDB 6.1.0 Release Notes > New Features > TiDB data share subscription | TiDB 6.1.0 Release Notes > Compatibility changes`
- Source Line Ranges: `188-231`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `sql`, `dm`, `ticdc`, `ecosystem`
- Topic Tags: `mysql compatibility`, `user-level locks`, `shard merge`, `optimistic mode`, `dm webui`, `data sharing`, `kafka`, `avro`, `canal-json`, `sasl`, `gbk`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0299_c436386fcc`
- Source ID: `tidb-docs-8.1:releases/release-6.1.0.md#mysql-compatibility`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0c441091f6678f2d4ef99418ddc38603848b891d021549214b51acabbd06ad76`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.0#mysql-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when finding TiDB 6.1.0 updates for MySQL-compatible user-level locks, DM sharded table optimistic mode and WebUI task startup parameters, TiCDC Kafka data sharing formats and authentication, or GBK table replication compatibility.
- Retrieval Keywords: TiDB 6.1.0 MySQL compatibility, user-level lock management, GET_LOCK, RELEASE_LOCK, RELEASE_ALL_LOCKS, Data migration, optimistic mode, merging and migrating sharded tables, DM WebUI, start time, safe mode duration, TiDB data share subscription, TiCDC, Kafka, Avro format, Canal-json, Flink, topic dispatcher, partition dispatchers, SASL GSSAPI, authentication and authorization of Kafka, charset=GBK, replicating GBK tables
- Follow-up Guidance: The source groups these items under new features for MySQL compatibility, data migration, and TiDB data share subscription, followed by a Compatibility changes heading.
- Classification Note: This is a shared self-managed release-note chunk covering SQL compatibility, DM migration features, TiCDC ecosystem integrations, and compatibility-related updates in TiDB 6.1.0.

## Official Source Content

### MySQL compatibility

* Support compatibility with user-level lock management with MySQL

    User-level locks are a user-named lock management system provided by MySQL through built-in functions. The locking functions can provide lock blocking, waiting, and other lock management capabilities. User-level locks are also widely used in ORM frameworks, such as Rails, Elixir, and Ecto. Since v6.1.0, TiDB has supported MySQL-compatible user-level lock management, and supports `GET_LOCK`, `RELEASE_LOCK`, and `RELEASE_ALL_LOCKS` functions.

    [User document](https://docs.pingcap.com/tidb/stable/functions-and-operators/locking-functions), [#14994](https://github.com/pingcap/tidb/issues/14994)
### Data migration

* The optimistic mode for merging and migrating sharded tables becomes GA

    DM adds a large number of scenario tests for tasks that merge and migrate data from sharded tables in the optimistic mode, which covers 90% of the daily use scenarios. Compared with the pessimistic mode, the optimistic mode is simpler and more efficient to use. It is recommended to use the optimistic mode preferably after you are familiar with the usage notes.

    [User document](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-optimistic#restrictions)

* DM WebUI supports starting a task according to the specified parameters

    When starting a migration task, you can specify a start time and a safe mode duration. This is especially useful when you create an incremental migration task with lots of sources, eliminating the need to specify the binlog start position specifically for each source.

    [User document](https://docs.pingcap.com/tidb/stable/dm/dm-webui-guide), [#5442](https://github.com/pingcap/tiflow/issues/5442)
### TiDB data share subscription

* TiDB supports data sharing with various third-party data ecosystems

    * TiCDC supports sending TiDB incremental data to Kafka in the Avro format, allowing data sharing with third-parties, such as KSQL and Snowflake via Confluent.

        [User document](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-avro-protocol), [#5338](https://github.com/pingcap/tiflow/issues/5338)

    * TiCDC supports dispatching incremental data from TiDB to different Kafka topics by table, which, combined with the Canal-json format, allows sharing data directly with Flink.

        [User document](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#customize-the-rules-for-topic-and-partition-dispatchers-of-kafka-sink), [#4423](https://github.com/pingcap/tiflow/issues/4423)

    * TiCDC supports SASL GSSAPI authentication types and adds SASL authentication examples using Kafka.

        [User document](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#ticdc-uses-the-authentication-and-authorization-of-kafka), [#4423](https://github.com/pingcap/tiflow/issues/4423)

* TiCDC supports replicating `charset=GBK` tables.

    [User document](https://docs.pingcap.com/tidb/stable/character-set-gbk#component-compatibility), [#4806](https://github.com/pingcap/tiflow/issues/4806)
## Compatibility changes
