# Inspect blocking transactions with Lock View

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-lock-conflicts.md`
- Source Title: `Troubleshoot Lock Conflicts`
- Source Heading Path: `Troubleshoot Lock Conflicts > Use Lock View to troubleshoot lock issues > A transaction is blocked for a long time`
- Source Line Ranges: `126-161`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `lock-view`, `blocking-transactions`, `start-ts`, `data-lock-waits`, `cluster-tidb-trx`, `processlist`, `sql-digests`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0134_f6b1196659`
- Source ID: `tidb-docs-8.1:troubleshoot-lock-conflicts.md#a-transaction-is-blocked-for-a-long-time`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `264a43d06957d09a0cb7656e80691b81d4c6c2d72cad51ac32f608c3bc270458`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-lock-conflicts#a-transaction-is-blocked-for-a-long-time
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-lock-conflicts.md

## Retrieval Guidance

- Use When: Use this chunk when you know a blocked transaction's start_ts and need to inspect the blocking transaction through Lock View system tables.
- Retrieval Keywords: Lock View, A transaction is blocked for a long time, information_schema.data_lock_waits, information_schema.cluster_tidb_trx, start_ts, transaction ID, current_holding_trx_id, trx_id, TIDB_DECODE_SQL_DIGESTS, ALL_SQL_DIGESTS, PROCESSLIST, CLUSTER_PROCESSLIST, TIDB_TRX, CLUSTER_TIDB_TRX, blocking transaction, data_lock_waits join cluster_tidb_trx
- Follow-up Guidance: If the current transaction's start_ts is unknown, the source says you can try to find it from TIDB_TRX or CLUSTER_TIDB_TRX, or from PROCESSLIST or CLUSTER_PROCESSLIST.
- Classification Note: This is classified as diagnosis because the content shows a SQL query and related system tables for identifying blocking transactions and decoding their SQL digests.

## Official Source Content

### A transaction is blocked for a long time

If a transaction is known to be blocked by another transaction (or multiple transactions) and the `start_ts` (transaction ID) of the current transaction is known, you can use the following method to obtain the information of the blocking transaction. Note that when you join multiple tables in Lock View, the data in different tables might not be obtained at the same time, so the information in different tables might not be consistent.

```sql
select l.key, trx.*, tidb_decode_sql_digests(trx.all_sql_digests) as sqls from information_schema.data_lock_waits as l join information_schema.cluster_tidb_trx as trx on l.current_holding_trx_id = trx.id where l.trx_id = 426831965449355272\G
```

The following is an example output:

```sql
*************************** 1. row ***************************
                    key: 74800000000000004D5F728000000000000001
               INSTANCE: 127.0.0.1:10080
                     ID: 426832040186609668
             START_TIME: 2021-08-06 07:30:16.581000
     CURRENT_SQL_DIGEST: 06da614b93e62713bd282d4685fc5b88d688337f36e88fe55871726ce0eb80d7
CURRENT_SQL_DIGEST_TEXT: update `t` set `v` = `v` + ? where `id` = ? ;
                  STATE: LockWaiting
     WAITING_START_TIME: 2021-08-06 07:30:16.592763
        MEM_BUFFER_KEYS: 1
       MEM_BUFFER_BYTES: 19
             SESSION_ID: 113
                   USER: root
                     DB: test
        ALL_SQL_DIGESTS: ["0fdc781f19da1c6078c9de7eadef8a307889c001e05f107847bee4cfc8f3cdf3","a4e28cc182bdd18288e2a34180499b9404cd0ba07e3cc34b6b3be7b7c2de7fe9","06da614b93e62713bd282d4685fc5b88d688337f36e88fe55871726ce0eb80d7"]
                   sqls: ["begin ;","select * from `t` where `id` = ? for update ;","update `t` set `v` = `v` + ? where `id` = ? ;"]
1 row in set (0.01 sec)
```

In the above query, the [`TIDB_DECODE_SQL_DIGESTS`](https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions#tidb_decode_sql_digests) function is used on the `ALL_SQL_DIGESTS` column of the `CLUSTER_TIDB_TRX` table. This function tries to convert this column (the value is a set of SQL digests) to the normalized SQL statements, which improves readability.

If the `start_ts` of the current transaction is unknown, you can try to find it out from the information in the `TIDB_TRX` / `CLUSTER_TIDB_TRX` table or in the [`PROCESSLIST` / `CLUSTER_PROCESSLIST`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-processlist) table.
