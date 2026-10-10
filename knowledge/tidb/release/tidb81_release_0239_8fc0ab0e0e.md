# TiDB 5.2 new features and feature enhancements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.2.0.md`
- Source Title: `TiDB 5.2 Release Notes`
- Source Heading Path: `TiDB 5.2 Release Notes > New features > SQL | TiDB 5.2 Release Notes > New features > Transaction | TiDB 5.2 Release Notes > New features > Stability | TiDB 5.2 Release Notes > New features > Data Migration | TiDB 5.2 Release Notes > New features > TiDB data share subscription | TiDB 5.2 Release Notes > New features > Deployment and operations | TiDB 5.2 Release Notes > Feature Enhancements`
- Source Line Ranges: `72-195`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `sql`, `tikv`, `tiflash`, `dm`, `lightning`, `ticdc`, `dumpling`, `pd`, `tiup`
- Topic Tags: `release-notes`, `new-features`, `feature-enhancements`, `sql`, `transactions`, `lock-view`, `stability`, `flow-control`, `slow-node-detection`, `data-migration`, `cdc`, `deployment`, `tools`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0239_8fc0ab0e0e`
- Source ID: `tidb-docs-8.1:releases/release-5.2.0.md#sql`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9b4f84baf1d8306c44be9a27e7bfbb6e205f9a7478e38668f631707ec1f0ac7f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.2.0#sql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 5.2 release-note content about new features and feature enhancements across SQL, transactions, stability, data migration, TiCDC subscription, deployment, and tools.
- Retrieval Keywords: TiDB 5.2 Release Notes, expression index, translate function in Oracle, HashAgg spill to disk, tidb_opt_limit_push_down_threshold, optimizer cardinality estimation, choose-index, Lock View, DATA_LOCK_WAITS, DEADLOCKS, TIDB_TRX, TIDB_DECODE_SQL_DIGESTS, pessimistic-txn.deadlock-history-collect-retryable, AUTO_RANDOM, SHARD_ROW_ID_BITS, TiFlash I/O Rate Limiter, storage.flow-control, flow control mechanism, slow node detection, evict-slow-store-scheduler, inspect-interval, DM v2.0.6, VIP, TiDB Lightning customized line terminators, HTTP protocol OpenAPI, tiup playground, Apple M1, binary MQ format, file sorter, log rotation configurations, Dumpling START TRANSACTION ... WITH CONSISTENT SNAPSHOT, SHOW CREATE TABLE
- Follow-up Guidance: The source also points to related user documents for CREATE INDEX, string functions, memory usage, system variables, choose-index, Lock View tables, TiFlash and TiKV configuration, and specific tool enhancements.
- Classification Note: This chunk is classified as a self-managed release-note summary because the official content enumerates TiDB 5.2 new features and enhancements for multiple components, including TiDB, TiKV, TiFlash, DM, TiCDC, Lightning, Dumpling, PD, and TiUP.

## Official Source Content

### SQL

- **Support using several functions in expression indexes**

    The expression index is a type of special index that can be created on an expression. After an expression index is created, TiDB supports expression-based queries, which greatly improves query performance.

    [User document](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index), [#25150](https://github.com/pingcap/tidb/issues/25150)

- **Support the `translate` function in Oracle**

    The `translate` function replaces all occurrences of characters by other characters in a string. In TiDB, this function does not treat empty strings as `NULL` as Oracle does.

    [User document](https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions)

- **Support spilling HashAgg**

    Support spilling HashAgg into disk. When a SQL statement that includes an HashAgg operator causes out of memory (OOM), you can try to set the concurrency of this operator to `1` to trigger disk spill, which alleviates memory stress.

    [User document](https://docs.pingcap.com/tidb/stable/configure-memory-usage#other-memory-control-behaviors-of-tidb-server), [#25882](https://github.com/pingcap/tidb/issues/25882)

- **Improve the accuracy of optimizer cardinality estimation**

    - Improve the accuracy of TiDB's estimation of TopN/Limit. For example, for pagination queries on a large table that contain the `order by col limit x` condition, TiDB can more easily select the right index and reduce query response time.
    - Improve the accuracy of out-of-range estimation. For example, even if the statistics for a day have not been updated, TiDB can accurately select the corresponding index for a query that contains `where date=Now()`.
    - Introduce the `tidb_opt_limit_push_down_threshold` variable to control the optimizer's behavior of pushing down Limit/TopN, which resolves the issue that Limit/TopN cannot be pushed down in some situations due to wrong estimation.

    [User document](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_limit_push_down_threshold), [#26085](https://github.com/pingcap/tidb/issues/26085)

- **Improve index selection of the optimizer**

    Add pruning rules for index selection. Before using the statistics for comparison, TiDB uses these rules to narrow down the scope of possible indexes to be selected, which reduces the possibility of selecting non-optimal indexes.

    [User document](https://docs.pingcap.com/tidb/stable/choose-index)
### Transaction

- **General availability (GA) for Lock View**

    The Lock View feature provides more information about lock conflicts and lock waits of pessimistic locks, which helps DBAs to observe transaction locking events and troubleshoot deadlock problems.

    In v5.2, the following enhancements are made to Lock View:

    - In addition to the SQL digest column in the Lock View-related tables, add a column to these tables that shows the corresponding normalized SQL text. You do not have to manually query the statement corresponding to a SQL digest.
    - Add the `TIDB_DECODE_SQL_DIGESTS` function to query the normalized SQL statements (a form without formats and arguments) corresponding to a set of SQL digests in the cluster. This simplifies the operation of querying the statements that have been historically executed by a transaction.
    - Add a column in the `DATA_LOCK_WAITS` and `DEADLOCKS` system tables to show the table name, row ID, index value, and other key information interpreted from a key. This simplifies the operations such as locating the table to which a key belongs and interpreting the key information.
    - Support collecting the information of retryable deadlock errors in the `DEADLOCKS` table, which makes it easier to troubleshoot issues caused by such errors. The error collection is disabled by default and can be enabled using the `pessimistic-txn.deadlock-history-collect-retryable` configuration.
    - Support distinguishing query-executing transactions from idle transactions on the `TIDB_TRX` system table. The `Normal` state is now divided into `Running` and `Idle` states.

   User documents:

    - View the pessimistic lock-waiting events that are occurring on all TiKV nodes in the cluster: [`DATA_LOCK_WAITS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-data-lock-waits)
    - View the deadlock errors recently occurred on a TiDB node: [`DEADLOCKS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-deadlocks)
    - View the executing transaction on a TiDB node: [`TIDB_TRX`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-trx)

- Optimize the user scenarios of adding indexes on tables with the `AUTO_RANDOM` or `SHARD_ROW_ID_BITS` attribute.
### Stability

- **Add TiFlash I/O traffic limit**

    This new feature is suitable for cloud storage with disk bandwidth of a small and specific size. It is disabled by default.

    TiFlash I/O Rate Limiter provides a new mechanism to avoid excessive race for I/O resources between read and write tasks. It balances the responses to read and write tasks, and limits the rate automatically according to read/write workload.

    [User document](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration)

- **Improve stability of TiKV flow control**

    TiKV introduces a new flow control mechanism to replace the previous RocksDB write stall mechanism. Compared with the write stall mechanism, this new mechanism reduces the impact on the stability of foreground write.

    In specific, when the stress of RocksDB compaction accumulates, flow control is performed at the TiKV scheduler layer instead of the RocksDB layer, to avoid the following issues:

    - Raftstore is stuck, which is caused by RocksDB write stall.
    - Raft election times out, and the node leader is transferred as a result.

    This new mechanism improves the flow control algorithm to mitigate QPS decrease when the write traffic is high.

    [User document](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#storageflow-control), [#10137](https://github.com/tikv/tikv/issues/10137)

- **Detect and recover automatically from impact caused by a single slow TiKV node in a cluster**

    TiKV introduces the slow node detection mechanism. This mechanism calculates a score by inspecting the rate of TiKV Raftstore, and then reports the score to PD through store heartbeats. Meanwhile, it adds the `evict-slow-store-scheduler` scheduler on PD to automatically evict the leader on a single slow TiKV node. In this way, the impact on the whole cluster is mitigated. At the same time, more alert items about slow nodes are introduced to help you quickly pinpoint and solve problems.

    [User document]( /tikv-configuration-file.md#inspect-interval), [#10539](https://github.com/tikv/tikv/issues/10539)
### Data Migration

- **Simplify operations of Data Migration (DM)**

    DM v2.0.6 can automatically identify the change event (failover or plan change) of the data source using VIP, and can automatically connect to a new data source instance, to reduce data replication latency and simplify operation procedures.

- TiDB Lightning supports customized line terminators in the CSV data, and is compatible with the MySQL LOAD DATA CSV data formats. You can then use TiDB Lightning directly in your data flow architecture.

    [#1297](https://github.com/pingcap/br/pull/1297)
### TiDB data share subscription

TiCDC supports using the HTTP protocol (OpenAPI) to manage TiCDC tasks, which is a more user-friendly operation method for both Kubernetes and self-hosted environments. (Experimental feature)

[#2411](https://github.com/pingcap/tiflow/issues/2411)
### Deployment and operations

Support running the `tiup playground` command on Mac computers with Apple M1 chips.
## Feature Enhancements

+ Tools

    + TiCDC

        - Add the binary MQ format designed for TiDB. It is more compact than the open protocols based on JSON [#1621](https://github.com/pingcap/tiflow/pull/1621)
        - Remove support for file sorter [#2114](https://github.com/pingcap/tiflow/pull/2114)
        - Support log rotation configurations [#2182](https://github.com/pingcap/tiflow/pull/2182)

    + TiDB Lightning

        - Support customized line terminators (except `\r` and `\n`) [#1297](https://github.com/pingcap/br/pull/1297)
        - Support expression index and the index that depends on virtual generated columns [#1407](https://github.com/pingcap/br/pull/1407)

    + Dumpling

        - Support backing up MySQL compatible databases but does not support `START TRANSACTION ... WITH CONSISTENT SNAPSHOT` or`SHOW CREATE TABLE` [#311](https://github.com/pingcap/dumpling/pull/311)
