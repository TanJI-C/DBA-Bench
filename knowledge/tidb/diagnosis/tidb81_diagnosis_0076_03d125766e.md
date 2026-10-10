# TiCDC replication interruption diagnosis and recovery handling

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/troubleshoot-ticdc.md`
- Source Title: `Troubleshoot TiCDC`
- Source Heading Path: `Troubleshoot TiCDC | Troubleshoot TiCDC > TiCDC replication interruptions | Troubleshoot TiCDC > TiCDC replication interruptions > How do I know whether a TiCDC replication task is interrupted? | Troubleshoot TiCDC > TiCDC replication interruptions > How do I know whether the replication task is stopped manually? | Troubleshoot TiCDC > TiCDC replication interruptions > How do I handle replication interruptions? | Troubleshoot TiCDC > TiCDC replication interruptions > What should I do to handle the OOM that occurs after TiCDC is restarted after a task interruption?`
- Source Line Ranges: `5-58`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `pd`, `tikv`
- Topic Tags: `replication`, `interruption`, `changefeed`, `checkpoint`, `grafana`, `logs`, `resume`, `pause`, `gc-safepoint`, `oom`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0076_03d125766e`
- Source ID: `tidb-docs-8.1:ticdc/troubleshoot-ticdc.md#troubleshoot-ticdc`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `107d902374f35d3a084571d7362dce79095d15b0b62b12795b09e0589b47d346`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/troubleshoot-ticdc#troubleshoot-ticdc
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/troubleshoot-ticdc.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing whether a TiCDC changefeed replication task is interrupted, manually stopped, or needs recovery after downstream failure, incompatible downstream SQL, restart, or post-restart OOM.
- Retrieval Keywords: changefeed checkpoint, checkpoint lag, exit error count, cdc cli changefeed list, cdc cli changefeed query, stopped, error on running processor, FATAL, admin-job-type, cdc cli changefeed resume, gc-ttl, service GC safepoint in PD, TiKV GC, ignore-txn-start-ts, cdc cli changefeed pause, cdc cli changefeed update, checkpoint-ts, OOM after TiCDC is restarted
- Follow-up Guidance: The content points to checking Grafana metrics, `cdc cli changefeed query` output including `admin-job-type` and `checkpoint-ts`, and TiCDC server logs for `error on running processor` or `FATAL` messages.
- Classification Note: This chunk is classified as diagnosis because it explains how to identify interruption symptoms and causes of TiCDC replication tasks, while also including grounded recovery handling steps.

## Official Source Content

# Troubleshoot TiCDC

This document introduces the common errors you might encounter when using TiCDC, and the corresponding maintenance and troubleshooting methods.

> **Note:**
>
> In this document, the server address specified in `cdc cli` commands is `server=http://127.0.0.1:8300`. When you use the command, replace the address with your actual TiCDC Server address.
## TiCDC replication interruptions
### How do I know whether a TiCDC replication task is interrupted?

- Check the `changefeed checkpoint` monitoring metric of the replication task (choose the right `changefeed id`) in the Grafana dashboard. If the metric value stays unchanged, or the `checkpoint lag` metric keeps increasing, the replication task might be interrupted.
- Check the `exit error count` monitoring metric. If the metric value is greater than `0`, an error has occurred in the replication task.
- Execute `cdc cli changefeed list` and `cdc cli changefeed query` to check the status of the replication task. `stopped` means the task has stopped, and the `error` item provides the detailed error message. After the error occurs, you can search `error on running processor` in the TiCDC server log to see the error stack for troubleshooting.
- In some extreme cases, the TiCDC service is restarted. You can search the `FATAL` level log in the TiCDC server log for troubleshooting.
### How do I know whether the replication task is stopped manually?

You can know whether the replication task is stopped manually by executing `cdc cli`. For example:

```shell
cdc cli changefeed query --server=http://127.0.0.1:8300 --changefeed-id 28c43ffc-2316-4f4f-a70b-d1a7c59ba79f
```

In the output of the above command, `admin-job-type` shows the state of this replication task. For more information about each state and its meaning, see [Changefeed states](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-overview#changefeed-state-transfer).
### How do I handle replication interruptions?

A replication task might be interrupted in the following known scenarios:

- The downstream continues to be abnormal, and TiCDC still fails after many retries.

    - In this scenario, TiCDC saves the task information. Because TiCDC has set the service GC safepoint in PD, the data after the task checkpoint is not cleaned by TiKV GC within the valid period of `gc-ttl`.

    - Handling method: You can resume the replication task by executing `cdc cli changefeed resume` after the downstream is back to normal.

- Replication cannot continue because of incompatible SQL statement(s) in the downstream.

    - In this scenario, TiCDC saves the task information. Because TiCDC has set the service GC safepoint in PD, the data after the task checkpoint is not cleaned by TiKV GC within the valid period of `gc-ttl`.
    - Handling procedures:
        1. Query the status information of the replication task using the `cdc cli changefeed query` command and record the value of `checkpoint-ts`.
        2. Use the new task configuration file and add the `ignore-txn-start-ts` parameter to skip the transaction corresponding to the specified `start-ts`.
        3. Pause the replication task by executing `cdc cli changefeed pause -c <changefeed-id>`.
        4. Specify the new task configuration file by executing `cdc cli changefeed update -c <changefeed-id> --config <config-file-path>`.
        5. Resume the replication task by executing `cdc cli changefeed resume -c <changefeed-id>`.
### What should I do to handle the OOM that occurs after TiCDC is restarted after a task interruption?

- Update your TiDB cluster and TiCDC cluster to the latest versions. The OOM problem has already been resolved in **v4.0.14 and later v4.0 versions, v5.0.2 and later v5.0 versions, and the latest versions**.
