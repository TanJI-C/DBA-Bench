# Drainer downstream and checkpoint configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/tidb-binlog-configuration-file.md`
- Source Title: `TiDB Binlog Configuration File`
- Source Heading Path: `TiDB Binlog Configuration File > Drainer > syncer > load-schema-snapshot | TiDB Binlog Configuration File > Drainer > syncer.to | TiDB Binlog Configuration File > Drainer > syncer.to > mysql/tidb | TiDB Binlog Configuration File > Drainer > syncer.to > file | TiDB Binlog Configuration File > Drainer > syncer.to > kafka | TiDB Binlog Configuration File > Drainer > syncer.to.checkpoint`
- Source Line Ranges: `308-360`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `drainer`, `syncer`, `schema-loading`, `ddl-replay`, `gc-safe-point`, `downstream`, `mysql`, `tidb`, `file`, `kafka`, `checkpoint`, `replication-progress`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0201_961551fa49`
- Source ID: `tidb-docs-8.1:tidb-binlog/tidb-binlog-configuration-file.md#load-schema-snapshot`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `13cfc191a151f2081d7125207245127134772fbc3fcb190f549bcdea8083b686`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-configuration-file#load-schema-snapshot
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/tidb-binlog-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Drainer settings for loading schema information, downstream connection targets, or where replication progress is stored.
- Retrieval Keywords: load-schema-snapshot, syncer.to, mysql/tidb, file, kafka, syncer.to.checkpoint, checkpoint schema, GC safe point, checkpoint TS, read-timeout, zookeeper-addrs, kafka-addrs, kafka-version, topic-name, data-dir/savepoint
- Follow-up Guidance: Check the downstream type and checkpoint storage settings together when configuring Drainer replication progress.
- Classification Note: This chunk is configuration content for TiDB Binlog Drainer downstream settings, schema loading behavior, and checkpoint storage options.

## Official Source Content

#### load-schema-snapshot

- Specifies how Drainer loads table information.
- When you set it to `false`, Drainer replays all DDL operations from history to derive the table schema for each table at a specific schema version. This approach requires processing all DDL changes from the initial state to the target schema version, which might involve significant data processing and replaying.
- When you set it to `true`, Drainer directly reads the table information at the checkpoint TS. Because it directly reads the table information at a specific point in time, this method is usually more efficient. However, it is subject to the GC mechanism, because GC might delete older data versions. If the checkpoint TS is too old, the corresponding table information might have been deleted by GC, making it impossible to read directly.
- When configuring Drainer, choose whether to read the table information at the checkpoint TS based on actual needs. If data integrity and consistency are priorities and handling a large number of DDL changes is acceptable, it is recommended to set it to `false`. If efficiency and performance are more important, and the checkpoint TS is guaranteed to be after the GC safe point, it is recommended to set it to `true`.
- Default value: `false`
### syncer.to

The `syncer.to` section introduces different types of downstream configuration items according to configuration types.
#### mysql/tidb

The following configuration items are related to connection to downstream databases:

* `host`: If this item is not set, TiDB Binlog tries to check the `MYSQL_HOST` environment variable which is `localhost` by default.
* `port`: If this item is not set, TiDB Binlog tries to check the `MYSQL_PORT` environment variable which is `3306` by default.
* `user`: If this item is not set, TiDB Binlog tries to check the `MYSQL_USER` environment variable which is `root` by default.
* `password`: If this item is not set, TiDB Binlog tries to check the `MYSQL_PSWD` environment variable which is `""` by default.
* `read-timeout`: Specifies the I/O read timeout of the downstream database connection. The default value is `1m`. If Drainer keeps failing on some DDLs that take a long time, you can set this configuration to a larger value. 
#### file

* `dir`: Specifies the directory where binlog files are stored. If this item is not set, `data-dir` is used.
#### kafka

When the downstream is Kafka, the valid configuration items are as follows:

* `zookeeper-addrs`
* `kafka-addrs`
* `kafka-version`
* `kafka-max-messages`
* `kafka-max-message-size`
* `topic-name`
### syncer.to.checkpoint

* `type`: Specifies in what way the replication progress is saved. Currently, the available options are `mysql`, `tidb`, and `file`.

    This configuration item is the same as the downstream type by default. For example, when the downstream is `file`, the checkpoint progress is saved in the local file `<data-dir>/savepoint`; when the downstream is `mysql`, the progress is saved in the downstream database. If you need to explicitly specify using `mysql` or `tidb` to store the progress, make the following configuration:

* `schema`: `"tidb_binlog"` by default.

    > **Note:**
    >
    > When deploying multiple Drainer nodes in the same TiDB cluster, you need to specify a different checkpoint schema for each node. Otherwise, the replication progress of two instances will overwrite each other.

* `host`
* `user`
* `password`
* `port`
