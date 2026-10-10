# Optimistic transaction write conflict troubleshooting

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-write-conflicts.md`
- Source Title: `Troubleshoot Write Conflicts in Optimistic Transactions`
- Source Heading Path: `Troubleshoot Write Conflicts in Optimistic Transactions | Troubleshoot Write Conflicts in Optimistic Transactions > The reason of write conflicts | Troubleshoot Write Conflicts in Optimistic Transactions > Detect write conflicts | Troubleshoot Write Conflicts in Optimistic Transactions > Resolve write conflicts`
- Source Line Ranges: `5-92`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `tiup`, `sql`
- Topic Tags: `optimistic-transactions`, `write-conflicts`, `2pc`, `prewrite`, `grafana`, `kv-errors`, `logs`, `timestamps`, `tableid`, `indexid`, `pessimistic-transactions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0142_7281a52c2d`
- Source ID: `tidb-docs-8.1:troubleshoot-write-conflicts.md#troubleshoot-write-conflicts-in-optimistic-transactions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b8fbf128d766c55bc91edefd691c9d59d6e97e43214896d3ce29f4e56a055396`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-write-conflicts#troubleshoot-write-conflicts-in-optimistic-transactions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-write-conflicts.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing optimistic transaction write conflicts in TiDB, including how they appear during 2PC prewrite, how to detect them in Grafana or logs, and how to interpret conflict details such as timestamps, tableID, and indexID.
- Retrieval Keywords: optimistic transaction write conflict, 2PC prewrite stage, [kv:9007]Write conflict, KV Errors, KV Backoff OPS, txnlock, txnLockFast, Lock Resolve OPS, not_expired, wait_expired, expired, KV Retry Duration, txnStartTS, conflictStartTS, conflictCommitTS, tableID, indexID, handle=x, primary={tableID, pd-ctl tso, tiup ctl:v<CLUSTER_VERSION> pd -u https://127.0.0.1:2379 tso {TIMESTAMP}, curl http://{TiDBIP}:10080/db-table/{tableID}, INFORMATION_SCHEMA.TIDB_INDEXES
- Follow-up Guidance: The content also shows how to convert transaction timestamps with pd-ctl, map tableID to a table name with the status API, and map indexID to an index name with INFORMATION_SCHEMA.TIDB_INDEXES.
- Classification Note: This is classified as diagnosis because the official content explains the cause of write conflicts, the monitoring metrics and log signatures used to detect them, and the identifiers used to inspect the conflicting key and transaction timestamps.

## Official Source Content

# Troubleshoot Write Conflicts in Optimistic Transactions

This document introduces the reason of and solutions to write conflicts in optimistic transactions.

Before TiDB v3.0.8, TiDB uses the optimistic transaction model by default. In this model, TiDB does not check conflicts during transaction execution. Instead, while the transaction is finally committed, the two-phase commit (2PC) is triggered and TiDB checks write conflicts. If a write conflict exists and the auto-retry mechanism is enabled, then TiDB retries the transaction within limited times. If the retry succeeds or has reached the upper limit on retry times, TiDB returns the result of transaction execution to the client. Therefore, if a lot of write conflicts exist in the TiDB cluster, the duration can be longer.
## The reason of write conflicts

TiDB implements its transactions by using the [Percolator](https://www.usenix.org/legacy/event/osdi10/tech/full_papers/Peng.pdf) transaction model. `percolator` is generally an implementation of 2PC. For the detailed 2PC process, see [TiDB Optimistic Transaction Model](https://docs.pingcap.com/tidb/stable/optimistic-transaction).

After the client sends a `COMMIT` request to TiDB, TiDB starts the 2PC process:

1. TiDB chooses one key from all keys in the transaction as the primary key of the transaction.
2. TiDB sends the `prewrite` request to all the TiKV Regions involved in this commit. TiKV judges whether all keys can preview successfully.
3. TiDB receives the result that all `prewrite` requests are successful.
4. TiDB gets the `commit_ts` from PD.
5. TiDB sends the `commit` request to the TiKV Region that contains the primary key of the transaction. After TiKV receives the `commit` request, it checks the validity of the data and clears the locks left in the `prewrite` stage.
6. After the `commit` request returns successfully, TiDB returns success to the client.

The write conflict occurs in the `prewrite` stage. When the transaction finds that another transaction is writing the current key (`data.commit_ts` > `txn.start_ts`), a write conflict occurs.
## Detect write conflicts

In the TiDB Grafana panel, check the following monitoring metrics under **KV Errors**:

* **KV Backoff OPS** indicates the count of error messages per second returned by TiKV.

    ![kv-backoff-ops](/media/troubleshooting-write-conflict-kv-backoff-ops.png)

    The `txnlock` metric indicates the write-write conflict. The `txnLockFast` metric indicates the read-write conflict.

* **Lock Resolve OPS** indicates the count of items related to transaction conflicts per second:

    ![lock-resolve-ops](/media/troubleshooting-write-conflict-lock-resolve-ops.png)

    - `not_expired` indicates the TTL of the lock was not expired. The conflict transaction cannot resolve locks until the TTL is expired.
    - `wait_expired` indicates that the transaction needs to wait the lock to expire.
    - `expired` indicates the TTL of the lock was expired. Then the conflict transaction can resolve this lock.

* **KV Retry Duration** indicates the duration of re-sends the KV request:

     ![kv-retry-duration](/media/troubleshooting-write-conflict-kv-retry-duration.png)

You can also use `[kv:9007]Write conflict` as the keywords to search in the TiDB log. The keywords also indicate the write conflict exists in the cluster.
## Resolve write conflicts

If many write conflicts exist in the cluster, it is recommended to find out the write conflict key and the reason, and then try to change the application logic to avoid write conflicts. When the write conflict exists in the cluster, you can see the log similar to the following one in the TiDB log file:

```log
[2020/05/12 15:17:01.568 +08:00] [WARN] [session.go:446] ["commit failed"] [conn=3] ["finished txn"="Txn{state=invalid}"] [error="[kv:9007]Write conflict, txnStartTS=416617006551793665, conflictStartTS=416617018650001409, conflictCommitTS=416617023093080065, key={tableID=47, indexID=1, indexValues={string, }} primary={tableID=47, indexID=1, indexValues={string, }} [try again later]"]
```

The explanation of the log above is as follows:

* `[kv:9007]Write conflict`: indicates the write-write conflict.
* `txnStartTS=416617006551793665`: indicates the `start_ts` of the current transaction. You can use the `pd-ctl` tool to convert `start_ts` to physical time.
* `conflictStartTS=416617018650001409`: indicates the `start_ts` of the write conflict transaction.
* `conflictCommitTS=416617023093080065`: indicates the `commit_ts` of the write conflict transaction.
* `key={tableID=47, indexID=1, indexValues={string, }}`: indicates the write conflict key. `tableID` indicates the ID of the write conflict table. `indexID` indicates the ID of write conflict index. If the write conflict key is a record key, the log prints `handle=x`, indicating which record(row) has a conflict. `indexValues` indicates the value of the index that has a conflict.
* `primary={tableID=47, indexID=1, indexValues={string, }}`: indicates the primary key information of the current transaction.

You can use the `pd-ctl` tool to convert the timestamp to readable time:

```shell
tiup ctl:v<CLUSTER_VERSION> pd -u https://127.0.0.1:2379 tso {TIMESTAMP}
```

You can use `tableID` to find the name of the related table:

```shell
curl http://{TiDBIP}:10080/db-table/{tableID}
```

You can use `indexID` and the table name to find the name of the related index:

```sql
SELECT * FROM INFORMATION_SCHEMA.TIDB_INDEXES WHERE TABLE_SCHEMA='{db_name}' AND TABLE_NAME='{table_name}' AND INDEX_ID={indexID};
```

In addition, in TiDB v3.0.8 and later versions, the pessimistic transaction becomes the default mode. The pessimistic transaction mode can avoid write conflicts during the transaction prewrite stage, so you do not need to modify the application any more. In the pessimistic transaction mode, each DML statement writes a pessimistic lock to the related keys during execution. This pessimistic lock can prevent other transactions from modifying the same keys, thus ensuring no write conflicts exist in the `prewrite` stage of the transaction 2PC.
