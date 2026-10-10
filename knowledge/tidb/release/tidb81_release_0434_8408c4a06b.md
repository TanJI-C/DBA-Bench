# Feature details for SQL, DB operations, and data migration

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.0.0.md`
- Source Title: `TiDB 7.0.0 Release Notes`
- Source Heading Path: `TiDB 7.0.0 Release Notes > Feature details > SQL | TiDB 7.0.0 Release Notes > Feature details > DB operations | TiDB 7.0.0 Release Notes > Feature details > Data migration`
- Source Line Ranges: `214-278`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `sql`, `ticdc`, `lightning`, `tikv`, `ecosystem`
- Topic Tags: `ttl`, `partitioning`, `reorganize-partition`, `ticdc`, `openapi`, `cloud-storage`, `load-data`, `data-import`, `compressed-transfer`, `dbeaver`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0434_8408c4a06b`
- Source ID: `tidb-docs-8.1:releases/release-7.0.0.md#sql`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `44184f7b75b3261a25515ef06e4650affbfe0eedd48e6057f547e841f3158742`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.0.0#sql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 7.0.0 release details about new SQL, DB operations, or data migration capabilities such as TTL, partition reorganization, TiCDC storage sinks, OpenAPI v2, `LOAD DATA` from cloud storage, or TiDB Lightning compressed transfer.
- Retrieval Keywords: TiDB 7.0.0 Release Notes, Time to live (TTL), row-level lifecycle control policies, ALTER TABLE...REORGANIZE PARTITION, Key partitioning, TiCDC supports replicating change data to storage services, Amazon S3, GCS, Azure Blob Storage, NFS, S3-compatible storage services, canal-json, CSV formats, TiCDC OpenAPI v2, cdc cli, getting TiCDC node status, checking cluster health status, managing replication tasks, DBeaver v23.0.1 supports TiDB by default, EXPLAIN results, TiDB keywords REORGANIZE EXCHANGE CACHE NONCLUSTERED CLUSTERED, TIDB_BOUNDED_STALENESS, TIDB_DECODE_KEY, TIDB_DECODE_PLAN, TIDB_IS_DDL_OWNER, TIDB_PARSE_TSO, TIDB_VERSION, TIDB_DECODE_SQL_DIGESTS, TIDB_SHARD, LOAD DATA, importing data from cloud storage, Amazon S3 and Google Cloud Storage, wildcards, DEFINED NULL BY, CSV and TSV formats, TiDB Lightning, compressed transfers, sending key-value pairs to TiKV, compress-kv-pairs, gzip, gz
- Follow-up Guidance: The source points to related documentation for TTL, partitioned tables, TiCDC cloud storage sink, TiCDC OpenAPI v2, `LOAD DATA`, and TiDB Lightning configuration.
- Classification Note: This is classified as a release chunk because it lists TiDB 7.0.0 feature details across SQL, DB operations, and data migration.

## Official Source Content

### SQL

* Time to live (TTL) is generally available [#39262](https://github.com/pingcap/tidb/issues/39262) @[lcwangchao](https://github.com/lcwangchao) @[YangKeao](https://github.com/YangKeao)

    TTL provides row-level lifecycle control policies. In TiDB, tables with TTL attributes set automatically check and delete expired row data based on the configuration. The goal of TTL is to help users periodically clean up unnecessary data in time while minimizing the impact on cluster workloads.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/time-to-live).

* Support `ALTER TABLE…REORGANIZE PARTITION` [#15000](https://github.com/pingcap/tidb/issues/15000) @[mjonss](https://github.com/mjonss)

    TiDB supports the `ALTER TABLE...REORGANIZE PARTITION` syntax. Using this syntax, you can reorganize some or all of the partitions of a table, including merging, splitting, or other modifications, without losing data.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/partitioned-table#reorganize-partitions).

* Support Key partitioning [#41364](https://github.com/pingcap/tidb/issues/41364) @[TonsnakeLin](https://github.com/TonsnakeLin)

    Now TiDB supports Key partitioning. Both Key partitioning and Hash partitioning can evenly distribute data into a certain number of partitions. The difference is that Hash partitioning only supports distributing data based on a specified integer expression or an integer column, while Key partitioning supports distributing data based on a column list, and partitioning columns of Key partitioning are not limited to the integer type.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/partitioned-table#key-partitioning).
### DB operations

* TiCDC supports replicating change data to storage services (GA) [#6797](https://github.com/pingcap/tiflow/issues/6797) @[zhaoxinyu](https://github.com/zhaoxinyu)

    TiCDC supports replicating changed data to Amazon S3, GCS, Azure Blob Storage, NFS, and other S3-compatible storage services. Storage services are reasonably priced and easy to use. If you are not using Kafka, you can use storage services. TiCDC saves the changed logs to a file and then sends it to the storage services instead. From the storage services, your own consumer program can read the newly generated changed log files periodically. Currently, TiCDC supports replicating changed logs in canal-json and CSV formats to the storage service.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-cloud-storage).

* TiCDC OpenAPI v2 [#8019](https://github.com/pingcap/tiflow/issues/8019) @[sdojjy](https://github.com/sdojjy)

    TiCDC provides OpenAPI v2. Compared with OpenAPI v1, OpenAPI v2 provides more comprehensive support for replication tasks. The features provided by TiCDC OpenAPI are a subset of the [`cdc cli` tool](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed). You can query and operate TiCDC clusters via OpenAPI v2, such as getting TiCDC node status, checking cluster health status, and managing replication tasks.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api-v2).

* [DBeaver](https://dbeaver.io/) v23.0.1 supports TiDB by default [#17396](https://github.com/dbeaver/dbeaver/issues/17396) @[Icemap](https://github.com/Icemap)

    - Provides an independent TiDB module, icon, and logo.
    - The default configuration supports [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter), making it easier to connect to {{{ .starter }}}.
    - Supports identifying TiDB versions to display or hide foreign key tabs.
    - Supports visualizing SQL execution plans in `EXPLAIN` results.
    - Supports highlighting TiDB keywords such as `PESSIMISTIC`, `OPTIMISTIC`, `AUTO_RANDOM`, `PLACEMENT`, `POLICY`, `REORGANIZE`, `EXCHANGE`, `CACHE`, `NONCLUSTERED`, and `CLUSTERED`.
    - Supports highlighting TiDB functions such as  `TIDB_BOUNDED_STALENESS`, `TIDB_DECODE_KEY`, `TIDB_DECODE_PLAN`, `TIDB_IS_DDL_OWNER`, `TIDB_PARSE_TSO`, `TIDB_VERSION`, `TIDB_DECODE_SQL_DIGESTS`, and `TIDB_SHARD`.

  For more information, see [DBeaver documentation](https://github.com/dbeaver/dbeaver/wiki).
### Data migration

* Enhance the functionalities of `LOAD DATA` statements and support importing data from cloud storage (experimental) [#40499](https://github.com/pingcap/tidb/issues/40499) @[lance6716](https://github.com/lance6716)

    Before TiDB v7.0.0, the `LOAD DATA` statement could only import data files from the client side. If you wanted to import data from cloud storage, you had to rely on TiDB Lightning. However, deploying TiDB Lightning separately would bring additional deployment and management costs. In v7.0.0, you can directly import data from cloud storage using the `LOAD DATA` statement. Some examples of the feature are as follows:

    - Supports importing data from Amazon S3 and Google Cloud Storage to TiDB. Supports importing multiple source files to TiDB in one go with wildcards.
    - Support using `DEFINED NULL BY` to define null.
    - Support source files in CSV and TSV formats.

  For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-data).

* TiDB Lightning supports enabling compressed transfers when sending key-value pairs to TiKV (GA) [#41163](https://github.com/pingcap/tidb/issues/41163) @[sleepymole](https://github.com/sleepymole)

    Starting from v6.6.0, TiDB Lightning supports compressing locally encoded and sorted key-value pairs for network transfer when sending them to TiKV, thus reducing the amount of data transferred over the network and lowering the network bandwidth overhead. In the earlier TiDB versions before this feature is supported, TiDB Lightning requires relatively high network bandwidth and incurs high traffic charges in case of large data volumes.

    In v7.0.0, this feature becomes GA and is disabled by default. To enable it, you can set the `compress-kv-pairs` configuration item of TiDB Lightning to `"gzip"` or `"gz"`.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task).
