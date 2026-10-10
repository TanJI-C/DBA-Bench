# User-level locking functions and MySQL compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/locking-functions.md`
- Source Title: `Locking Functions`
- Source Heading Path: `Locking Functions | Locking Functions > Supported functions | Locking Functions > MySQL compatibility`
- Source Line Ranges: `5-25`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `locking-functions`, `advisory-locks`, `mysql-compatibility`, `timeouts`, `deadlocks`, `sessions`, `cluster-scope`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0325_d4855f2609`
- Source ID: `tidb-docs-8.1:functions-and-operators/locking-functions.md#locking-functions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f582312b30b89473061c15810f5b791294d6637a89cdeaec61754d80233c12af`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/locking-functions#locking-functions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/locking-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB SQL user-level locking functions, their timeout limits, and MySQL compatibility differences for advisory locks.
- Retrieval Keywords: locking functions, user-level locking functions, advisory lock, GET_LOCK(lockName, timeout), IS_FREE_LOCK(lockName), IS_USED_LOCK(lockName), RELEASE_ALL_LOCKS(), RELEASE_LOCK(lockName), lockName no longer than 64 characters, minimum timeout 1 second, maximum timeout 3600 seconds, timeout=-1 converted to 3600 seconds, out-of-range values converted to nearest permitted value, deadlocks caused by user-level locks, KILL, locks take effect on all TiDB servers in the cluster, IS_USED_LOCK returns 1 from another session
- Follow-up Guidance: The content notes that deadlocked sessions time out after a maximum of 1 hour and can also be manually resolved by using KILL on one of the affected sessions.
- Classification Note: This is reference content because it lists supported SQL locking functions and documents TiDB-specific compatibility behavior such as timeout bounds, deadlock handling, cluster-wide lock scope, and IS_USED_LOCK() return behavior.

## Official Source Content

# Locking Functions

TiDB supports most of the user-level [locking functions](https://dev.mysql.com/doc/refman/8.0/en/locking-functions.html) available in MySQL 8.0.
## Supported functions

| Name                                                                                                                 | Description                                                           |
|:---------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------|
| [`GET_LOCK(lockName, timeout)`](https://dev.mysql.com/doc/refman/8.0/en/locking-functions.html#function_get-lock)    | Acquires an advisory lock. The `lockName` parameter must be NO longer than 64 characters. Waits maximum `timeout` seconds before timing out and returns a failure.         |
| [`IS_FREE_LOCK(lockName)`](https://dev.mysql.com/doc/refman/8.0/en/locking-functions.html#function_is-free-lock) | Checks if a lock is free. |
| [`IS_USED_LOCK(lockName)`](https://dev.mysql.com/doc/refman/8.0/en/locking-functions.html#function_is-used-lock) | Checks if a lock is in use. If true, it returns the corresponding connection ID. |
| [`RELEASE_ALL_LOCKS()`](https://dev.mysql.com/doc/refman/8.0/en/locking-functions.html#function_release-all-locks)   | Releases all locks held by the current session.                        |
| [`RELEASE_LOCK(lockName)`](https://dev.mysql.com/doc/refman/8.0/en/locking-functions.html#function_release-lock)     | Releases a previously acquired lock. The `lockName` parameter must be NO longer than 64 characters. |
## MySQL compatibility

* The minimum timeout permitted by TiDB is 1 second, and the maximum timeout is 1 hour (3600 seconds). This differs from MySQL, where both 0 second and unlimited timeouts (`timeout=-1`) are permitted. TiDB will automatically convert out-of-range values to the nearest permitted value and convert `timeout=-1` to 3600 seconds.
* TiDB does not automatically detect deadlocks caused by user-level locks. Deadlocked sessions will time out after a maximum of 1 hour, but can also be manually resolved by using [`KILL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-kill) on one of the affected sessions. You can also prevent deadlocks by always acquiring user-level locks in the same order.
* Locks take effect on all TiDB servers in the cluster. This differs from MySQL Cluster and Group Replication where locks are local to a single server.
* `IS_USED_LOCK()` returns `1` if it is called from another session and is unable to return the ID of the process that is holding the lock.
