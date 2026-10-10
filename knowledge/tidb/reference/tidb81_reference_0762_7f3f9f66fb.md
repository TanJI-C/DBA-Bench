# TiCDC compatibility overview and feature/configuration constraints

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-compatibility.md`
- Source Title: `TiCDC Compatibility`
- Source Heading Path: `TiCDC Compatibility | TiCDC Compatibility > Compatibility with TiDB Lightning | TiCDC Compatibility > Compatibility with TiFlash | TiCDC Compatibility > CLI and configuration file compatibility | TiCDC Compatibility > Handle compatibility issues`
- Source Line Ranges: `5-48`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `lightning`, `tiflash`, `tidb`, `tikv`
- Topic Tags: `compatibility`, `logical-import`, `physical-import`, `changefeed`, `replication`, `tiflash-ddl`, `cli`, `configuration`, `deprecated-parameters`, `syncpoint`, `privileges`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0762_7f3f9f66fb`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-compatibility.md#ticdc-compatibility`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fc9762d66a0c74d5328e63abd68602e2eba52b7a1886356303d47a83801f2229`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-compatibility#ticdc-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-compatibility.md

## Retrieval Guidance

- Use When: Use this chunk when checking whether TiCDC works with TiDB Lightning import modes, TiFlash-related DDL, or changed TiCDC CLI and configuration parameters and privileges.
- Retrieval Keywords: TiCDC Compatibility, TiDB Lightning logical import mode, TiDB Lightning physical import mode, changefeed, replicate subsequent incremental data written through SQL, TiFlash-related DDL, ALTER TABLE table_name SET TIFLASH REPLICA count;, ALTER DATABASE db_name SET TIFLASH REPLICA count;, ignore-txn-commit-ts, ignore-txn-start-ts, db-dbs, db-tables, ignore-dbs, ignore-tables, rules, Table Filter, cdc cli, TiCDC Open API, --server, --pd is deprecated, SYSTEM_VARIABLES_ADMIN, SUPER, TiCDC Syncpoint
- Follow-up Guidance: If physical import mode is involved, the source distinguishes between downstream TiDB clusters and non-TiDB downstream systems before creating a changefeed for subsequent incremental data written through SQL.
- Classification Note: The official content is a compatibility reference covering supported and unsupported combinations, parameter deprecations and replacements, and privilege requirements for TiCDC features.

## Official Source Content

# TiCDC Compatibility

This section describes compatibility issues related to TiCDC and how to handle them.
## Compatibility with TiDB Lightning

[TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview) provides two data import modes: [logical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-logical-import-mode) and [physical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode). This section describes the compatibility of these modes with TiCDC and the steps to use TiDB Lightning and TiCDC together in a cluster.

In the logical import mode, TiDB Lightning imports data by executing SQL statements. This mode is compatible with TiCDC. To use TiDB Lightning's logical import mode with TiCDC for data replication, perform the following steps:

1. Create a changefeed. For more information, see [Create a replication task](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed#create-a-replication-task).
2. Start TiDB Lightning and import data using the logical import mode. For more information, see [Use logical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-logical-import-mode-usage).

In the physical import mode, TiDB Lightning imports data by inserting SST files into TiKV. TiCDC is not compatible with this mode and does not support replicating data imported through physical import mode. If you need to use both TiDB Lightning's physical import mode and TiCDC, choose one of the following solutions based on your downstream system:

- If the downstream is a TiDB cluster, perform the following steps:

    1. Use TiDB Lightning to import data into both the upstream and downstream TiDB clusters to ensure data consistency.
    2. Create a changefeed to replicate subsequent incremental data written through SQL. For more information, see [Create a replication task](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed#create-a-replication-task).

- If the downstream is not a TiDB cluster, perform the following steps:

    1. Use the offline import tool provided by your downstream system to import TiDB Lightning's input files.
    2. Create a changefeed to replicate subsequent incremental data written through SQL. For more information, see [Create a replication task](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed#create-a-replication-task).
## Compatibility with TiFlash

Currently, when you use TiCDC to replicate tables to a downstream TiDB cluster, creating TiFlash replicas for the tables is not supported, which means that TiCDC does not support replicating TiFlash-related DDL statements, such as:

* `ALTER TABLE table_name SET TIFLASH REPLICA count;`
* `ALTER DATABASE db_name SET TIFLASH REPLICA count;`
## CLI and configuration file compatibility

* In TiCDC v4.0.0, `ignore-txn-commit-ts` is removed and `ignore-txn-start-ts` is added, which uses start_ts to filter transactions.
* In TiCDC v4.0.2, `db-dbs`/`db-tables`/`ignore-dbs`/`ignore-tables` are removed and `rules` is added, which uses new filter rules for databases and tables. For detailed filter syntax, see [Table Filter](https://docs.pingcap.com/tidb/stable/table-filter).
* Starting from TiCDC v6.2.0, `cdc cli` can directly interact with TiCDC server via TiCDC Open API. You can specify the address of the TiCDC server using the `--server` parameter. `--pd` is deprecated.
* Since v6.4.0, only the changefeed with the `SYSTEM_VARIABLES_ADMIN` or `SUPER` privilege can use the TiCDC Syncpoint feature.
## Handle compatibility issues

This section describes compatibility issues related to TiCDC and how to handle them.
