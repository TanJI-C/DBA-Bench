# Bidirectional replication overview, mechanics, mark table, and DDL constraints

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/bidirectional-replication-between-tidb-clusters.md`
- Source Title: `Bidirectional Replication Between TiDB Clusters`
- Source Heading Path: `Bidirectional Replication between TiDB Clusters | Bidirectional Replication between TiDB Clusters > User scenario | Bidirectional Replication between TiDB Clusters > Implementation details | Bidirectional Replication between TiDB Clusters > Mark table | Bidirectional Replication between TiDB Clusters > Replicate DDL operations`
- Source Line Ranges: `5-85`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `bidirectional-replication`, `experimental`, `deprecation`, `conflict-free-writes`, `replication-loop`, `mark-table`, `binlog`, `drainer`, `channel-id`, `ddl-replication`, `one-way-replication`, `schema-change`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0072_01f4ae8302`
- Source ID: `tidb-docs-8.1:tidb-binlog/bidirectional-replication-between-tidb-clusters.md#bidirectional-replication-between-tidb-clusters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `93a8015d7d4ca09f360ff787efa8cfb7e46b9e0b5a3894183a8cf39e51954a4f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/bidirectional-replication-between-tidb-clusters#bidirectional-replication-between-tidb-clusters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/bidirectional-replication-between-tidb-clusters.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official overview of TiDB Binlog bidirectional replication, including loop prevention with `_drainer_repl_mark`, `channel_id`, conflict-free writes, and DDL replication limitations.
- Retrieval Keywords: bidirectional replication between TiDB clusters, TiDB Binlog experimental feature, technical support no longer provided starting from TiDB v7.5.0, TiCDC alternative solution for data replication, PITR alternative solution for data recovery, conflict-free writes, replication loop, Drainer marks the binlog events, _drainer_repl_mark, channel_id, same channel_id configuration, mark table, CREATE TABLE `_drainer_repl_mark`, update drainer_repl_mark set val = val + 1 where id = ? && channel_id = ?, DDL operations are not transactional, one-way replication method to replicate DDL operations, DDL operations cannot be executed on two clusters at the same time
- Follow-up Guidance: The source also provides a separate configuration section showing the Drainer settings for each replication path, including `loopback-control`, `channel-id`, `sync-ddl`, `sync-mode`, and `ignore-table` for `tidb_binlog.checkpoint`.
- Classification Note: This chunk is classified as architecture because it explains the bidirectional replication scenario, Drainer loopback filtering with the mark table, and the one-way handling of DDL operations.

## Official Source Content

# Bidirectional Replication between TiDB Clusters

> **Warning:**
>
> - Currently, bidirectional replication is still an experimental feature. It is **NOT** recommended to use it in the production environment.
> - TiDB Binlog is not compatible with some features introduced in TiDB v5.0 and they cannot be used together. For details, see [Notes](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-overview#notes).
> - Starting from TiDB v7.5.0, technical support for the data replication feature of TiDB Binlog is no longer provided. It is strongly recommended to use [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview) as an alternative solution for data replication.
> - Although TiDB v7.5.0 still supports the real-time backup and restoration feature of TiDB Binlog, this component will be completely deprecated in future versions. It is recommended to use [PITR](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide) as an alternative solution for data recovery.

This document describes the bidirectional replication between two TiDB clusters, how the replication works, how to enable it, and how to replicate DDL operations.
## User scenario

If you want two TiDB clusters to exchange data changes with each other, TiDB Binlog allows you to do that. For example, you want cluster A and cluster B to replicate data with each other.

> **Note:**
>
> The data written to these two clusters must be conflict-free, that is, in the two clusters, the same primary key or the rows with the unique index of the tables must not be modified.

The user scenario is shown as below:

![Architect](/media/binlog/bi-repl1.jpg)
## Implementation details

![Mark Table](/media/binlog/bi-repl2.png)

If the bidirectional replication is enabled between cluster A and cluster B, the data written to cluster A will be replicated to cluster B, and then these data changes will be replicated back to cluster A, which causes an infinite loop of replication. From the figure above, you can see that during the data replication, Drainer marks the binlog events, and filters out the marked events to avoid such a replication loop.

The detailed implementation is described as follows:

1. Start the TiDB Binlog replication program for each of the two clusters.
2. When the transaction to be replicated passes through the Drainer of cluster A, this Drainer adds the [`_drainer_repl_mark` table](#mark-table) to the transaction, writes this DML event update to the mark table, and replicate this transaction to cluster B.
3. Cluster B returns binlog events with the `_drainer_repl_mark` mark table to cluster A. The Drainer of cluster B identifies the mark table with the DML event when parsing the binlog event, and gives up replicating this binlog event to cluster A.

The replication process from cluster B to cluster A is the same as above. The two clusters can be upstream and downstream of each other.

> **Note:**
>
> * When updating the `_drainer_repl_mark` mark table, data changes are required to generate binlogs.
> * DDL operations are not transactional, so you need to use the one-way replication method to replicate DDL operations. See [Replicate DDL operations](#replicate-ddl-operations) for details.

Drainer can use a unique ID for each connection to downstream to avoid conflicts. `channel_id` is used to indicate a channel for bidirectional replication. The two clusters should have the same `channel_id` configuration (with the same value).

If you add or delete columns in the upstream, there might be extra or missing columns of the data to be replicated to the downstream. Drainer allows this situation by ignoring the extra columns or by inserting default values to the missing columns.
## Mark table

The `_drainer_repl_mark` mark table has the following structure:

```sql
CREATE TABLE `_drainer_repl_mark` (
  `id` bigint(20) NOT NULL,
  `channel_id` bigint(20) NOT NULL DEFAULT '0',
  `val` bigint(20) DEFAULT '0',
  `channel_info` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`,`channel_id`)
);
```

Drainer uses the following SQL statement to update `_drainer_repl_mark`, which ensures data change and the generation of binlog:

```sql
update drainer_repl_mark set val = val + 1 where id = ? && channel_id = ?;
```
## Replicate DDL operations

Because Drainer cannot add the mark table to DDL operations, you can only use the one-way replication method to replicate DDL operations.

For example, if DDL replication is enabled from cluster A to cluster B, then the replication is disabled from cluster B to cluster A. This means that all DDL operations are performed on cluster A.

> **Note:**
>
> DDL operations cannot be executed on two clusters at the same time. When a DDL operation is executed, if any DML operation is being executed at the same time or any DML binlog is being replicated, the upstream and downstream table structures of the DML replication might be inconsistent.
