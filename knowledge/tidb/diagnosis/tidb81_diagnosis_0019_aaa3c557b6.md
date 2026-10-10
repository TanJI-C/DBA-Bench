# GC, transaction, and SQL execution timeouts

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-timeouts-in-tidb.md`
- Source Title: `Timeouts in TiDB`
- Source Heading Path: `Timeouts in TiDB | Timeouts in TiDB > GC timeout | Timeouts in TiDB > Transaction timeout | Timeouts in TiDB > SQL execution timeout`
- Source Line Ranges: `5-76`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `dumpling`, `sql`
- Topic Tags: `timeouts`, `gc`, `mvcc`, `transaction-timeout`, `idle-transaction-timeout`, `max-txn-ttl`, `sql-execution-time`, `read-only-queries`, `snapshot-retention`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0019_aaa3c557b6`
- Source ID: `tidb-docs-8.1:develop/dev-guide-timeouts-in-tidb.md#timeouts-in-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `deda44ebd6a5c0de48851f3dc67d2368169a3e973d087f6acb675eacc0fe2df4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-timeouts-in-tidb#timeouts-in-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-timeouts-in-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting TiDB timeout behavior involving GC retention, MVCC snapshots, long-running transactions, idle transaction timeout, or read-only SQL execution time limits.
- Retrieval Keywords: GC life time is shorter than transaction duration, MVCC, Garbage Collection, tikv_gc_life_time, mysql.tidb, tidb_gc_life_time, INFORMATION_SCHEMA.CLUSTER_INFO, Dumpling, GC safe point, max-txn-ttl, [performance], tidb_idle_transaction_timeout, INSERT INTO t10 SELECT * FROM t1, max_execution_time, read-only SQL statements, 100ms level
- Follow-up Guidance: The source also points to GC Overview and Manually set the TiDB GC time for more details about garbage collection and Dumpling export scenarios.
- Classification Note: This chunk is classified as diagnosis because it explains timeout-related errors and limits for GC, transactions, and SQL execution, including the exact variables and messages involved.

## Official Source Content

# Timeouts in TiDB

This document describes various timeouts in TiDB to help you troubleshoot errors.
## GC timeout

TiDB's transaction implementation uses the MVCC (Multiple Version Concurrency Control) mechanism. When the newly written data overwrites the old data, the old data will not be replaced, but kept together with the newly written data. The versions are distinguished by the timestamp. TiDB uses the mechanism of periodic Garbage Collection (GC) to clean up the old data that is no longer needed.

- For TiDB versions earlier than v4.0:

    By default, each MVCC version (consistency snapshots) is kept for 10 minutes. Transactions that take longer than 10 minutes to read will receive an error `GC life time is shorter than transaction duration`.

- For TiDB v4.0 and later versions:

    For running transactions that do not exceed a duration of 24 hours, garbage collection (GC) are blocked during the transaction execution. The error `GC life time is shorter than transaction duration` does not occur.

If you need longer read time temporarily in some cases, you can increase the retention time of MVCC versions:

- For TiDB versions earlier than v5.0: adjust `tikv_gc_life_time` in the `mysql.tidb` table in TiDB.
- For TiDB v5.0 and later versions: adjust the system variable [`tidb_gc_life_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_life_time-new-in-v50).

Note that the system variable configuration takes effect globally and immediately. Increasing its value will increase the life time of all existing snapshots, and decreasing it will immediately shorten the life time of all snapshots. Too many MVCC versions will impact the performance of the TiDB cluster. So you need to change this variable back to the previous setting in time.

> **Tip:**
>
> Specifically, when Dumpling is exporting data from TiDB (less than 1 TB), if the TiDB version is v4.0.0 or later and Dumpling can access the PD address and the [`INFORMATION_SCHEMA.CLUSTER_INFO`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-cluster-info) table of the TiDB cluster, Dumpling automatically adjusts the GC safe point to block GC without affecting the original cluster.
>
> However, in either of the following scenarios, Dumpling cannot automatically adjust the GC time:
>
> - The data size is very large (more than 1 TB).
> - Dumpling cannot connect directly to PD, for example, the TiDB cluster is on TiDB Cloud or on Kubernetes that is separated from Dumpling.
>
> In such scenarios, you must manually extend the GC time in advance to avoid export failure due to GC during the export process.
>
> For more details, see [Manually set the TiDB GC time](https://docs.pingcap.com/tidb/stable/dumpling-overview#manually-set-the-tidb-gc-time).

> **Tip:**
>
> Specifically, when Dumpling is exporting data from TiDB (less than 1 TB), if the TiDB version is later than or equal to v4.0.0 and Dumpling can access the PD address of the TiDB cluster, Dumpling automatically extends the GC time without affecting the original cluster.
>
> However, in either of the following scenarios, Dumpling cannot automatically adjust the GC time:
>
> - The data size is very large (more than 1 TB).
> - Dumpling cannot connect directly to PD, for example, the TiDB cluster is on TiDB Cloud or on Kubernetes that is separated from Dumpling.
>
> In such scenarios, you must manually extend the GC time in advance to avoid export failure due to GC during the export process.
>
> For more details, see [Manually set the TiDB GC time](https://docs.pingcap.com/tidb/stable/dumpling-overview#manually-set-the-tidb-gc-time).

For more information about GC, see [GC Overview](https://docs.pingcap.com/tidb/stable/garbage-collection-overview).
## Transaction timeout

In scenarios where a transaction starts but is neither committed nor rolled back, you might need a finer-grained control and a shorter timeout to prevent prolonged lock holding.  In this case, you can use [`tidb_idle_transaction_timeout`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_idle_transaction_timeout-new-in-v760) (introduced in TiDB v7.6.0) to control the idle timeout for transactions in a user session.

GC does not affect ongoing transactions. However, there is still an upper limit to the number of pessimistic transactions that can run, with a limit on the transaction timeout and a limit on the memory used by the transaction. You can modify the transaction timeout by `max-txn-ttl` under the `[performance]` category of the TiDB profile, `60` minutes by default.

SQL statements such as `INSERT INTO t10 SELECT * FROM t1` are not affected by GC, but will be rolled back due to timeout after exceeding `max-txn-ttl`.
## SQL execution timeout

TiDB also provides a system variable (`max_execution_time`, `0` by default, indicating no limit) to limit the execution time of a single SQL statement. Currently, the system variable only takes effect for read-only SQL statements. The unit of `max_execution_time` is `ms`, but the actual precision is at the `100ms` level instead of the millisecond level.
