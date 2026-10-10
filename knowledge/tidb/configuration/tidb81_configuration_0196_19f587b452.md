# Drainer configuration for enabling bidirectional replication

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/bidirectional-replication-between-tidb-clusters.md`
- Source Title: `Bidirectional Replication Between TiDB Clusters`
- Source Heading Path: `Bidirectional Replication between TiDB Clusters > Configure and enable bidirectional replication`
- Source Line Ranges: `86-132`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `drainer`, `configuration`, `loopback-control`, `channel-id`, `sync-ddl`, `sync-mode`, `ignore-table`, `checkpoint`, `partial-column-sync`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0196_19f587b452`
- Source ID: `tidb-docs-8.1:tidb-binlog/bidirectional-replication-between-tidb-clusters.md#configure-and-enable-bidirectional-replication`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `84420dce971851a3f3867caaad808ec6045e380959bc0d689e82140f64a90125`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/bidirectional-replication-between-tidb-clusters#configure-and-enable-bidirectional-replication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/bidirectional-replication-between-tidb-clusters.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact Drainer configuration examples to enable bidirectional replication between cluster A and cluster B, including different `sync-ddl` settings by replication direction.
- Retrieval Keywords: Configure and enable bidirectional replication, Drainer configuration, [syncer], loopback-control = true, channel-id = 1, sync-ddl = true, sync-ddl = false, [syncer.to], sync-mode = 2, SyncFullColumn, SyncPartialColumn, STRICT_TRANS_TABLES, [[syncer.ignore-table]], db-name = "tidb_binlog", tbl-name = "checkpoint", Ignores the checkpoint table
- Follow-up Guidance: The source pairs these examples with the assumption that all DDL operations are executed on cluster A, so the A to B path enables `sync-ddl` and the B to A path disables it.
- Classification Note: This chunk is classified as configuration because it consists of concrete Drainer TOML settings for bidirectional replication, including loopback control, channel ID, DDL sync, sync mode, and ignored tables.

## Official Source Content

## Configure and enable bidirectional replication

For bidirectional replication between cluster A and cluster B, assume that all DDL operations are executed on cluster A. On the replication path from cluster A to cluster B, add the following configuration to Drainer:

```toml
[syncer]
loopback-control = true
channel-id = 1 # Configures the same ID for both clusters to be replicated.
sync-ddl = true # Enables it if you need to perform DDL replication.

[syncer.to]
# 1 means SyncFullColumn and 2 means SyncPartialColumn.
# If set to SyncPartialColumn, Drainer allows the downstream table
# structure to have more or fewer columns than the data to be replicated
# And remove the STRICT_TRANS_TABLES of the SQL mode to allow fewer columns, and insert zero values to the downstream.
sync-mode = 2

# Ignores the checkpoint table.
[[syncer.ignore-table]]
db-name = "tidb_binlog"
tbl-name = "checkpoint"
```

On the replication path from cluster B to cluster A, add the following configuration to Drainer:

```toml
[syncer]
loopback-control = true
channel-id = 1 # Configures the same ID for both clusters to be replicated.
sync-ddl = false  # Disables it if you do not need to perform DDL replication.

[syncer.to]
# 1 means SyncFullColumn and 2 means SyncPartialColumn.
# If set to SyncPartialColumn, Drainer allows the downstream table
# structure to have more or fewer columns than the data to be replicated
# And remove the STRICT_TRANS_TABLES of the SQL mode to allow fewer columns, and insert zero values to the downstream.
sync-mode = 2

# Ignores the checkpoint table.
[[syncer.ignore-table]]
db-name = "tidb_binlog"
tbl-name = "checkpoint"
```
