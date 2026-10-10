# TiDB 3.0.8 fixes and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.8.md`
- Source Title: `TiDB 3.0.8 Release Notes`
- Source Heading Path: `TiDB 3.0.8 Release Notes > TiDB`
- Source Line Ranges: `14-75`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`, `shared`
- Topic Tags: `sql-optimizer`, `sql-execution`, `ddl`, `server`, `statement-summary`, `binlog`, `privileges`, `authentication`, `transactions`, `monitoring`, `pessimistic-transactions`, `configuration`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0128_9986cb7f70`
- Source ID: `tidb-docs-8.1:releases/release-3.0.8.md#tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `22985d2eeda11b06bee5188c0e30d9e62b8da0732485b40ae56326b7cdc30714`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.8#tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.8.md

## Retrieval Guidance

- Use When: Use this chunk when you need the list of TiDB 3.0.8 fixes and improvements across SQL Optimizer, SQL Execution Engine, DDL, Server, Transaction, and Monitor.
- Retrieval Keywords: TiDB 3.0.8 fixes and improvements, SQL Optimizer SQL binding plan cache updates, PhysicalUnionScan wrong statistics, minAutoAnalyzeRatio autoAnalyze, INSERT REPLACE UPDATE SET DEFAULT virtual generated column, EXPLAIN ANALYZE ExplainExec goroutine leak, SPLIT PARTITION TABLE, GC life time is shorter than transaction duration, information_schema.KEY_COLUMN_USAGE DROP COLUMN MODIFY COLUMN CHANGE COLUMN, Statement Summary improvements, stmt-summary.refresh-interval, events_statements_summary_by_digest, events_statements_summary_by_digest_history, server-version configuration item, HTTP interface recover writing the TiDB binlog, GRANT roles TO user ROLE_ADMIN SUPER, No database selected GRANT statement, GRANT ALL WITH GRANT OPTION GrantPriv, LOAD DATA LoadDataInfo addRecord, system_time_zone mysql.tidb systemTZ, SHUTDOWN command ShutdownPriv, tidb_enable_window_function SHOW VARIABLE, tidb_enable_table_partition GLOBAL SCOPE, certificate-based authentication, tidb_txn_mode pessimistic, pessimistic transaction lock waiting time, pessimistic_lock_keys_duration
- Follow-up Guidance: This chunk is useful to continue into specific TiDB 3.0.8 changes such as statement summary tables and parameters, privilege behavior, transaction fixes, monitoring items, and added syntax like `SPLIT PARTITION TABLE` and `SHUTDOWN`.
- Classification Note: This is classified as a TiDB release change list because the content enumerates TiDB 3.0.8 bug fixes, behavior changes, configuration items, syntax additions, and monitoring updates within the TiDB component.

## Official Source Content

## TiDB

+ SQL Optimizer
    - Fix the wrong SQL binding plan caused by untimely cache updates [#13891](https://github.com/pingcap/tidb/pull/13891)
    - Fix the issue that the SQL binding might be invalid when an SQL statement contains a symbol list [#14004](https://github.com/pingcap/tidb/pull/14004)
    - Fix the issue that an SQL binding cannot be created or deleted because an SQL statement ends with `;` [#14113](https://github.com/pingcap/tidb/pull/14113)
    - Fix the issue that a wrong SQL query plan might be selected because the `PhysicalUnionScan` operator sets wrong statistics [#14133](https://github.com/pingcap/tidb/pull/14133)
    - Remove the `minAutoAnalyzeRatio` restriction to make `autoAnalyze` more timely [#14015](https://github.com/pingcap/tidb/pull/14015)
+ SQL Execution Engine
    - Fix issues that the `INSERT/REPLACE/UPDATE ... SET ... = DEFAULT` syntax might report an error and combining the usage of the `DEFAULT` expression with a virtual generated column might report an error [#13682](https://github.com/pingcap/tidb/pull/13682)
    - Fix the issue that the `INSERT` statement might report an error when converting a string to a float [#14011](https://github.com/pingcap/tidb/pull/14011)
    - Fix the issue that sometimes the aggregate operation is low effective because the concurrency value of the `HashAgg` executor is incorrectly initialized [#13811](https://github.com/pingcap/tidb/pull/13811)
    - Fix the issue that an error is reported in the execution of`group by item` when the clause is in the parentheses [#13658](https://github.com/pingcap/tidb/pull/13658)
    - Fix the issue that the execution of `OUTER JOIN` might report an error because TiDB incorrectly calculates `group by item` [#14014](https://github.com/pingcap/tidb/pull/14014)
    - Fix the issue that the error message is inaccurate when Range-exceeding data is written into Range partitioned tables [#14107](https://github.com/pingcap/tidb/pull/14107)
    - Revert [PR #10124](https://github.com/pingcap/tidb/pull/10124) and cancel the `PadCharToFullLength` effect to avoid unexpected query results in special cases, considering that MySQL 8 will discard `PadCharToFullLength` soon [#14157](https://github.com/pingcap/tidb/pull/14157)
    - Fix the goroutine leak issue when executing the `EXPLAIN ANALYZE` statement caused by unguaranteed `close()` calling in `ExplainExec` [#14226](https://github.com/pingcap/tidb/pull/14226)
+ DDL
    - Optimize the error message output of `change column`/`modify column` to make it easier to understand [#13796](https://github.com/pingcap/tidb/pull/13796)
    - Add the `SPLIT PARTITION TABLE` syntax to support splitting Regions for partitioned tables [#13929](https://github.com/pingcap/tidb/pull/13929)
    - Fix the issue that the index length exceeds 3072 bytes and no error is reported because the index length is incorrectly checked when an index is created [#13779](https://github.com/pingcap/tidb/pull/13779)
    - Fix the issue that the `GC life time is shorter than transaction duration` error message might be reported because it takes too much time to add an index in partitioned tables [#14132](https://github.com/pingcap/tidb/pull/14132)
    - Fix the panic when `SELECT * FROM information_schema.KEY_COLUMN_USAGE` is executed because the foreign key is not checked when `DROP COLUMN`/`MODIFY COLUMN`/`CHANGE COLUMN` is executed [#14105](https://github.com/pingcap/tidb/pull/14105)
+ Server
    - Statement Summary improvements:
        - Add a large number of SQL metric fields to facilitate analyzing SQL statements in more detail [#14151](https://github.com/pingcap/tidb/pull/14151), [#14168](https://github.com/pingcap/tidb/pull/14168)
        - Add the `stmt-summary.refresh-interval` parameter to control whether to move the stale data from the `events_statements_summary_by_digest` table to the `events_statements_summary_by_digest_history` table (the default interval: 30 minutes) [#14161](https://github.com/pingcap/tidb/pull/14161)
        - Add the `events_statements_summary_by_digest_history` table to save the stale data in `events_statements_summary_by_digest` [#14166](https://github.com/pingcap/tidb/pull/14166)
    - Fix the issue that the binlog is incorrectly output when RBAC-related internal SQL statements are executed [#13890](https://github.com/pingcap/tidb/pull/13890)
    - Add the `server-version` configuration item to control the feature of modifying the TiDB server version [#13906](https://github.com/pingcap/tidb/pull/13906)
    - Add the feature of using the HTTP interface to recover writing the TiDB binlog [#13892](https://github.com/pingcap/tidb/pull/13892)
    - Update the privilege required by `GRANT roles TO user` from `GrantPriv` to `ROLE_ADMIN` or `SUPER`, to keep consistency with the MySQL behavior [#13932](https://github.com/pingcap/tidb/pull/13932)
    - Modify the TiDB behavior from using the current database to reporting the `No database selected` error when the `GRANT` statement does not specify a database name, to keep compatibility with the MySQL behavior [#13784](https://github.com/pingcap/tidb/pull/13784)
    - Modify the execution privilege for the `REVOKE` statement from `SuperPriv` to `REVOKE` being executable only if the user has the privilege for the corresponding schema, to keep consistency with the MySQL behavior [#13306](https://github.com/pingcap/tidb/pull/13306)
    - Fix the issue that `GrantPriv` is mistakenly granted to the target user when the `GRANT ALL` syntax does not contain `WITH GRANT OPTION` [#13943](https://github.com/pingcap/tidb/pull/13943)
    - Fix the issue that the error message does not contain the cause for the `LOAD DATA` statement's wrong behavior when `LoadDataInfo` fails to call `addRecord` [#13980](https://github.com/pingcap/tidb/pull/13980)
    - Fix the issue that wrong slow query information is output because multiple SQL statements in a query share the same `StartTime` [#13898](https://github.com/pingcap/tidb/pull/13898)
    - Fix the issue that the memory might leak when `batchClient` processes a large transaction [#14032](https://github.com/pingcap/tidb/pull/14032)
    - Fix the issue that `system_time_zone` is always displayed as `CST` and now TiDB's `system_time_zone` is obtained from `systemTZ` in the `mysql.tidb` table [#14086](https://github.com/pingcap/tidb/pull/14086)
    - Fix the issue that the `GRANT ALL` syntax does not grant all privileges to the user [#14092](https://github.com/pingcap/tidb/pull/14092)
    - Fix the issue that the `Priv_create_user` privilege is invalid for `CREATE ROLE` and `DROP ROLE` [#14088](https://github.com/pingcap/tidb/pull/14088)
    - Modify the error code of `ErrInvalidFieldSize` from `1105(Unknow Error)` to `3013` [#13737](https://github.com/pingcap/tidb/pull/13737)
    - Add the `SHUTDOWN` command to stop a TiDB server and add the `ShutdownPriv` privilege [#14104](https://github.com/pingcap/tidb/pull/14104)
    - Fix the atomicity issue for the `DROP ROLE` statement to avoid some roles being deleted unexpectedly when TiDB fails to execute a statement [#14130](https://github.com/pingcap/tidb/pull/14130)
    - Fix the issue that the `tidb_enable_window_function` in the `SHOW VARIABLE` result incorrectly outputs `1` when a TiDB version is upgraded to 3.0, and replace the wrong result with `0` [#14131](https://github.com/pingcap/tidb/pull/14131)
    - Fix the issue that the goroutine might leak because `gcworker` continuously retries when the TiKV node is offline [#14106](https://github.com/pingcap/tidb/pull/14106)
    - Record the binlog `Prewrite` time in the slow query log to improve the usability for issue tracking [#14138](https://github.com/pingcap/tidb/pull/14138)
    - Make the `tidb_enable_table_partition` variable support `GLOBAL SCOPE` [#14091](https://github.com/pingcap/tidb/pull/14091)
    - Fix the issue that the user privilege might be missing or mistakenly added because the newly added privilege is not correctly granted to the corresponding user when a new privilege is added [#14178](https://github.com/pingcap/tidb/pull/14178)
    - Fix the issue that the `CheckStreamTimeoutLoop` goroutine might leak because `rpcClient` does not close when the TiKV server is disconnected [#14227](https://github.com/pingcap/tidb/pull/14227)
    - Support certificate-based authentication ([User document](https://docs.pingcap.com/tidb/stable/certificate-authentication)) [#13955](https://github.com/pingcap/tidb/pull/13955)
+ Transaction
    - Update the default value of the `tidb_txn_mode` variable from `""` to `"pessimistic"` when a new cluster is created [#14171](https://github.com/pingcap/tidb/pull/14171)
    - Fix the issue that the lock waiting time is too long for a pessimistic transaction because the lock waiting time for a single statement is not reset when a transaction is retried [#13990](https://github.com/pingcap/tidb/pull/13990)
    - Fix the issue that wrong data might be read because unmodified data is unlocked for the pessimistic transaction mode [#14050](https://github.com/pingcap/tidb/pull/14050)
    - Fix repeated insert value restriction checks because transaction types are not distinguished when prewrite is performed in mocktikv [#14175](https://github.com/pingcap/tidb/pull/14175)
    - Fix the panic because transactions are not correctly handled when `session.TxnState` is `Invalid` [#13988](https://github.com/pingcap/tidb/pull/13988)
    - Fix the issue that the `ErrConfclit` structure in mocktikv does not contain `ConflictCommitTS` [#14080](https://github.com/pingcap/tidb/pull/14080)
    - Fix the issue that the transaction is blocked because TiDB does not correctly check lock timeout after resolving the lock [#14083](https://github.com/pingcap/tidb/pull/14083)
+ Monitor
    - Add the `pessimistic_lock_keys_duration` monitoring item in `LockKeys` [#14194](https://github.com/pingcap/tidb/pull/14194)
