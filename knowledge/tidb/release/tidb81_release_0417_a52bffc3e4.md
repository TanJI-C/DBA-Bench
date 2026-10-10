# DB operations features across storage, import, migration, CDC, and ecosystem

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.6.0.md`
- Source Title: `TiDB 6.6.0 Release Notes`
- Source Heading Path: `TiDB 6.6.0 Release Notes > Feature details > DB operations`
- Source Line Ranges: `193-254`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `dm`, `lightning`, `ticdc`, `br`, `pd`, `ecosystem`, `sql`
- Topic Tags: `db-operations`, `read-only-nodes`, `replica-read`, `dynamic-config`, `cluster-initialization`, `initialize-sql-file`, `full-migration`, `physical-import`, `csv-import`, `compression`, `rawkv`, `cdc`, `kafka`, `scale-out`, `gorm`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0417_a52bffc3e4`
- Source ID: `tidb-docs-8.1:releases/release-6.6.0.md#db-operations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `896b36fdf51f87a9bf3c287b3565db7ec25406bb93db2248780cae31df1cece3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.6.0#db-operations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.6.0 DB operations updates across read-only storage nodes, dynamic TiKV configuration, cluster initialization SQL, migration and import features, CDC capabilities, or GORM ecosystem integration.
- Retrieval Keywords: TiDB 6.6.0 DB operations, read-only storage nodes, resource-consuming read-only tasks, tidb_replica_read, spark.tispark.replica_read, --replica-read-label, raftstore.store-io-pool-size, store-io-pool-size, dynamic-config, --initialize-sql-file, cluster initialization SQL script, DM physical import mode, full migration experimental, header-schema-match, CSV header does not match target table, compress-kv-pairs, gzip, gz, TiKV-CDC, RawKV, cross-cluster replication of RawKV, TiCDC Kafka changefeed scale out single table, multiple TiCDC nodes, GORM TiDB integration tests, AUTO_RANDOM, AutoMigrate Unique attribute
- Follow-up Guidance: The content provides follow-up documentation links for read-only nodes, dynamic config, initialize-sql-file, DM physical import precheck, TiDB Lightning task configuration, TiKV-CDC, TiCDC Kafka sink scale-out, and GORM documentation.
- Classification Note: This is classified under DB operations because the official content spans operational features for storage access, configuration changes, initialization, data migration and import, CDC, and ecosystem tooling.

## Official Source Content

### DB operations

* Support configuring read-only storage nodes for resource-consuming tasks @[v01dstar](https://github.com/v01dstar)

    In production environments, some read-only operations might consume a large number of resources regularly and affect the performance of the entire cluster, such as backups and large-scale data reading and analysis. TiDB v6.6.0 supports configuring read-only storage nodes for resource-consuming read-only tasks to reduce the impact on the online application. Currently, TiDB, TiSpark, and BR support reading data from read-only storage nodes. You can configure read-only storage nodes according to [steps](https://docs.pingcap.com/tidb/stable/best-practices/readonly-nodes#procedures) and specify where data is read through the system variable `tidb_replica_read`, the TiSpark configuration item `spark.tispark.replica_read`, or the br command line argument `--replica-read-label`, to ensure the stability of cluster performance.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/best-practices/readonly-nodes).

* Support dynamically modifying `store-io-pool-size` [#13964](https://github.com/tikv/tikv/issues/13964) @[LykxSassinator](https://github.com/LykxSassinator)

    The TiKV configuration item [`raftstore.store-io-pool-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#store-io-pool-size-new-in-v530) specifies the allowable number of threads that process Raft I/O tasks, which can be adjusted when tuning TiKV performance. Before v6.6.0, this configuration item cannot be modified dynamically. Starting from v6.6.0, you can modify this configuration without restarting the server, which means more flexible performance tuning.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/dynamic-config).

* Support specifying the SQL script executed upon TiDB cluster initialization [#35624](https://github.com/pingcap/tidb/issues/35624) @[morgo](https://github.com/morgo)

    When you start a TiDB cluster for the first time, you can specify the SQL script to be executed by configuring the command line parameter `--initialize-sql-file`. You can use this feature when you need to perform such operations as modifying the value of a system variable, creating a user, or granting privileges.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#initialize-sql-file-new-in-v660).

* TiDB Data Migration (DM) integrates with TiDB Lightning's physical import mode for up to a 10x performance boost for full migration (experimental) @[lance6716](https://github.com/lance6716)

    In v6.6.0, DM full migration capability integrates with physical import mode of TiDB Lightning, which enables DM to improve the performance of full data migration by up to 10 times, greatly reducing the migration time in large data volume scenarios.

    Before v6.6.0, for large data volume scenarios, you were required to configure physical import tasks in TiDB Lightning separately for fast full data migration, and then use DM for incremental data migration, which was a complex configuration. Starting from v6.6.0, you can migrate large data volumes without the need to configure TiDB Lightning tasks; one DM task can accomplish the migration.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/dm/dm-precheck#check-items-for-physical-import).

* TiDB Lightning adds a new configuration parameter `"header-schema-match"` to address the issue of mismatched column names between the source file and the target table @[dsdashun](https://github.com/dsdashun)

    In v6.6.0, TiDB Lightning adds a new profile parameter `"header-schema-match"`. The default value is `true`, which means the first row of the source CSV file is treated as the column name, and consistent with that in the target table. If the field name in the CSV table header does not match the column name of the target table, you can set this configuration to `false`. TiDB Lightning will ignore the error and continue to import the data in the order of the columns in the target table.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task).

* TiDB Lightning supports enabling compressed transfers when sending key-value pairs to TiKV [#41163](https://github.com/pingcap/tidb/issues/41163) @[sleepymole](https://github.com/sleepymole)

    Starting from v6.6.0, TiDB Lightning supports compressing locally encoded and sorted key-value pairs for network transfer when sending them to TiKV, thus reducing the amount of data transferred over the network and lowering the network bandwidth overhead. In the earlier TiDB versions before this feature is supported, TiDB Lightning requires relatively high network bandwidth and incurs high traffic charges in case of large data volumes.

    This feature is disabled by default. To enable it, you can set the `compress-kv-pairs` configuration item of TiDB Lightning to `"gzip"` or `"gz"`.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task).

* The TiKV-CDC tool is now GA and supports subscribing to data changes of RawKV [#48](https://github.com/tikv/migration/issues/48) @[zeminzhou](https://github.com/zeminzhou) @[haojinming](https://github.com/haojinming) @[pingyu](https://github.com/pingyu)

    TiKV-CDC is a CDC (Change Data Capture) tool for TiKV clusters. TiKV and PD can constitute a KV database when used without TiDB, which is called RawKV. TiKV-CDC supports subscribing to data changes of RawKV and replicating them to a downstream TiKV cluster in real time, thus enabling cross-cluster replication of RawKV.

    For more information, see [documentation](https://tikv.org/docs/latest/concepts/explore-tikv-features/cdc/cdc/).

* TiCDC supports scaling out a single table on Kafka changefeeds and distributing the changefeed to multiple TiCDC nodes (experimental) [#7720](https://github.com/pingcap/tiflow/issues/7720) @[overvenus](https://github.com/overvenus)

    Before v6.6.0, when a table in the upstream accepts a large amount of writes, the replication capability of this table cannot be scaled out, resulting in an increase in the replication latency. Starting from TiCDC v6.6.0. the changefeed of an upstream table can be distributed to multiple TiCDC nodes in a Kafka sink, which means the replication capability of a single table is scaled out.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#scale-out-the-load-of-a-single-large-table-to-multiple-ticdc-nodes).

* [GORM](https://github.com/go-gorm/gorm) adds TiDB integration tests. Now TiDB is the default database supported by GORM. [#6014](https://github.com/go-gorm/gorm/pull/6014) @[Icemap](https://github.com/Icemap)

    - In v1.4.6, [GORM MySQL driver](https://github.com/go-gorm/mysql) adapts to the `AUTO_RANDOM` attribute of TiDB [#104](https://github.com/go-gorm/mysql/pull/104)
    - In v1.4.6, [GORM MySQL driver](https://github.com/go-gorm/mysql) fixes the issue that when connecting to TiDB, the `Unique` attribute of the `Unique` field cannot be modified during `AutoMigrate` [#105](https://github.com/go-gorm/mysql/pull/105)
    - [GORM documentation](https://github.com/go-gorm/gorm.io) mentions TiDB as the default database [#638](https://github.com/go-gorm/gorm.io/pull/638)

    For more information, see [GORM documentation](https://gorm.io/docs/index.html).
