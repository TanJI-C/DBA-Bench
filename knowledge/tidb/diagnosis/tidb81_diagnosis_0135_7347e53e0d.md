# Diagnose optimistic lock conflicts and related errors

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-lock-conflicts.md`
- Source Title: `Troubleshoot Lock Conflicts`
- Source Heading Path: `Troubleshoot Lock Conflicts > Troubleshoot optimistic lock conflicts | Troubleshoot Lock Conflicts > Troubleshoot optimistic lock conflicts > Read-write conflicts | Troubleshoot Lock Conflicts > Troubleshoot optimistic lock conflicts > KeyIsLocked error | Troubleshoot Lock Conflicts > Troubleshoot optimistic lock conflicts > LockNotFound error`
- Source Line Ranges: `162-283`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `tiup`, `sql`
- Topic Tags: `optimistic-transactions`, `read-write-conflicts`, `keyislocked`, `locknotfound`, `backoff-retry`, `grafana-metrics`, `tidb-logs`, `tikv-logs`, `ttl`, `tso`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0135_7347e53e0d`
- Source ID: `tidb-docs-8.1:troubleshoot-lock-conflicts.md#troubleshoot-optimistic-lock-conflicts`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `601da3b3d96553aee95cc545fd65d6593de1fd94933350554fddf880633a34b1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-lock-conflicts#troubleshoot-optimistic-lock-conflicts
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-lock-conflicts.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing optimistic transaction lock conflicts such as read-write conflicts, KeyIsLocked, or TxnLockNotFound from Grafana metrics, TiDB logs, or TiKV logs.
- Retrieval Keywords: Troubleshoot optimistic lock conflicts, optimistic transaction mode, Read-write conflicts, KeyIsLocked, LockNotFound, TxnLockNotFound, KV Errors, Lock Resolve OPS, KV Backoff OPS, not_expired, resolve, tikvLockFast, txnLock, txnStartTS, backoff_types, TxnLockFast, backoff_ms, region_id, locked primary_lock, lock_version, key, lock_ttl, txn_size, tidb-ctl decoder, decoder, tidb_retry_limit, pd tso, tiup ctl:v<CLUSTER_VERSION> pd tso, start_ts, commit_ts, TTL
- Follow-up Guidance: The source also includes follow-up checks such as using tidb-ctl decoder to decode a locked key and using tiup ctl:v<CLUSTER_VERSION> pd tso on start_ts and commit_ts to compare the interval with TTL.
- Classification Note: This is classified as diagnosis because the content explains how to recognize optimistic lock conflict types through specific metrics, log fields, error names, and timestamp inspection.

## Official Source Content

## Troubleshoot optimistic lock conflicts

This section provides the solutions of common lock conflict issues in the optimistic transaction mode.
### Read-write conflicts

As the TiDB server receives a read request from a client, it gets a globally unique and increasing timestamp at the physical time as the start_ts of the current transaction. The transaction needs to read the latest data before start_ts, that is, the target key of the latest commit_ts that is smaller than start_ts. When the transaction finds that the target key is locked by another transaction, and it cannot know which phase the other transaction is in, a read-write conflict happens. The diagram is as follows:

![read-write conflict](/media/troubleshooting-lock-pic-04.png)

Txn0 completes the Prewrite phase and enters the Commit phase. At this time, Txn1 requests to read the same target key. Txn1 needs to read the target key of the latest commit_ts that is smaller than its start_ts. Because Txn1's start_ts is larger than Txn0's lock_ts, Txn1 must wait for the target key's lock to be cleared, but it hasn't been done. As a result, Txn1 cannot confirm whether Txn0 has been committed or not. Thus, a read-write conflict between Txn1 and Txn0 happens.

You can detect the read-write conflict in your TiDB cluster by the following ways:

1. Monitoring metrics and logs of the TiDB server

    * Monitoring data through Grafana

        In the `KV Errors` panel in the TiDB dashboard, `not_expired`/`resolve` in `Lock Resolve OPS` and `tikvLockFast` in `KV Backoff OPS` are monitoring metrics that can be used to check read-write conflicts in transactions. If the values of all the metrics increase, there might be many read-write conflicts. The `not_expired` item means that the transaction's lock has not timed out. The `resolve` item means that the other transaction tries to clean up the locks. The `tikvLockFast` item means that read-write conflicts occur.

        ![KV-backoff-txnLockFast-optimistic](/media/troubleshooting-lock-pic-09.png)
        ![KV-Errors-resolve-optimistic](/media/troubleshooting-lock-pic-08.png)

    * Logs of the TiDB server

        If there is any read-write conflict, you can see the following message in the TiDB log:

        ```log
        [INFO] [coprocessor.go:743] ["[TIME_COP_PROCESS] resp_time:406.038899ms txnStartTS:416643508703592451 region_id:8297 store_addr:10.8.1.208:20160 backoff_ms:255 backoff_types:[txnLockFast,txnLockFast] kv_process_ms:333 scan_total_write:0 scan_processed_write:0 scan_total_data:0 scan_processed_data:0 scan_total_lock:0 scan_processed_lock:0"]
        ```

        * txnStartTS: The start_ts of the transaction that is sending the read request. In the above log, `416643508703592451` is the start_ts.
        * backoff_types: If a read-write conflict happens, and the read request performs backoff and retry, the type of retry is `TxnLockFast`.
        * backoff_ms: The time that the read request spends in the backoff and retry, and the unit is milliseconds. In the above log, the read request spends 255 milliseconds in the backoff and retry.
        * region_id: Region ID corresponding to the target key of the read request.

2. Logs of the TiKV server

    If there is any read-write conflict, you can see the following message in the TiKV log:

    ```log
    [ERROR] [endpoint.rs:454] [error-response] [err=""locked primary_lock:7480000000000004D35F6980000000000000010380000000004C788E0380000000004C0748 lock_version: 411402933858205712 key: 7480000000000004D35F7280000000004C0748 lock_ttl: 3008 txn_size: 1""]
    ```

    This message indicates that a read-write conflict occurs in TiDB. The target key of the read request has been locked by another transaction. The locks are from the uncommitted optimistic transaction and the uncommitted pessimistic transaction after the prewrite phase.

    * primary_lock: Indicates that the target key is locked by the primary lock.
    * lock_version: The start_ts of the transaction that owns the lock.
    * key: The target key that is locked.
    * lock_ttl: The lock's TTL (Time To Live)
    * txn_size: The number of keys that are in the Region of the transaction that owns the lock.

Solutions:

* A read-write conflict triggers an automatic backoff and retry. As in the above example, Txn1 has a backoff and retry. The first time of the retry is 10 ms, the longest retry is 3000 ms, and the total time is 20000 ms at maximum.

* You can use the sub-command [`decoder`](https://docs.pingcap.com/tidb/stable/tidb-control#the-decoder-command) of TiDB Control to view the table id and rowid of the row corresponding to the specified key:

    ```sh
    ./tidb-ctl decoder "t\x00\x00\x00\x00\x00\x00\x00\x1c_r\x00\x00\x00\x00\x00\x00\x00\xfa"
    format: table_row
    table_id: -9223372036854775780
    row_id: -9223372036854775558
    ```
### KeyIsLocked error

In the Prewrite phase of a transaction, TiDB checks whether there is any write-write conflict, and then checks whether the target key has been locked by another transaction. If the key is locked, the TiKV server outputs a "KeyIsLocked" error. At present, the error message is not printed in the logs of TiDB and TiKV. Same as read-write conflicts, when "KeyIsLocked" occurs, TiDB automatically performs backoff and retry for the transaction.

You can check whether there's any "KeyIsLocked" error in the TiDB monitoring on Grafana:

The `KV Errors` panel in the TiDB dashboard has two monitoring metrics `Lock Resolve OPS` and `KV Backoff OPS` which can be used to check write-write conflicts caused by a transaction. If the `resolve` item under `Lock Resolve OPS` and the `txnLock` item under `KV Backoff OPS` have a clear upward trend, a "KeyIsLocked" error occurs. `resolve` refers to the operation that attempts to clear the lock, and `txnLock` represents a write conflict.

![KV-backoff-txnLockFast-optimistic-01](/media/troubleshooting-lock-pic-07.png)
![KV-Errors-resolve-optimistic-01](/media/troubleshooting-lock-pic-08.png)

Solutions:

* If there is a small amount of txnLock in the monitoring, no need to pay too much attention. The backoff and retry is automatically performed in the background. The first time of the retry is 100 ms and the maximum time is 3000 ms for a single retry.
* If there are too many "txnLock" operations in the `KV Backoff OPS`, it is recommended that you analyze the reasons to the write conflicts from the application side.
* If your application is a write-write conflict scenario, it is strongly recommended to use the pessimistic transaction mode.
### LockNotFound error

The error log of "TxnLockNotFound" means that transaction commit time is longer than the TTL time, and when the transaction is going to commit, its lock has been rolled back by other transactions. If the TiDB server enables transaction commit retry, this transaction is re-executed according to [tidb_retry_limit](https://docs.pingcap.com/tidb/stable/system-variables#tidb_retry_limit). (Note about the difference between explicit and implicit transactions.)

You can check whether there is any "LockNotFound" error in the following ways:

1. View the logs of the TiDB server

    If a "TxnLockNotFound" error occurs, the TiDB log message is like this:

    ```log
    [WARN] [session.go:446] ["commit failed"] [conn=149370] ["finished txn"="Txn{state=invalid}"] [error="[kv:6]Error: KV error safe to retry tikv restarts txn: Txn(Mvcc(TxnLockNotFound{ start_ts: 412720515987275779, commit_ts: 412720519984971777, key: [116, 128, 0, 0, 0, 0, 1, 111, 16, 95, 114, 128, 0, 0, 0, 0, 0, 0, 2] })) [try again later]"]
    ```

    * start_ts: The start_ts of the transaction that outputs the `TxnLockNotFound` error because its lock has been rolled back by other transactions. In the above log, `412720515987275779` is the start_ts.
    * commit_ts: The commit_ts of the transaction that outputs the `TxnLockNotFound` error. In the above log, `412720519984971777` is the commit_ts.

2. View the logs of the TiKV server

    If a "TxnLockNotFound" error occurs, the TiKV log message is like this:

    ```log
    Error: KV error safe to retry restarts txn: Txn(Mvcc(TxnLockNotFound)) [ERROR [Kv.rs:708] ["KvService::batch_raft send response fail"] [err=RemoteStoped]
    ```

Solutions:

* By checking the time interval between start_ts and commit_ts, you can confirm whether the commit time exceeds the TTL time.

    Checking the time interval using the PD control tool:

    ```shell
    tiup ctl:v<CLUSTER_VERSION> pd tso [start_ts]
    tiup ctl:v<CLUSTER_VERSION> pd tso [commit_ts]
    ```

* It is recommended to check whether the write performance is slow, which might cause that the efficiency of transaction commit is poor, and thus the lock is cleared.

* In the case of disabling the TiDB transaction retry, you need to catch the exception on the application side and try again.
