# Example diagnosing stale read miss rate with metrics, tikv-ctl, and logs

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-stale-read.md`
- Source Title: `Understanding Stale Read and safe-ts in TiKV`
- Source Heading Path: `Understanding Stale Read and safe-ts in TiKV > Example`
- Source Line Ranges: `165-237`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`, `shared`
- Topic Tags: `stale-read`, `safe-ts`, `resolved-ts`, `miss-rate`, `grafana`, `tikv-ctl`, `logs`, `transactions`, `locks`, `processlist`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0138_99ffa42f89`
- Source ID: `tidb-docs-8.1:troubleshoot-stale-read.md#example`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6a077f7fb9a4abc829101f53a41aeea03f3f88703e915a8e2020c6201b4820b8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-stale-read#example
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-stale-read.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing an increasing Stale Read OPS miss rate by correlating Resolved-TS dashboard metrics, TiKV region read progress, and transaction logs to find a blocking transaction.
- Retrieval Keywords: Stale Read OPS miss rate, Max Resolved TS gap, Min Resolved TS Region, TiKV-Details, Resolved-TS, Region 3121, tikv-ctl get-region-read-progress, ./tikv-ctl --host 127.0.0.1:20160 get-region-read-progress -r 3121 --log, safe_ts, resolved_ts, applied_index, tracked index, number of locks, number of transactions, locks with the minimum start_ts in resolver, start_ts, txnStartTS, BIG_TXN, expensive_query, SHOW PROCESSLIST, update t set b = b + 1
- Follow-up Guidance: After identifying the transaction start_ts from TiKV logs, grep that timestamp in TiDB logs and use SHOW PROCESSLIST to locate the running statement and session.
- Classification Note: This is classified as diagnosis because the content walks through observing stale read miss metrics, inspecting a region with tikv-ctl, checking TiKV and TiDB logs, and identifying the statement causing stale read hindrance.

## Official Source Content

## Example

If you observe an increasing miss rate of **Stale Read OPS** as follows:

![Example: Stale Read OPS](/media/stale-read/example-ops.png)

You can first check the **Max Resolved TS gap** and **Min Resolved TS Region** metrics in the [**TiKV-Details** > **Resolved-TS** dashboard](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#resolved-ts):

![Example: Max Resolved TS gap](/media/stale-read/example-ts-gap.png)

From the preceding metrics, you can find that Region `3121` and some other Regions have not updated their resolved-ts in time.

To get more details about the state of Region `3121`, you can run the following command:

```bash
./tikv-ctl --host 127.0.0.1:20160 get-region-read-progress -r 3121 --log
```

The output is as follows:

```log
Region read progress:
    exist: true,
    safe_ts: 442918444145049601,
    applied_index: 2477,
    read_state.ts: 442918444145049601,
    read_state.apply_index: 1532,
    pending front item (oldest) ts: 0,
    pending front item (oldest) applied index: 0,
    pending back item (latest) ts: 0,
    pending back item (latest) applied index: 0,
    paused: false,
    discarding: false,
Resolver:
    exist: true,
    resolved_ts: 442918444145049601,
    tracked index: 2477,
    number of locks: 480000,
    number of transactions: 1,
    stopped: false,
```

A notable observation here is that the `applied_index` equals to the `tracked index` in resolver. Therefore, the resolver appears to be the root of this issue. You can also see that there is 1 transaction that leaves 480000 locks in this Region, which might be the cause.

To get the exact transaction and the keys of some of the locks, you can check TiKV logs and grep `locks with`. The output is as follows:

```log
[2023/07/17 21:16:44.257 +08:00] [INFO] [resolver.rs:213] ["locks with the minimum start_ts in resolver"] [keys="[74800000000000006A5F7280000000000405F6, ... , 74800000000000006A5F72800000000000EFF6, 74800000000000006A5F7280000000000721D9, 74800000000000006A5F72800000000002F691]"] [start_ts=442918429687808001] [region_id=3121]
```

From the TiKV log, you can get the start_ts of the transaction, that is `442918429687808001`. To get more information about the statement and transaction, you can grep this timestamp in TiDB logs. The output is as follows:

```log
[2023/07/17 21:16:18.287 +08:00] [INFO] [2pc.go:685] ["[BIG_TXN]"] [session=2826881778407440457] ["key sample"=74800000000000006a5f728000000000000000] [size=319967171] [keys=10000000] [puts=10000000] [dels=0] [locks=0] [checks=0] [txnStartTS=442918429687808001]

[2023/07/17 21:16:22.703 +08:00] [WARN] [expensivequery.go:145] [expensive_query] [cost_time=60.047172498s] [cop_time=0.004575113s] [process_time=15.356963423s] [wait_time=0.017093811s] [request_count=397] [total_keys=20000398] [process_keys=10000000] [num_cop_tasks=397] [process_avg_time=0.038682527s] [process_p90_time=0.082608262s] [process_max_time=0.116321331s] [process_max_addr=192.168.31.244:20160] [wait_avg_time=0.000043057s] [wait_p90_time=0.00004007s] [wait_max_time=0.00075014s] [wait_max_addr=192.168.31.244:20160] [stats=t:442918428521267201] [conn=2826881778407440457] [user=root] [database=test] [table_ids="[106]"] [txn_start_ts=442918429687808001] [mem_max="2513773983 Bytes (2.34 GB)"] [sql="update t set b = b + 1"]
```

Then, you can basically locate the statement that caused the problem. To further check it, you can execute the [`SHOW PROCESSLIST`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-processlist) statement. The output is as follows:

```sql
+---------------------+------+---------------------+--------+---------+------+------------+---------------------------+
| Id                  | User | Host                | db     | Command | Time | State      | Info                      |
+---------------------+------+---------------------+--------+---------+------+------------+---------------------------+
| 2826881778407440457 | root | 192.168.31.43:58641 | test   | Query   | 48   | autocommit | update t set b = b + 1    |
| 2826881778407440613 | root | 127.0.0.1:45952     | test   | Execute | 0    | autocommit | select * from t where a=? |
| 2826881778407440619 | root | 192.168.31.43:60428 | <null> | Query   | 0    | autocommit | show processlist          |
+---------------------+------+---------------------+--------+---------+------+------------+---------------------------+
```

The output shows that someone is executing an unexpected `UPDATE` statement (`update t set b = b + 1`), which results in a large transaction and hinders Stale Read.

To resolve this issue, you can stop the application that is running this `UPDATE` statement.
