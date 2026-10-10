# Troubleshooting slow commits, long-lived transactions, and CheckLeader

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-stale-read.md`
- Source Title: `Understanding Stale Read and safe-ts in TiKV`
- Source Heading Path: `Understanding Stale Read and safe-ts in TiKV > Troubleshooting tips | Understanding Stale Read and safe-ts in TiKV > Troubleshooting tips > Handle slow transaction commit | Understanding Stale Read and safe-ts in TiKV > Troubleshooting tips > Handle long-lived transactions | Understanding Stale Read and safe-ts in TiKV > Troubleshooting tips > Address CheckLeader issues`
- Source Line Ranges: `125-164`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`, `sql`, `dashboard`
- Topic Tags: `troubleshooting`, `slow-commit`, `long-lived-transactions`, `locks`, `checkleader`, `network`, `logs`, `processlist`, `cluster_tidb_trx`, `resolved-ts`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0527_e658f39924`
- Source ID: `tidb-docs-8.1:troubleshoot-stale-read.md#troubleshooting-tips`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `61a349dcbd5e31af378372867bdab5dc4f3f70940cedb8698c8727881138a522`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-stale-read#troubleshooting-tips
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-stale-read.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting stale read impact from slow transaction commits, long-lived transactions, or CheckLeader delays.
- Retrieval Keywords: expensive_query, txn_start_ts, CLUSTER_TIDB_TRX, SHOW PROCESSLIST, Check Leader Duration, TiKV-Details > Resolved-TS, slow transaction commit, long-lived transactions, locks, start_ts, CheckLeader issues, network
- Follow-up Guidance: The source suggests checking TiKV logs with `--log`, searching start_ts in TiDB and TiKV logs, using `CLUSTER_TIDB_TRX`, checking `SHOW PROCESSLIST`, and checking the network plus the Check Leader Duration metric.
- Classification Note: This chunk is classified as operation because it lists practical troubleshooting steps and operational checks for slow commits, long-lived transactions, and CheckLeader-related issues.

## Official Source Content

## Troubleshooting tips
### Handle slow transaction commit

A transaction that takes a long time to commit is often a large transaction. The prewrite phase of this slow transaction leaves some locks, but it takes too long before the commit phase clean the locks. To troubleshoot this issue, you can try to identify the transaction to which the locks belong and try to pinpoint the reason they exist, such as using logs.

The following list some actions you can take:

- Specify the `--log` option in the `tikv-ctl` command and check TiKV logs to find the specific locks with their start_ts.
- Search the start_ts in both TiDB and TiKV logs to identify issues with the transaction.

    If a query takes over 60 seconds, an `expensive_query` log is printed with the SQL statement. You can use the start_ts value to match the log. The following is an example:

    ```log
    [2023/07/17 19:32:09.403 +08:00] [WARN] [expensivequery.go:145] [expensive_query] [cost_time=60.025022732s] [cop_time=0.00346666s] [process_time=8.358409508s] [wait_time=0.013582596s] [request_count=278] [total_keys=9943616] [process_keys=9943360] [num_cop_tasks=278] [process_avg_time=0.030066221s] [process_p90_time=0.045296042s] [process_max_time=0.052828934s] [process_max_addr=192.168.31.244:20160] [wait_avg_time=0.000048858s] [wait_p90_time=0.00006057s] [wait_max_time=0.00040991s] [wait_max_addr=192.168.31.244:20160] [stats=t:442916666913587201] [conn=2826881778407440457] [user=root] [database=test] [table_ids="[100]"] [**txn_start_ts**=442916790435840001] [mem_max="2514229289 Bytes (2.34 GB)"] [sql="update t set b = b + 1"]
    ```

- Use the [`CLUSTER_TIDB_TRX`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-trx#cluster_tidb_trx) table to find active transactions if you cannot get enough information about the locks from logs.
- Execute [`SHOW PROCESSLIST`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-processlist) to view the current sessions connected to the same TiDB server and their time spent on the current statement. But it does not show start_ts.

If the locks exist due to ongoing large transactions, consider modifying your application logic as these locks can hinder the progress of resolve-ts.

If the locks do not belong to any ongoing transactions, it might be due to a coordinator (TiDB) crashing after it prewrites the locks. In this case, TiDB will automatically resolve the locks. No action is required unless the problem persists.
### Handle long-lived transactions

Transactions that remain active for a long time could possibly block the advance of resolved-ts, even if they eventually commit quickly. This is because it is the start-ts of these long-lived transactions that are used to calculate the resolved-ts.

To address this issue:

- Identify the Transaction: Begin by pinpointing the transaction associated with the locks. It is crucial to understand the reason behind their existence. Leveraging logs can be particularly helpful.

- Examine Application Logic: If the prolonged transaction duration is a result of your application's logic, consider revising it to prevent such occurrences.

- Address Slow Queries: If the transaction's duration is extended due to slow queries, prioritize resolving these queries to alleviate the issue.
### Address CheckLeader issues

To address CheckLeader issues, you can check the network and the **Check Leader Duration** metric in [**TiKV-Details** > **Resolved-TS** dashboard](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#resolved-ts).
