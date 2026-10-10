# Lock View troubleshooting for deadlocks and hot-key lock waits

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-lock-conflicts.md`
- Source Title: `Troubleshoot Lock Conflicts`
- Source Heading Path: `Troubleshoot Lock Conflicts | Troubleshoot Lock Conflicts > Use Lock View to troubleshoot lock issues | Troubleshoot Lock Conflicts > Use Lock View to troubleshoot lock issues > Deadlock errors | Troubleshoot Lock Conflicts > Use Lock View to troubleshoot lock issues > A few hot keys cause queueing locks`
- Source Line Ranges: `5-125`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `lock-view`, `deadlocks`, `pessimistic-locks`, `lock-waits`, `hot-keys`, `information-schema`, `transactions`, `sql-digests`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0133_f5a7201822`
- Source ID: `tidb-docs-8.1:troubleshoot-lock-conflicts.md#troubleshoot-lock-conflicts`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d8c02e8f31239f8b4dbed8015a9a969178cf27c5ff947cb0e91493fb42c78c11`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-lock-conflicts#troubleshoot-lock-conflicts
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-lock-conflicts.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing pessimistic lock conflicts with Lock View, especially recent deadlock errors or queueing lock waits caused by a few hot keys.
- Retrieval Keywords: Lock View, information_schema, DEADLOCKS, CLUSTER_DEADLOCKS, DATA_LOCK_WAITS, TIDB_TRX, CLUSTER_TIDB_TRX, pessimistic locks only, deadlock errors, hot keys, queueing locks, select * from information_schema.deadlocks;, select `key`, count(*) as `count` from information_schema.data_lock_waits group by `key` order by `count` desc;, CURRENT_SQL_DIGEST, CURRENT_SQL_DIGEST_TEXT, KEY_INFO, TRX_HOLDING_LOCK, LockWaiting, WAITING_START_TIME, normalized SQL statements, SQL digests
- Follow-up Guidance: The source also shows joining information_schema.data_lock_waits with information_schema.cluster_tidb_trx by transaction ID for a specific key, and notes that Lock View tables show running transactions only and joined table data might not be obtained at the same time.
- Classification Note: This is classified as diagnosis because the content explains how Lock View system tables expose waiting relationships, lock-waiting status, transaction state, SQL digests, and key information to troubleshoot deadlocks and hot-key lock waits.

## Official Source Content

# Troubleshoot Lock Conflicts

TiDB supports complete distributed transactions. Starting from v3.0, TiDB provides optimistic transaction mode and pessimistic transaction mode. This document describes how to use Lock View to troubleshoot lock issues and how to deal with common lock conflict issues in optimistic and pessimistic transactions.
## Use Lock View to troubleshoot lock issues

Since v5.1, TiDB supports the Lock View feature. This feature has several system tables built in `information_schema` that provide more information about the lock conflicts and lock waitings.

> **Note:**
>
> Currently, the Lock View feature provides conflict and waiting information for pessimistic locks only.

For the detailed introduction of these tables, see the following documents:

* [`TIDB_TRX` and `CLUSTER_TIDB_TRX`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-trx): Provides information of all running transactions on the current TiDB node or in the entire cluster, including whether the transaction is in the lock-waiting state, the lock-waiting time, and the digests of statements that have been executed in the transaction.
* [`DATA_LOCK_WAITS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-data-lock-waits): Provides the pessimistic lock-waiting information in TiKV, including the `start_ts` of the blocking and blocked transaction, the digest of the blocked SQL statement, and the key on which the waiting occurs.
* [`DEADLOCKS` and `CLUSTER_DEADLOCKS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-deadlocks): Provides the information of several deadlock events that have recently occurred on the current TiDB node or in the entire cluster, including the waiting relationship among transactions in the deadlock loops, the digest of the statement currently being executed in the transaction, and the key on which the waiting occurs.

> **Note:**
>
> The SQL statements shown in the Lock View-related system tables are normalized SQL statements (that is, SQL statements without formats and arguments), which are obtained by internal queries according to SQL digests, so the tables cannot obtain the complete statements that include the format and arguments. For the detailed description of SQL digests and normalized SQL statement, see [Statement Summary Tables](https://docs.pingcap.com/tidb/stable/statement-summary-tables).

The following sections show the examples of troubleshooting some issues using these tables.
### Deadlock errors

To get the information of the recent deadlock errors, you can query the `DEADLOCKS` or `CLUSTER_DEADLOCKS` table.

For example, to query the `DEADLOCKS` table, you can execute the following SQL statement:

```sql
select * from information_schema.deadlocks;
```

The following is an example output:

```sql
+-------------+----------------------------+-----------+--------------------+------------------------------------------------------------------+-----------------------------------------+----------------------------------------+----------------------------------------------------------------------------------------------------+--------------------+
| DEADLOCK_ID | OCCUR_TIME                 | RETRYABLE | TRY_LOCK_TRX_ID    | CURRENT_SQL_DIGEST                                               | CURRENT_SQL_DIGEST_TEXT                 | KEY                                    | KEY_INFO                                                                                           | TRX_HOLDING_LOCK   |
+-------------+----------------------------+-----------+--------------------+------------------------------------------------------------------+-----------------------------------------+----------------------------------------+----------------------------------------------------------------------------------------------------+--------------------+
|           1 | 2021-08-05 11:09:03.230341 |         0 | 426812829645406216 | 22230766411edb40f27a68dadefc63c6c6970d5827f1e5e22fc97be2c4d8350d | update `t` set `v` = ? where `id` = ? ; | 7480000000000000355F728000000000000002 | {"db_id":1,"db_name":"test","table_id":53,"table_name":"t","handle_type":"int","handle_value":"2"} | 426812829645406217 |
|           1 | 2021-08-05 11:09:03.230341 |         0 | 426812829645406217 | 22230766411edb40f27a68dadefc63c6c6970d5827f1e5e22fc97be2c4d8350d | update `t` set `v` = ? where `id` = ? ; | 7480000000000000355F728000000000000001 | {"db_id":1,"db_name":"test","table_id":53,"table_name":"t","handle_type":"int","handle_value":"1"} | 426812829645406216 |
+-------------+----------------------------+-----------+--------------------+------------------------------------------------------------------+-----------------------------------------+----------------------------------------+----------------------------------------------------------------------------------------------------+--------------------+
```

The query result above shows the waiting relationship among multiple transactions in the deadlock error, the normalized form of the SQL statements currently being executed in each transaction (statements without formats and arguments), the key on which the conflict occurs, and the information of the key.

For example, in the above example, the first row means that the transaction with the ID of `426812829645406216` is executing a statement like ``update `t` set `v` =? Where `id` =? ;`` but is blocked by another transaction with the ID of `426812829645406217`. The transaction with the ID of `426812829645406217` is also executing a statement that is in the form of ``update `t` set `v` =? Where `id` =? ;`` but is blocked by the transaction with the ID of `426812829645406216`. The two transactions thus form a deadlock.
### A few hot keys cause queueing locks

The `DATA_LOCK_WAITS` system table provides the lock-waiting status on the TiKV nodes. When you query this table, TiDB automatically obtains the real-time lock-waiting information from all TiKV nodes. If a few hot keys are frequently locked and block many transactions, you can query the `DATA_LOCK_WAITS` table and aggregate the results by key to try to find the keys on which issues frequently occur:

```sql
select `key`, count(*) as `count` from information_schema.data_lock_waits group by `key` order by `count` desc;
```

The following is an example output:

```sql
+----------------------------------------+-------+
| key                                    | count |
+----------------------------------------+-------+
| 7480000000000000415F728000000000000001 |     2 |
| 7480000000000000415F728000000000000002 |     1 |
+----------------------------------------+-------+
```

To avoid contingency, you might need to make multiple queries.

If you know the key that frequently has issues occurred, you can try to get the information of the transaction that tries to lock the key from the `TIDB_TRX` or `CLUSTER_TIDB_TRX` table.

Note that the information displayed in the `TIDB_TRX` and `CLUSTER_TIDB_TRX` tables is also the information of the transactions that are running at the time the query is performed. These tables do not display the information of the completed transactions. If there is a large number of concurrent transactions, the result set of the query might also be large. You can use the `limit` clause or the `where` clause to filter transactions with a long lock-waiting time. Note that when you join multiple tables in Lock View, the data in different tables might not be obtained at the same time, so the information in different tables might not be consistent.

For example, to filter transactions with a long lock-waiting time using the `where` clause, you can execute the following SQL statement:

```sql
select trx.* from information_schema.data_lock_waits as l left join information_schema.cluster_tidb_trx as trx on l.trx_id = trx.id where l.key = "7480000000000000415F728000000000000001"\G
```

The following is an example output:

```sql
*************************** 1. row ***************************
               INSTANCE: 127.0.0.1:10080
                     ID: 426831815660273668
             START_TIME: 2021-08-06 07:16:00.081000
     CURRENT_SQL_DIGEST: 06da614b93e62713bd282d4685fc5b88d688337f36e88fe55871726ce0eb80d7
CURRENT_SQL_DIGEST_TEXT: update `t` set `v` = `v` + ? where `id` = ? ;
                  STATE: LockWaiting
     WAITING_START_TIME: 2021-08-06 07:16:00.087720
        MEM_BUFFER_KEYS: 0
       MEM_BUFFER_BYTES: 0
             SESSION_ID: 77
                   USER: root
                     DB: test
        ALL_SQL_DIGESTS: ["0fdc781f19da1c6078c9de7eadef8a307889c001e05f107847bee4cfc8f3cdf3","06da614b93e62713bd282d4685fc5b88d688337f36e88fe55871726ce0eb80d7"]
*************************** 2. row ***************************
               INSTANCE: 127.0.0.1:10080
                     ID: 426831818019569665
             START_TIME: 2021-08-06 07:16:09.081000
     CURRENT_SQL_DIGEST: 06da614b93e62713bd282d4685fc5b88d688337f36e88fe55871726ce0eb80d7
CURRENT_SQL_DIGEST_TEXT: update `t` set `v` = `v` + ? where `id` = ? ;
                  STATE: LockWaiting
     WAITING_START_TIME: 2021-08-06 07:16:09.290271
        MEM_BUFFER_KEYS: 0
       MEM_BUFFER_BYTES: 0
             SESSION_ID: 75
                   USER: root
                     DB: test
        ALL_SQL_DIGESTS: ["0fdc781f19da1c6078c9de7eadef8a307889c001e05f107847bee4cfc8f3cdf3","06da614b93e62713bd282d4685fc5b88d688337f36e88fe55871726ce0eb80d7"]
2 rows in set (0.00 sec)
```
