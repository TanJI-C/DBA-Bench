# PD metadata usage, large transaction risks, and lossy DDL behavior

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-faq.md`
- Source Title: `TiCDC FAQs`
- Source Heading Path: `TiCDC FAQs > How much PD storage does TiCDC use? | TiCDC FAQs > Does TiCDC support replicating large transactions? Is there any risk? | TiCDC FAQs > Does TiCDC replicate data changes caused by lossy DDL operations to the downstream?`
- Source Line Ranges: `293-335`
- Source Scope: `shared`
- Primary Component: `ticdc`
- Related Components: `pd`, `br`
- Topic Tags: `etcd`, `metadata`, `storage-space`, `large-transactions`, `oom`, `checkpoint-ts`, `incremental-backup`, `lossy-ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0252_554d1e6da8`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-faq.md#how-much-pd-storage-does-ticdc-use`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a21a5cb0d350ab812c37725e268f1aaed56aab888fc635b8dae930504ae36165`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq#how-much-pd-storage-does-ticdc-use
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-faq.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiCDC metadata usage in PD/etcd, risks from large transactions, BR-based recovery using `checkpoint-ts` and `BackupTS`, or how lossy DDL affects downstream replication.
- Retrieval Keywords: etcdserver: mvcc: database space exceeded, PD storage, etcd, MVCC, compaction interval, metadata for all tables in a changefeed, v6.0.0, large transactions more than 5 GB, ErrBufferReachLimit, OOM, transaction-atomicity, none, checkpoint-ts, --lastbackupts, BackupTS, BR incremental backup, lossy DDL, redundant DML events, v7.1.0, Kafka, cloud storage service
- Follow-up Guidance: If the issue is `etcdserver: mvcc: database space exceeded`, the content points to etcd maintenance space-quota, and for large-transaction recovery it outlines BR incremental backup and restore steps using `checkpoint-ts` and `BackupTS`.
- Classification Note: This is classified as operation because the content describes runtime storage errors, replication risk conditions, recovery workflow with BR, and version-specific behavior for lossy DDL replication.

## Official Source Content

## How much PD storage does TiCDC use?

When using TiCDC, you might encounter the `etcdserver: mvcc: database space exceeded` error, which is primarily related to the mechanism that TiCDC uses etcd in PD to store metadata.

etcd uses Multi-Version Concurrency Control (MVCC) to store data, and the default compaction interval in PD is 1 hour. This means that etcd retains multiple versions of all data for 1 hour before compaction.

Before v6.0.0, TiCDC uses etcd in PD to store and update metadata for all tables in a changefeed. Therefore, the PD storage space used by TiCDC is proportional to the number of tables being replicated by the changefeed. When TiCDC is replicating a large number of tables, the etcd storage space could fill up quickly, increasing the probability of the `etcdserver: mvcc: database space exceeded` error.

If you encounter this error, refer to [etcd maintenance space-quota](https://etcd.io/docs/v3.4.0/op-guide/maintenance/#space-quota) to clean up the etcd storage space.

Starting from v6.0.0, TiCDC optimizes its metadata storage mechanism, effectively avoiding the etcd storage space issues caused by the preceding reasons. If your TiCDC version is earlier than v6.0.0, it is recommended to upgrade to v6.0.0 or later versions.
## Does TiCDC support replicating large transactions? Is there any risk?

TiCDC provides partial support for large transactions (more than 5 GB in size). Depending on different scenarios, the following risks might exist:

- The latency of primary-secondary replication might greatly increase.
- When TiCDC's internal processing capacity is insufficient, the replication task error `ErrBufferReachLimit` might occur.
- When TiCDC's internal processing capacity is insufficient or the throughput capacity of TiCDC's downstream is insufficient, out of memory (OOM) might occur.

Since v6.2, TiCDC supports splitting a single-table transaction into multiple transactions. This can greatly reduce the latency and memory consumption of replicating large transactions. Therefore, if your application does not have a high requirement on transaction atomicity, it is recommended to enable the splitting of large transactions to avoid possible replication latency and OOM. To enable the splitting, set the value of the sink uri parameter [`transaction-atomicity`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-mysql#configure-sink-uri-for-mysql-or-tidb) to `none`.

If you still encounter an error above, it is recommended to use BR to restore the incremental data of large transactions. The detailed operations are as follows:

1. Record the `checkpoint-ts` of the changefeed that is terminated due to large transactions, use this TSO as the `--lastbackupts` of the BR incremental backup, and execute [incremental data backup](https://docs.pingcap.com/tidb/stable/br/br-incremental-guide#back-up-incremental-data).
2. After backing up the incremental data, you can find a log record similar to `["Full backup Failed summary : total backup ranges: 0, total success: 0, total failed: 0"] [BackupTS=421758868510212097]` in the BR log output. Record the `BackupTS` in this log.
3. [Restore the incremental data](https://docs.pingcap.com/tidb/stable/br/br-incremental-guide#restore-incremental-data).
4. Create a new changefeed and start the replication task from `BackupTS`.
5. Delete the old changefeed.
## Does TiCDC replicate data changes caused by lossy DDL operations to the downstream?

Lossy DDL refers to DDL that might cause data changes when executed in TiDB. Some common lossy DDL operations include:

- Modifying the type of a column, for example, INT -> VARCHAR
- Modifying the length of a column, for example, VARCHAR(20) -> VARCHAR(10)
- Modifying the precision of a column, for example, DECIMAL(10, 3) -> DECIMAL(10, 2)
- Modifying the UNSIGNED or SIGNED attribute of a column, for example, INT UNSIGNED -> INT SIGNED

Before TiDB v7.1.0, TiCDC replicates DML events with identical old and new data to the downstream. When the downstream is MySQL, these DML events do not cause any data changes until the downstream receives and executes the DDL statement. However, when the downstream is Kafka or a cloud storage service, TiCDC writes a row of redundant data to the downstream.

Starting from TiDB v7.1.0, TiCDC eliminates these redundant DML events and no longer replicates them to downstream.
