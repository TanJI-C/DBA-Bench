# DB operations features: flashback, idle transactions, bindings, row size, BR restore

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.6.0.md`
- Source Title: `TiDB 7.6.0 Release Notes`
- Source Heading Path: `TiDB 7.6.0 Release Notes > Feature details > DB operations`
- Source Line Ranges: `171-214`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `br`, `ticdc`
- Topic Tags: `flashback cluster`, `tso`, `idle transactions`, `plan bindings`, `row size limit`, `system tables restore`, `backup restore`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0561_fee6bfdeec`
- Source ID: `tidb-docs-8.1:releases/release-7.6.0.md#db-operations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `282da6d020b75f471c08410c0c6c74702fdbe274f986f7929929cf74743ef7e8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.6.0#db-operations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when answering about TiDB v7.6.0 DB operations changes involving `FLASHBACK CLUSTER TO TSO`, `tidb_idle_transaction_timeout`, simplified `CREATE GLOBAL BINDING ... USING` syntax, `tidb_txn_entry_size_limit`, or BR restoring system tables by default with `--with-sys-table`.
- Retrieval Keywords: FLASHBACK CLUSTER TO TSO, TSO, tidb_idle_transaction_timeout, idle transactions, CREATE GLOBAL BINDING, USING, execution plan bindings, tidb_txn_entry_size_limit, txn-entry-size-limit, entry too large, BR, --with-sys-table, system tables, mysql schema, user data, table statistics
- Follow-up Guidance: The source includes example SQL for `FLASHBACK CLUSTER TO TSO` and `CREATE GLOBAL BINDING ... USING`, and links to the related documentation pages for each feature.
- Classification Note: This is a release-note DB operations section covering multiple operational features across flashback, transaction timeout, plan bindings, row size limits, and BR restore behavior.

## Official Source Content

### DB operations

* `FLASHBACK CLUSTER` supports specifying a precise TSO [#48372](https://github.com/pingcap/tidb/issues/48372) @[BornChanger](https://github.com/BornChanger/BornChanger)

    In TiDB v7.6.0, the flashback feature is more powerful and precise. It not only supports rolling back a cluster to a specified historical timestamp but also enables you to specify a precise recovery [TSO](https://docs.pingcap.com/tidb/stable/tso) using `FLASHBACK CLUSTER TO TSO`, thereby increasing flexibility in data recovery. For example, you can use this feature with TiCDC. After pausing data replication and conducting pre-online read-write tests in your downstream TiDB cluster, this feature allows the cluster to gracefully and quickly roll back to the paused TSO and continue to replicate data using TiCDC. This streamlines the pre-online validation process and simplifies data management.

    ```sql
    FLASHBACK CLUSTER TO TSO 445494839813079041;
    ````

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster).

* Support automatically terminating long-running idle transactions [#48714](https://github.com/pingcap/tidb/pull/48714) @[crazycs520](https://github.com/crazycs520)

    In scenarios where network disconnection or application failure occurs, `COMMIT`/`ROLLBACK` statements might fail to be transmitted to the database. This could lead to delayed release of database locks, causing transaction lock waits and a rapid increase in database connections. Such issues are common in test environments but can also occur occasionally in production environments, and they are sometimes difficult to diagnose promptly. To avoid these issues, TiDB v7.6.0 introduces the [`tidb_idle_transaction_timeout`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_idle_transaction_timeout-new-in-v760) system variable, which automatically terminates long-running idle transactions. When a user session in a transactional state remains idle for a duration exceeding the value of this variable, TiDB will terminate the database connection of the transaction and roll back it.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tidb_idle_transaction_timeout-new-in-v760).

* Simplify the syntax for creating execution plan bindings [#48876](https://github.com/pingcap/tidb/issues/48876) @[qw4990](https://github.com/qw4990)

    TiDB v7.6.0 simplifies the syntax for creating execution plan bindings. When creating an execution plan binding, you no longer need to provide the original SQL statement. TiDB identifies the original SQL statement based on the statement with hints. This improvement enhances the convenience of creating execution plan bindings. For example:

    ```sql
    CREATE GLOBAL BINDING
    USING
    SELECT /*+ merge_join(t1, t2) */ * FROM t1, t2 WHERE t1.id = t2.id;
    ```

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-plan-management#create-a-binding-according-to-a-sql-statement).

* Support dynamically modifying the size limit of a single row record in TiDB [#49237](https://github.com/pingcap/tidb/pull/49237) @[zyguan](https://github.com/zyguan)

    Before v7.6.0, the size of a single row record in a transaction is limited by the TiDB configuration item [`txn-entry-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-entry-size-limit-new-in-v4010-and-v500). If the size limit is exceeded, TiDB returns the `entry too large` error. In this case, you need to manually modify the TiDB configuration file and restart TiDB to make the modification take effect. To reduce your management overhead, TiDB v7.6.0 introduces the system variable [`tidb_txn_entry_size_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_txn_entry_size_limit-new-in-v760), which supports dynamically modifying the value of the `txn-entry-size-limit` configuration item. The default value of this variable is `0`, which means that TiDB uses the value of the configuration item `txn-entry-size-limit` by default. When this variable is set to a non-zero value, TiDB limits the size of a row record in transactions to the value of this variable. This improvement enhances the flexibility for you to adjust system configurations without restarting TiDB.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tidb_txn_entry_size_limit-new-in-v760).

* BR restores system tables by default, such as user data [#48567](https://github.com/pingcap/tidb/issues/48567) @[BornChanger](https://github.com/BornChanger) [#49627](https://github.com/pingcap/tidb/issues/49627) @[Leavrth](https://github.com/Leavrth)

    Starting from v5.1.0, when you back up snapshots, BR automatically backs up system tables in the `mysql` schema, but does not restore these system tables by default. In v6.2.0, BR adds the parameter `--with-sys-table` to support restoring data in some system tables, providing more flexibility in operations.

    To further reduce your management overhead and provide more intuitive default behavior, starting from v7.6.0, BR enables the parameter `--with-sys-table` by default. This means that BR restores some system tables by default during restoration, especially user account and table statistics data. This improvement makes backup and restore operations more intuitive, thereby reducing the burden of manual configuration and improving the overall operation experience.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide).
