# PITR, log backup resume errors, and TiFlash access after point restore

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/backup-and-restore-faq.md`
- Source Title: `Backup & Restore FAQs`
- Source Heading Path: `Backup & Restore FAQs > PITR issues | Backup & Restore FAQs > PITR issues > What is the difference between [PITR](/br/br-pitr-guide.md) and [cluster flashback](/sql-statements/sql-statement-flashback-cluster.md)? | Backup & Restore FAQs > PITR issues > When the upstream database imports data using TiDB Lightning in the physical import mode, the log backup feature becomes unavailable. Why? | Backup & Restore FAQs > PITR issues > The cluster has recovered from the network partition failure, but the checkpoint of the log backup task progress still does not resume. Why? | Backup & Restore FAQs > After restoring a downstream cluster using the `br restore point` command, data cannot be accessed from TiFlash. What should I do? | Backup & Restore FAQs > After restoring a downstream cluster using the `br restore point` command, data cannot be accessed from TiFlash. What should I do? > What should I do if the `status` of a log backup task becomes `ERROR`? | Backup & Restore FAQs > After restoring a downstream cluster using the `br restore point` command, data cannot be accessed from TiFlash. What should I do? > What should I do if the error message `ErrBackupGCSafepointExceeded` is returned when using the `br log resume` command to resume a suspended task?`
- Source Line Ranges: `29-109`
- Source Scope: `shared`
- Primary Component: `br`
- Related Components: `lightning`, `tiflash`, `tikv`, `tidb`
- Topic Tags: `pitr`, `flashback`, `log-backup`, `checkpoint`, `network-partition`, `resume`, `gc-safepoint`, `tiflash-replica`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0025_064b33db8e`
- Source ID: `tidb-docs-8.1:faq/backup-and-restore-faq.md#pitr-issues`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `778713cfdfe5de64a902b0a4a021ce301a8e4914c5ac0c2d34c0038b0323ae1a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/backup-and-restore-faq#pitr-issues
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/backup-and-restore-faq.md

## Retrieval Guidance

- Use When: Use this chunk when asking about PITR versus cluster flashback, log backup task resume and ERROR handling, TiDB Lightning physical mode limitations for log backup, TiFlash availability after `br restore point`, or `ErrBackupGCSafepointExceeded` during `br log resume`.
- Retrieval Keywords: PITR, cluster flashback, br-pitr-guide, sql-statement-flashback-cluster, TiDB Lightning physical import mode, log backup feature becomes unavailable, br log resume, br log status, status ERROR, status NORMAL, network partition failure, checkpoint of the log backup task progress, br restore point, TiFlash, ALTER TABLE table_name SET TIFLASH REPLICA, INFORMATION_SCHEMA.tiflash_replica, progress, ErrBackupGCSafepointExceeded, br log stop, br log start, GC safepoint, service safepoint
- Follow-up Guidance: It includes the exact `br log resume --task-name=task1 --pd x.x.x.x:2379` command, explains that resumed tasks continue from the last checkpoint if the safe point is still retained, and says to stop and recreate the task if the checkpoint data has been garbage collected.
- Classification Note: This is classified as recovery because the content focuses on point-in-time recovery, flashback comparison, restoring access after point restore, and resuming or recreating failed log backup tasks.

## Official Source Content

## PITR issues
### What is the difference between [PITR](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide) and [cluster flashback](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster)?

From the perspective of use cases, PITR is usually used to restore the data of a cluster to a specified point in time when the cluster is completely out of service or the data is corrupted and cannot be recovered using other solutions. To use PITR, you need a new cluster for data recovery. The cluster flashback feature is specifically designed for the data error scenarios caused by user mis-operations or other factors, which allows you to restore the data of a cluster in-place to the latest timestamp before the data errors occur.

In most cases, flashback is a better recovery solution than PITR for data errors caused by human mistakes, as it has a much shorter RPO (close to zero) and RTO. However, when a cluster is completely unavailable, because flashback cannot run at this time, PITR is the only solution to recover the cluster in this case. Therefore, PITR is always a must-have solution when you develop database disaster recovery strategies, even though it has a longer RPO (up to 5 minutes) and RTO than flashback.
### When the upstream database imports data using TiDB Lightning in the physical import mode, the log backup feature becomes unavailable. Why?

Currently, the log backup feature is not fully adapted to TiDB Lightning. Therefore, data imported in the physical mode of TiDB Lightning cannot be backed up into log data

In upstream clusters where you create log backup tasks, avoid using the TiDB Lightning physical mode to import data. Instead, you can use TiDB Lightning logical mode. If you do need to use the physical mode, perform a snapshot backup after the import is complete, so that PITR can be restored to the time point after the snapshot backup.
### The cluster has recovered from the network partition failure, but the checkpoint of the log backup task progress still does not resume. Why?

Issue: [#13126](https://github.com/tikv/tikv/issues/13126)

After a network partition failure in the cluster, the backup task cannot continue backing up logs. After a certain retry time, the task will be set to `ERROR` state. At this point, the backup task has stopped.

To resolve this issue, you need to manually execute the `br log resume` command to resume the log backup task.
## After restoring a downstream cluster using the `br restore point` command, data cannot be accessed from TiFlash. What should I do?

Currently, PITR does not support writing data directly to TiFlash during the restore phase. Instead, br command-line tool executes the `ALTER TABLE table_name SET TIFLASH REPLICA ***` DDL to replicate the data. Therefore, TiFlash replicas are not available immediately after PITR completes data restore. Instead, you need to wait for a certain period of time for the data to be replicated from TiKV nodes. To check the replication progress, check the `progress` information in the `INFORMATION_SCHEMA.tiflash_replica` table.
### What should I do if the `status` of a log backup task becomes `ERROR`?

During a log backup task, the task status becomes `ERROR` if it fails and cannot be recovered after retrying. The following is an example:

```shell
br log status --pd x.x.x.x:2379

● Total 1 Tasks.
> #1 <
                    name: task1
                  status: ○ ERROR
                   start: 2022-07-25 13:49:02.868 +0000
                     end: 2090-11-18 14:07:45.624 +0000
                 storage: s3://tmp/br-log-backup0ef49055-5198-4be3-beab-d382a2189efb/Log
             speed(est.): 0.00 ops/s
      checkpoint[global]: 2022-07-25 14:46:50.118 +0000; gap=11h31m29s
          error[store=1]: KV:LogBackup:RaftReq
error-happen-at[store=1]: 2022-07-25 14:54:44.467 +0000; gap=11h23m35s
  error-message[store=1]: retry time exceeds: and error failed to get initial snapshot: failed to get the snapshot (region_id = 94812): Error during requesting raftstore: message: "read index not ready, reason can not read index due to merge, region 94812" read_index_not_ready { reason: "can not read index due to merge" region_id: 94812 }: failed to get initial snapshot: failed to get the snapshot (region_id = 94812): Error during requesting raftstore: message: "read index not ready, reason can not read index due to merge, region 94812" read_index_not_ready { reason: "can not read index due to merge" region_id: 94812 }: failed to get initial snapshot: failed to get the snapshot (region_id = 94812): Error during requesting raftstore: message: "read index not ready, reason can not read index due to merge, region 94812" read_index_not_ready { reason: "can not read index due to merge" region_id: 94812 }
```

To address this problem, check the error message for the cause and perform as instructed. After the problem is addressed, run the following command to resume the task:

```shell
br log resume --task-name=task1 --pd x.x.x.x:2379
```

After the backup task is resumed, you can check the status using `br log status`. The backup task continues when the task status becomes `NORMAL`.

```shell
● Total 1 Tasks.
> #1 <
              name: task1
            status: ● NORMAL
             start: 2022-07-25 13:49:02.868 +0000
               end: 2090-11-18 14:07:45.624 +0000
           storage: s3://tmp/br-log-backup0ef49055-5198-4be3-beab-d382a2189efb/Log
       speed(est.): 15509.75 ops/s
checkpoint[global]: 2022-07-25 14:46:50.118 +0000; gap=6m28s
```

> **Note:**
>
> This feature backs up multiple versions of data. When a long backup task fails and the status becomes `ERROR`, the checkpoint data of this task is set as a `safe point`, and the data of the `safe point` will not be garbage collected within 24 hours. Therefore, the backup task continues from the last checkpoint after resuming the error. If the task fails for more than 24 hours and the last checkpoint data has been garbage collected, an error will be reported when you resume the task. In this case, you can only run the `br log stop` command to stop the task first and then start a new backup task.
### What should I do if the error message `ErrBackupGCSafepointExceeded` is returned when using the `br log resume` command to resume a suspended task?

```shell
Error: failed to check gc safePoint, checkpoint ts 433177834291200000: GC safepoint 433193092308795392 exceed TS 433177834291200000: [BR:Backup:ErrBackupGCSafepointExceeded]backup GC safepoint exceeded
```

After you pause a log backup task, to prevent the MVCC data from being garbage collected, the pausing task program sets the current checkpoint as the service safepoint automatically. This ensures that the MVCC data generated within 24 hours can remain. If the MVCC data of the backup checkpoint has been generated for more than 24 hours, the data of the checkpoint will be garbage collected, and the backup task is unable to resume.

To address this problem, delete the current task using `br log stop`, and then create a log backup task using `br log start`. At the same time, you can perform a full backup for subsequent PITR.
