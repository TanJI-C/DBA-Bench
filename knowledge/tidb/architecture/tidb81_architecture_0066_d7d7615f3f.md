# TiCDC changefeed concepts and state transfer

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-changefeed-overview.md`
- Source Title: `Changefeed Overview`
- Source Heading Path: `Changefeed Overview | Changefeed Overview > Changefeed state transfer`
- Source Line Ranges: `5-40`
- Source Scope: `shared`
- Primary Component: `ticdc`
- Related Components: `shared`
- Topic Tags: `changefeed`, `replication-task`, `state-transfer`, `checkpoint-ts`, `target-ts`, `gc`, `gc-ttl`, `retry`, `pause`, `resume`, `failure`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0066_d7d7615f3f`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-changefeed-overview.md#changefeed-overview`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ea27d319c611a2becf3cabf5b26245eff33784130a427c45ae86e3930f55470b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-overview#changefeed-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-changefeed-overview.md

## Retrieval Guidance

- Use When: Use this chunk when asking about TiCDC changefeed states, state transfer conditions, automatic retry behavior, or how GC blocking relates to `checkpoint-ts`, `target-ts`, and `gc-ttl`.
- Retrieval Keywords: TiCDC changefeed state transfer, Normal Stopped Warning Finished Failed, checkpoint-ts, TargetTs, target-ts, gc-ttl, changefeed-error-stuck-duration, changefeed pause, changefeed resume, ErrGCTTLExceeded, ErrSnapshotLostByGC, ErrStartTsBeforeGC, recoverable errors, unrecoverable error, block GC operations
- Follow-up Guidance: It also points to the `changefeed pause` and `changefeed resume` commands and names `changefeed-error-stuck-duration` as the adjustable retry duration setting.
- Classification Note: This is classified as architecture because it defines the changefeed replication task model, its runtime states, and the official state transition relationships in TiCDC.

## Official Source Content

# Changefeed Overview

A changefeed is a replication task in TiCDC, which replicates the data change logs of specified tables in a TiDB cluster to the designated downstream. You can run and manage multiple changefeeds in a TiCDC cluster.
## Changefeed state transfer

The state of a replication task represents the running status of the replication task. During the running of TiCDC, replication tasks might fail with errors, be manually paused, resumed, or reach the specified `TargetTs`. These behaviors can lead to the change of the replication task state. This section describes the states of TiCDC replication tasks and the transfer relationships between states.

![TiCDC state transfer](/media/ticdc/ticdc-changefeed-state-transfer.png)

The states in the preceding state transfer diagram are described as follows:

- `Normal`: The replication task runs normally and the checkpoint-ts proceeds normally. A changefeed in this state blocks GC to advance.
- `Stopped`: The replication task is stopped, because the user manually pauses the changefeed. The changefeed in this state blocks GC operations.
- `Warning`: The replication task returns an error. The replication cannot continue due to some recoverable errors. The changefeed in this state keeps trying to resume until the state transfers to `Normal`. The default retry time is 30 minutes (which can be adjusted by [`changefeed-error-stuck-duration`](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config)). If it exceeds this time, the changefeed enters a failed state. The changefeed in this state blocks GC operations.
- `Finished`: The replication task is finished and has reached the preset `TargetTs`. The changefeed in this state does not block GC operations.
- `Failed`: The replication task fails. The changefeed in this state does not keep trying to resume. To give you enough time to handle the failure, the changefeed in this state blocks GC operations. The duration of the blockage is specified by the `gc-ttl` parameter, with a default value of 24 hours. If the underlying issue is resolved within this duration, you can manually resume the changefeed. Otherwise, if the changefeed remains in this state beyond the `gc-ttl` duration, the replication task cannot resume and cannot be recovered.

> **Note:**
>
> - If GC is blocked by a changefeed, the changefeed will block GC advancement for up to the time specified by `gc-ttl`. After that, the changefeed will be set to the `failed` state, with an error type of `ErrGCTTLExceeded`, and will no longer block GC advancement.
> - If the changefeed encounters errors with error codes `ErrGCTTLExceeded`, `ErrSnapshotLostByGC`, or `ErrStartTsBeforeGC`, it does not block GC operations.

The numbers in the preceding state transfer diagram are described as follows.

- ① Run the `changefeed pause` command.
- ② Run the `changefeed resume` command to resume the replication task.
- ③ Recoverable errors occur during the `changefeed` operation, and the operation is retried automatically.
- ④ The changefeed automatic retry succeeds, and `checkpoint-ts` continues to advance.
- ⑤ The changefeed automatic retry exceeds 30 minutes and fails. The changefeed enters the failed state. At this time, the changefeed continues to block upstream GC for a duration specified by `gc-ttl`.
- ⑥ The changefeed encounters an unrecoverable error and directly enters the failed state. At this time, the changefeed continues to block upstream GC for a duration specified by `gc-ttl`.
- ⑦ The replication progress of the changefeed reaches the value set by `target-ts`, and the replication is completed.
- ⑧ The changefeed has been suspended for a duration longer than the value specified by `gc-ttl`, thus encountering GC advancement errors, and cannot be resumed.
- ⑨ If the cause of the failure has been resolved, and the changefeed was suspended for a duration shorter than the value specified by `gc-ttl`, run the `changefeed resume` command to resume the replication task.
