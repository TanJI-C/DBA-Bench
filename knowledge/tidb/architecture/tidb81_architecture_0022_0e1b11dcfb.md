# DM DML processing flow and optimization stages

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-replication-logic.md`
- Source Title: `DML Replication Mechanism in Data Migration`
- Source Heading Path: `DML Replication Mechanism in Data Migration | DML Replication Mechanism in Data Migration > DML processing flow | DML Replication Mechanism in Data Migration > DML optimization logic | DML Replication Mechanism in Data Migration > DML optimization logic > Compactor | DML Replication Mechanism in Data Migration > DML optimization logic > Causality | DML Replication Mechanism in Data Migration > DML optimization logic > Merger`
- Source Line Ranges: `5-89`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `dml`, `replication-flow`, `binlog`, `filtering`, `routing`, `expression-filter`, `compactor`, `causality`, `merger`, `optimization`, `concurrency`, `batching`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0022_0e1b11dcfb`
- Source ID: `tidb-docs-8.1:dm/dm-replication-logic.md#dml-replication-mechanism-in-data-migration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ef96c886f977508393076859af03a92950c9c08b09a4911bc566b95c56c0b45c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-replication-logic#dml-replication-mechanism-in-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-replication-logic.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how the DM Sync unit processes and optimizes DML from binlog reading through filtering, routing, compaction, causality, merger, execution, and checkpoint saving.
- Retrieval Keywords: DML processing flow, Sync unit, binlog filter, filters, table routing, routes, expression filter, expression-filter, Compactor, syncer.compact, Causality, Merger, syncer.multiple-rows, merge multiple operations on the same record, conflict detection, merge multiple binlog events into one DML, binlog position or GTID, checkpoint
- Follow-up Guidance: It also includes example transformations for Compactor and Merger and shows that `syncer.compact` and `syncer.multiple-rows` are disabled by default and can be enabled in the `sync` configuration module.
- Classification Note: This is classified as architecture because it describes the end-to-end DML replication flow in DM and the roles of optimization stages inside the Sync unit.

## Official Source Content

# DML Replication Mechanism in Data Migration

This document introduces how the core processing unit Sync in DM processes DML statements read from the data source or relay log. This document introduces the complete processing flow of DML events in DM, including the logic of binlog reading, filtering, routing, transformation, optimization, and execution. This document also explains the DML optimization logic and DML execution logic in detail.
## DML processing flow

The Sync unit processes DML statements as follows:

1. Read the binlog event from the MySQL, MariaDB, or relay log.
2. Transform the binlog event read from the data source:

    1. [Binlog filter](https://docs.pingcap.com/tidb/stable/dm/dm-binlog-event-filter): filter binlog events according to binlog expressions, configured by `filters`.
    2. [Table routing](https://docs.pingcap.com/tidb/stable/dm/dm-table-routing): transform the "database/table" name according to the "database/table" routing rule, configured by `routes`.
    3. [Expression filter](https://docs.pingcap.com/tidb/stable/filter-dml-event): filter binlog events according to SQL expressions, configured by `expression-filter`.

3. Optimize the DML execution plan:

    1. [Compactor](#compactor): merge multiple operations on the same record (with the same primary key) into one operation. This feature is enabled by `syncer.compact`.
    2. [Causality](#causality): perform conflict detection on different records (with different primary keys) to improve the concurrency of replication.
    3. [Merger](#merger): merge multiple binlog events into one DML statement, enabled by `syncer.multiple-rows`.

4. Execute the DML to the downstream.
5. Periodically save the binlog position or GTID to the checkpoint.

![DML processing logic](/media/dm/dm-dml-replication-logic.png)
## DML optimization logic

The Sync unit implements the DML optimization logic through three steps: Compactor, Causality, and Merger.
### Compactor

According to the binlog records of the upstream, DM captures the changes of the records and replicates them to the downstream. When the upstream makes multiple changes to the same record (`INSERT`/`UPDATE`/`DELETE`) in a short period of time, DM can compress multiple changes into one change through Compactor to reduce the pressure on the downstream and improve the throughput. For example:

```
INSERT + UPDATE => INSERT
INSERT + DELETE => DELETE
UPDATE + UPDATE => UPDATE
UPDATE + DELETE => DELETE
DELETE + INSERT => UPDATE
```

The Compactor feature is disabled by default. To enable it, you can set `syncer.compact` to `true` in the `sync` configuration module of the replication task, as shown below:

```yaml
syncers:                            # The configuration parameters of the sync processing unit
  global:                           # Configuration name
    ...                              # Other configurations are omitted
    compact: true
```
### Causality

The sequential replication model of MySQL binlog requires that binlog events be replicated in the order of binlog. This replication model cannot meet the requirements of high QPS and low replication latency. In addition, because not all operations involved in binlog have conflicts, sequential replication is not necessary in those cases.

DM recognizes the binlog that needs to be executed sequentially through conflict detection, and ensures that these binlog are executed sequentially while maximizing the concurrency of other binlog. This helps improve the performance of binlog replication.

Causality adopts an algorithm similar to the union-find algorithm to classify each DML and group DMLs that are related to each other.
### Merger

According to the MySQL binlog protocol, each binlog corresponds to a change operation of one row of data. Through Merger, DM can merge multiple binlogs into one DML and execute it to the downstream, reducing the network interaction. For example:

```
  INSERT tb(a,b) VALUES(1,1);
+ INSERT tb(a,b) VALUES(2,2);
= INSERT tb(a,b) VALUES(1,1),(2,2);
  UPDATE tb SET a=1, b=1 WHERE a=1;
+ UPDATE tb SET a=2, b=2 WHERE a=2;
= INSERT tb(a,b) VALUES(1,1),(2,2) ON DUPLICATE UPDATE a=VALUES(a), b=VALUES(b)
  DELETE tb WHERE a=1
+ DELETE tb WHERE a=2
= DELETE tb WHERE (a) IN (1),(2);
```

The Merger feature is disabled by default. To enable it, you can set `syncer.multiple-rows` to `true` in the `sync` configuration module of the replication task, as shown below:

```yaml
syncers:                            # The configuration parameters of the sync processing unit
  global:                           # Configuration name
    ...                              # Other configurations are omitted
    multiple-rows: true
```
