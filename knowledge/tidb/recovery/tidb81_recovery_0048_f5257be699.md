# TiDB Binlog FAQ: crash recovery, checkpoints, redeployment, and restore

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/tidb-binlog-faq.md`
- Source Title: `TiDB Binlog FAQs`
- Source Heading Path: `TiDB Binlog FAQs > What can I do if a Pump instance crashes? | TiDB Binlog FAQs > What is checkpoint? | TiDB Binlog FAQs > How to redeploy Drainer on the new machine when Drainer fails and the data in the downstream remains? | TiDB Binlog FAQs > How to restore the data of a cluster using a full backup and a binlog backup file? | TiDB Binlog FAQs > How to redeploy Drainer when enabling `ignore-error` in Primary-Secondary replication triggers a critical error?`
- Source Line Ranges: `75-144`
- Source Scope: `shared`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `sql`, `shared`
- Topic Tags: `pump`, `drainer`, `checkpoint`, `restore`, `full-backup`, `incremental-backup`, `reparo`, `initialcommitts`, `data-loss`, `redeployment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0048_f5257be699`
- Source ID: `tidb-docs-8.1:tidb-binlog/tidb-binlog-faq.md#what-can-i-do-if-a-pump-instance-crashes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5dd565a277dfff2725cab8353ba9d9e01f740ffad210b03aeebb651a316e6c38`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-faq#what-can-i-do-if-a-pump-instance-crashes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/tidb-binlog-faq.md

## Retrieval Guidance

- Use When: Use this chunk when recovering from a Pump crash, understanding checkpoint and `initialCommitTs`, redeploying Drainer, restoring from full backup plus binlog backup, or handling data loss after `ignore-error` triggers a critical error.
- Retrieval Keywords: Pump instance crashes, change the state of this Pump instance to `offline`, full and incremental backups again, Stop the Drainer, tidb_binlog.checkpoint, initialCommitTs, snapshot timestamp of the full backup, What is checkpoint, commit-ts, ["write save point"] [ts=411222863322546177], MySQL/TiDB checkpoint table, Kafka/file checkpoint, configuration directory, redeploy Drainer on the new machine, checkpoint is not lost, checkpoint is lost, old Drainer, full backup and a binlog backup file, Reparo, start-tso, end-ts = 0, ignore-error, critical error, restart the `tidb-server` instance
- Follow-up Guidance: The content provides step-by-step recovery flows involving stopping Drainer, clearing downstream data including `tidb_binlog.checkpoint`, restoring a full backup, and setting `initialCommitTs` or Reparo `start-tso` from the backup snapshot timestamp.
- Classification Note: This chunk is classified as recovery because it covers crash handling, checkpoint-based restart points, redeployment after failure, and restore procedures after binlog loss or backup recovery.

## Official Source Content

## What can I do if a Pump instance crashes?

If a Pump instance crashes, Drainer cannot replicate data to the downstream because it cannot obtain the data of this instance. If this Pump instance can recover to the normal state, Drainer resumes replication; if not, perform the following steps:

1. Use [binlogctl to change the state of this Pump instance to `offline`](https://docs.pingcap.com/tidb/stable/tidb-binlog/maintain-tidb-binlog-cluster) to discard the data of this Pump instance.

2. Because Drainer cannot obtain the data of this pump instance, the data in the downstream and upstream is inconsistent. In this situation, perform full and incremental backups again. The steps are as follows:

    1. Stop the Drainer.

    2. Perform a full backup in the upstream.

    3. Clear the data in the downstream including the `tidb_binlog.checkpoint` table.

    4. Restore the full backup to the downstream.

    5. Deploy Drainer and use `initialCommitTs` (set `initialCommitTs` as the snapshot timestamp of the full backup) as the start point of initial replication.
## What is checkpoint?

Checkpoint records the `commit-ts` that Drainer replicates to the downstream. When Drainer restarts, it reads the checkpoint and then replicates data to the downstream starting from the corresponding `commit-ts`. The `["write save point"] [ts=411222863322546177]` Drainer log means saving the checkpoint with the corresponding timestamp.

Checkpoint is saved in different ways for different types of downstream platforms:

- For MySQL/TiDB, it is saved in the `tidb_binlog.checkpoint` table.

- For Kafka/file, it is saved in the file of the corresponding configuration directory.

The data of kafka/file contains `commit-ts`, so if the checkpoint is lost, you can check the latest `commit-ts` of the downstream data by consuming the latest data in the downstream .

Drainer reads the checkpoint when it starts. If Drainer cannot read the checkpoint, it uses the configured `initialCommitTs` as the start point of the initial replication.
## How to redeploy Drainer on the new machine when Drainer fails and the data in the downstream remains?

If the data in the downstream is not affected, you can redeploy Drainer on the new machine as long as the data can be replicated from the corresponding checkpoint.

- If the checkpoint is not lost, perform the following steps:

    1. Deploy and start a new Drainer (Drainer can read checkpoint and resumes replication).

    2. Use [binlogctl to change the state of the old Drainer to `offline`](https://docs.pingcap.com/tidb/stable/tidb-binlog/maintain-tidb-binlog-cluster).

- If the checkpoint is lost, perform the following steps:

    1. To deploy a new Drainer, obtain the `commit-ts` of the old Drainer as the `initialCommitTs` of the new Drainer.

    2. Use [binlogctl to change the state of the old Drainer to `offline`](https://docs.pingcap.com/tidb/stable/tidb-binlog/maintain-tidb-binlog-cluster).
## How to restore the data of a cluster using a full backup and a binlog backup file?

1. Clean up the cluster and restore a full backup.

2. To restore the latest data of the backup file, use Reparo to set `start-tso` = {snapshot timestamp of the full backup + 1} and `end-ts` = 0 (or you can specify a point in time).
## How to redeploy Drainer when enabling `ignore-error` in Primary-Secondary replication triggers a critical error?

If a critical error is triggered when TiDB fails to write binlog after enabling `ignore-error`, TiDB stops writing binlog and binlog data loss occurs. To resume replication, perform the following steps:

1. Stop the Drainer instance.

2. Restart the `tidb-server` instance that triggers critical error and resume writing binlog (TiDB does not write binlog to Pump after critical error is triggered).

3. Perform a full backup in the upstream.

4. Clear the data in the downstream including the `tidb_binlog.checkpoint` table.

5. Restore the full backup to the downstream.

6. Deploy Drainer and use `initialCommitTs` (set `initialCommitTs` as the snapshot timestamp of the full backup) as the start point of initial replication.
