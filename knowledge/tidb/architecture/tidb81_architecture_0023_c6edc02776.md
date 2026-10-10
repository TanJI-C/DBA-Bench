# DM DML execution, workers, batching, and checkpoint

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-replication-logic.md`
- Source Title: `DML Replication Mechanism in Data Migration`
- Source Heading Path: `DML Replication Mechanism in Data Migration > DML execution logic | DML Replication Mechanism in Data Migration > DML execution logic > DML generation | DML Replication Mechanism in Data Migration > DML execution logic > Worker count | DML Replication Mechanism in Data Migration > DML execution logic > Batch | DML Replication Mechanism in Data Migration > DML execution logic > checkpoint`
- Source Line Ranges: `90-131`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `dml-execution`, `schema-tracker`, `ddl`, `worker-count`, `concurrency`, `batch`, `transactions`, `checkpoint`, `binlog-position`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0023_c6edc02776`
- Source ID: `tidb-docs-8.1:dm/dm-replication-logic.md#dml-execution-logic`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b3f31b5b52dd050734c0596c1f2e5c6a00d8abe7b48ee1744bc43a3ab56107be`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-replication-logic#dml-execution-logic
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-replication-logic.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how DM generates and executes DML, how `worker-count` and `batch` affect concurrent execution, or how checkpoint progress is calculated.
- Retrieval Keywords: DML execution logic, DML generation, schema tracker, embedded schema tracker, DDL statement, upstream table structure, downstream primary key or unique key, WHERE condition, worker-count, syncer.worker-count, Batch, syncer.batch, single transaction, DML worker, checkpoint, updated every 30 seconds by default, earliest replication progress, binlog position
- Follow-up Guidance: It explains that Sync uses the table structure exported during upstream full data migration for full and incremental task startup, and for incremental task startup it uses the corresponding downstream table structure because MySQL binlog does not record table structure information.
- Classification Note: This is classified as architecture because it explains the internal execution logic of DM, including schema tracking, concurrent workers, batching, and checkpoint calculation.

## Official Source Content

## DML execution logic

After the Sync unit optimizes the DML, it performs the execution logic.
### DML generation

DM has an embedded schema tracker that records the schema information of the upstream and downstream:

* When DM receives a DDL statement, DM updates the table schema of the internal schema tracker.
* When DM receives a DML statement, DM generates the corresponding DML according to the table schema of the schema tracker.

The logic of generating DML is as follows:

1. The Sync unit records the initial table structure of the upstream:
    * When starting a full and incremental task, Sync uses the **table structure exported during the upstream full data migration** as the initial table structure of the upstream.
    * When starting an incremental task, because MySQL binlog does not record the table structure information, Sync uses the **table structure of the corresponding table in the downstream** as the initial table structure of the upstream.
2. The user's upstream and downstream table structures might be inconsistent, for example, the downstream might have additional columns than the upstream, or the upstream and downstream primary keys are inconsistent. Therefore, to ensure the correctness of data replication, DM records the **primary key and unique key information of the corresponding table in the downstream**.
3. DM generates DML:
    * Use the **the upstream table structure recorded in the schema tracker** to generate the column names of the DML statement.
    * Use the **column values recorded in the binlog** to generate the column values of the DML statement.
    * Use the **downstream primary key or unique key recorded in the schema tracker** to generate the `WHERE` condition of the DML statement. When the table structure has no unique key, DM uses all the column values recorded in the binlog as the `WHERE` condition.
### Worker count

Causality can divide binlog into multiple groups through conflict detection and execute them concurrently to the downstream. DM controls the concurrency by setting `worker-count`. When the CPU usage of the downstream TiDB is not high, increasing the concurrency can effectively improve the throughput of data replication.

You can modify the number of threads that concurrently migrate DML by modifying the [`syncer.worker-count` configuration item](https://docs.pingcap.com/tidb/stable/dm/dm-tune-configuration#worker-count).
### Batch

DM batches multiple DMLs into a single transaction and executes it to the downstream. When a DML worker receives a DML, it adds the DML to the cache. When the number of DMLs in the cache reaches the preset threshold, or the DML worker does not receive DML for a long time, the DML worker executes the DMLs in the cache to the downstream.

You can modify the number of DMLs contained in a transaction by modifying the [`syncer.batch` configuration item](https://docs.pingcap.com/tidb/stable/dm/dm-tune-configuration#batch).
### checkpoint

The operation of executing DML and updating checkpoint is not atomic.

In DM, checkpoint is updated every 30 seconds by default. Because there are multiple DML worker processes, the checkpoint process calculates the binlog position of the earliest replication progress of all DML workers, and uses this position as the current replication checkpoint. All binlogs earlier than this position are guaranteed to be successfully executed to the downstream.

<!-- For details on checkpoint mechanism, refer to Checkpoint /dm/dm-checkpoint.md -->
