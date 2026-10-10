# Diagnose Stale Read issues with metrics, tikv-ctl, and logs

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-stale-read.md`
- Source Title: `Understanding Stale Read and safe-ts in TiKV`
- Source Heading Path: `Understanding Stale Read and safe-ts in TiKV > Diagnose Stale Read issues | Understanding Stale Read and safe-ts in TiKV > Diagnose Stale Read issues > Identify issues | Understanding Stale Read and safe-ts in TiKV > Diagnose Stale Read issues > Common causes | Understanding Stale Read and safe-ts in TiKV > Diagnose Stale Read issues > Use Grafana to diagnose | Understanding Stale Read and safe-ts in TiKV > Diagnose Stale Read issues > Use `tikv-ctl` to diagnose | Understanding Stale Read and safe-ts in TiKV > Diagnose Stale Read issues > Use logs to diagnose`
- Source Line Ranges: `36-124`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`, `dashboard`
- Topic Tags: `stale-read`, `safe-ts`, `resolved-ts`, `grafana`, `tikv-ctl`, `logs`, `metrics`, `dataisnotready`, `region`, `locks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0137_28bd46324a`
- Source ID: `tidb-docs-8.1:troubleshoot-stale-read.md#diagnose-stale-read-issues`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7a82aa00bedb47200a6c357e8b9b73f812a184ac1230503a0521b4ed4fe8dba9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-stale-read#diagnose-stale-read-issues
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-stale-read.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing Stale Read issues through Grafana metrics, tikv-ctl output, TiDB WARN logs, or TiKV historical logs.
- Retrieval Keywords: DataIsNotReady, Grafana > TiDB dashboard > KV Request, TiKV-Details > Resolved-TS, tikv-ctl get-region-read-progress, get-region-read-progress -r 14 --log --min-start-ts 0, RegionReadProgress, resolved_ts, safe_ts, apply index, number of locks, the max gap of leader resolved-ts is large, the max gap of follower safe-ts is large, the max gap of follower resolved-ts is large
- Follow-up Guidance: The source says these tools help determine whether locks block resolved-ts, whether the apply index is too small to update safe-ts, and whether the leader is sending a sufficiently updated resolved-ts when a follower peer exists.
- Classification Note: This chunk is classified as diagnosis because it identifies indicators, common causes, dashboards, tikv-ctl fields, and logs used to investigate Stale Read problems.

## Official Source Content

## Diagnose Stale Read issues

This section introduces how to diagnose Stale Read issues using Grafana, `tikv-ctl`, and logs.
### Identify issues

In the [Grafana > TiDB dashboard > **KV Request** dashboard](https://docs.pingcap.com/tidb/stable/grafana-tidb-dashboard#kv-request), the following panels show the hit rate, OPS, and traffic of Stale Read:

![Stale Read Hit/Miss OPS](/media/stale-read/metrics-hit-miss.png)

![Stale Read Req OPS](/media/stale-read/metrics-ops.png)

![Stale Read Req Traffic](/media/stale-read/traffic.png)

For more information about the preceding metrics, see [TiDB monitoring metrics](https://docs.pingcap.com/tidb/stable/grafana-tidb-dashboard#kv-request).

When Stale Read issues occur, you might notice changes in the preceding metrics. The most direct indicator is a WARN log from TiDB, which reports `DataIsNotReady` with a Region ID and the `safe-ts` it encounters.
### Common causes

The most common causes that can impact the effectiveness of Stale Read are as follows:

- Transactions that take long time to commit.
- Transactions live too long before they commit.
- Delays in pushing the information of CheckLeader from the leader to the follower.
### Use Grafana to diagnose

In the [**TiKV-Details** > **Resolved-TS** dashboard](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#resolved-ts), you can identify the Region with the smallest resolved-ts and safe-ts for each TiKV. If these timestamps are significantly behind real-time, you need to check the details of these Regions using `tikv-ctl`.
### Use `tikv-ctl` to diagnose

`tikv-ctl` provides up-to-date details of the resolver and `RegionReadProgress`. For more details, see [Get the state of a Region's `RegionReadProgress`](https://docs.pingcap.com/tidb/stable/tikv-control#get-the-state-of-a-regions-regionreadprogress).

The following is an example:

```bash
./tikv-ctl --host 127.0.0.1:20160 get-region-read-progress -r 14 --log --min-start-ts 0
```

The output is as follows:

```log
Region read progress:
    exist: true,
    safe_ts: 0,
    applied_index: 92,
    pending front item (oldest) ts: 0,
    pending front item (oldest) applied index: 0,
    pending back item (latest) ts: 0,
    pending back item (latest) applied index: 0,
    paused: false,
Resolver:
    exist: true,
    resolved_ts: 0,
    tracked index: 92,
    number of locks: 0,
    number of transactions: 0,
    stopped: false,
```

The preceding output helps you determine:

- Whether locks are blocking resolved-ts.
- Whether the apply index is too small to update safe-ts.
- Whether the leader is sending a sufficiently updated resolved-ts when a follower peer exists.
### Use logs to diagnose

Every 10 seconds, TiKV checks the following metrics:

- The Region leader whose resolved-ts is the minimal
- The Region follower whose safe-ts is the minimal
- The Region follower whose resolved-ts is the minimal

If any of these timestamps is abnormally small, TiKV prints a log.

These logs are especially useful when you want to diagnose a historical problem that is no longer present.

The following shows an example of the logs:

```log
[2023/08/29 16:48:18.118 +08:00] [INFO] [endpoint.rs:505] ["the max gap of leader resolved-ts is large"] [last_resolve_attempt="Some(LastAttempt { success: false, ts: TimeStamp(443888082736381953), reason: \"lock\", lock: Some(7480000000000000625F728000000002512B5C) })"] [duration_to_last_update_safe_ts=10648ms] [min_memory_lock=None] [txn_num=0] [lock_num=0] [min_lock=None] [safe_ts=443888117326544897] [gap=110705ms] [region_id=291]

[2023/08/29 16:48:18.118 +08:00] [INFO] [endpoint.rs:526] ["the max gap of follower safe-ts is large"] [oldest_candidate=None] [latest_candidate=None] [applied_index=3276] [duration_to_last_consume_leader=11460ms] [resolved_ts=443888117117353985] [safe_ts=443888117117353985] [gap=111503ms] [region_id=273]

[2023/08/29 16:48:18.118 +08:00] [INFO] [endpoint.rs:547] ["the max gap of follower resolved-ts is large; it's the same region that has the min safe-ts"]
```
