# TiDB system variables for checksum, commit, constraints, cost model, and DDL reorg

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_checksum_table_concurrency | System Variables > Variable reference > tidb_committer_concurrency <span class="version-mark">New in v6.1.0</span> | System Variables > Variable reference > tidb_config | System Variables > Variable reference > tidb_constraint_check_in_place | System Variables > Variable reference > tidb_constraint_check_in_place_pessimistic <span class="version-mark">New in v6.3.0</span> | System Variables > Variable reference > tidb_cost_model_version <span class="version-mark">New in v6.2.0</span> | System Variables > Variable reference > tidb_current_ts | System Variables > Variable reference > tidb_ddl_disk_quota <span class="version-mark">New in v6.3.0</span> | System Variables > Variable reference > tidb_ddl_enable_fast_reorg <span class="version-mark">New in v6.3.0</span>`
- Source Line Ranges: `1418-1618`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `cloud`
- Topic Tags: `system-variables`, `checksum`, `commit`, `configuration`, `constraints`, `optimistic-transactions`, `pessimistic-transactions`, `cost-model`, `transaction-timestamp`, `ddl`, `index-creation`, `fast-reorg`, `disk-quota`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0717_22d56e7d01`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-checksum-table-concurrency`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `76e6c20e8ce58f5f54afa6f9827161d7ff74eb04db94a6ace8540af1a75b1413`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-checksum-table-concurrency
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables related to checksum concurrency, commit concurrency, server configuration visibility, optimistic or pessimistic unique constraint checking, cost model version, current transaction timestamp, and fast DDL reorganization for index creation.
- Retrieval Keywords: tidb_checksum_table_concurrency, ADMIN CHECKSUM TABLE, scan index concurrency, tidb_committer_concurrency, performance.committer-concurrency, commit phase of the single transaction, tidb_config, current TiDB server configuration, tidb_constraint_check_in_place, optimistic transactions, ERROR 1062, Duplicate entry, tidb_constraint_check_in_place_pessimistic, pessimistic transactions, LazyUniquenessCheckFailure, SAVEPOINT, Write conflict, tidb_cost_model_version, Cost Model Version 1, Cost Model Version 2, SET_VAR, tidb_current_ts, current transaction timestamp, tidb_ddl_disk_quota, tidb_ddl_enable_fast_reorg, ADD INDEX, CREATE INDEX, backfilling, ADMIN SHOW DDL JOBS, ingest, temp-dir
- Follow-up Guidance: The source also points to related references for Constraints, Cost Model, ADMIN SHOW DDL JOBS, SAVEPOINT, temp-dir, and the tidb_ddl_enable_fast_reorg dependency of tidb_ddl_disk_quota.
- Classification Note: This is reference content because it enumerates TiDB system variables with their scope, type, default values, ranges, notes, and behavior for checksum, commit, constraints, cost model, transaction timestamp, and DDL reorganization.

## Official Source Content

### tidb_checksum_table_concurrency

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `4`
- Range: `[1, 256]`
- Unit: Threads
- This variable is used to set the scan index concurrency of executing the [`ADMIN CHECKSUM TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-checksum-table) statement.
- When the variable is set to a larger value, the execution performance of other queries is affected.
### tidb_committer_concurrency New in v6.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `128`
- Range: `[1, 10000]`
- The number of goroutines for requests related to executing commit in the commit phase of the single transaction.
- If the transaction to commit is too large, the waiting time for the flow control queue when the transaction is committed might be too long. In this situation, you can increase the configuration value to speed up the commit.
- This setting was previously a `tidb.toml` option (`performance.committer-concurrency`), but changed to a system variable starting from TiDB v6.1.0.
### tidb_config

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: ""
- This variable is read-only. It is used to obtain the configuration information of the current TiDB server.
### tidb_constraint_check_in_place

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable only applies to optimistic transactions. For pessimistic transactions, use [`tidb_constraint_check_in_place_pessimistic`](#tidb_constraint_check_in_place_pessimistic-new-in-v630) instead.
- When this variable is set to `OFF`, checking for duplicate values in unique indexes is deferred until the transaction commits. This helps improve performance but might be an unexpected behavior for some applications. See [Constraints](https://docs.pingcap.com/tidb/stable/constraints#optimistic-transactions) for details.

    - When setting `tidb_constraint_check_in_place` to `OFF` and using optimistic transactions:

        ```sql
        tidb> create table t (i int key);
        tidb> insert into t values (1);
        tidb> begin optimistic;
        tidb> insert into t values (1);
        Query OK, 1 row affected
        tidb> commit; -- Check only when a transaction is committed.
        ERROR 1062 : Duplicate entry '1' for key 't.PRIMARY'
        ```

    - When setting `tidb_constraint_check_in_place` to `ON` and using optimistic transactions:

        ```sql
        tidb> set @@tidb_constraint_check_in_place=ON;
        tidb> begin optimistic;
        tidb> insert into t values (1);
        ERROR 1062 : Duplicate entry '1' for key 't.PRIMARY'
        ```
### tidb_constraint_check_in_place_pessimistic New in v6.3.0

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean

- Default value: By default, the [`pessimistic-txn.constraint-check-in-place-pessimistic`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#constraint-check-in-place-pessimistic-new-in-v640) configuration item is `true` so the default value of this variable is `ON`. When [`pessimistic-txn.constraint-check-in-place-pessimistic`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#constraint-check-in-place-pessimistic-new-in-v640) is set to `false`, the default value of this variable is `OFF`.

- Default value: `ON`

- This variable only applies to pessimistic transactions. For optimistic transactions, use [`tidb_constraint_check_in_place`](#tidb_constraint_check_in_place) instead.
- When this variable is set to `OFF`, TiDB defers the unique constraint check of a unique index (to the next time when executing a statement that requires a lock to the index or to the time when committing the transaction). This helps improve performance but might be an unexpected behavior for some applications. See [Constraints](https://docs.pingcap.com/tidb/stable/constraints#pessimistic-transactions) for details.
- Disabling this variable might cause TiDB to return a `LazyUniquenessCheckFailure` error in pessimistic transactions. When this error occurs, TiDB rolls back the current transaction.
- When this variable is disabled, you cannot use [`SAVEPOINT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-savepoint) in pessimistic transactions.
- When this variable is disabled, committing a pessimistic transaction might return a `Write conflict` or `Duplicate entry` error. When such an error occurs, TiDB rolls back the current transaction.

    - When setting `tidb_constraint_check_in_place_pessimistic` to `OFF` and using pessimistic transactions:

        ```sql
        set @@tidb_constraint_check_in_place_pessimistic=OFF;
        create table t (i int key);
        insert into t values (1);
        begin pessimistic;
        insert into t values (1);
        ```

        ```
        Query OK, 1 row affected
        ```

        ```sql
        tidb> commit; -- Check only when a transaction is committed.
        ```

        ```
        ERROR 1062 : Duplicate entry '1' for key 't.PRIMARY'
        ```

    - When setting `tidb_constraint_check_in_place_pessimistic` to `ON` and using pessimistic transactions:

        ```sql
        set @@tidb_constraint_check_in_place_pessimistic=ON;
        begin pessimistic;
        insert into t values (1);
        ```

        ```
        ERROR 1062 : Duplicate entry '1' for key 't.PRIMARY'
        ```
### tidb_cost_model_version New in v6.2.0

> **Note:**
>
> - Since TiDB v6.5.0, the newly created cluster uses Cost Model Version 2 by default. If you upgrade from a TiDB version earlier than v6.5.0 to v6.5.0 or later, the `tidb_cost_model_version` value does not change.
> - Switching the version of the cost model might cause changes to query plans.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `2`
- Value options:
    - `1`: enables the Cost Model Version 1, which is used by default in TiDB v6.4.0 and earlier versions.
    - `2`: enables the [Cost Model Version 2](https://docs.pingcap.com/tidb/stable/cost-model#cost-model-version-2), which is generally available in TiDB v6.5.0 and is more accurate than the version 1 in internal tests.
- The version of cost model affects the plan decision of optimizer. For more details, see [Cost Model](https://docs.pingcap.com/tidb/stable/cost-model).
### tidb_current_ts

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 9223372036854775807]`
- This variable is read-only. It is used to obtain the timestamp of the current transaction.
### tidb_ddl_disk_quota New in v6.3.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `107374182400` (100 GiB)
- Range: `[107374182400, 1125899906842624]` ([100 GiB, 1 PiB])
- Unit: Bytes
- This variable only takes effect when [`tidb_ddl_enable_fast_reorg`](#tidb_ddl_enable_fast_reorg-new-in-v630) is enabled. It sets the usage limit of local storage during backfilling when creating an index.
### tidb_ddl_enable_fast_reorg New in v6.3.0

> **Note:**
>
> - If you are using a [TiDB Cloud Dedicated](https://docs.pingcap.com/tidbcloud/select-cluster-tier#tidb-cloud-dedicated) cluster, to improve the speed for index creation using this variable, make sure that your TiDB cluster is hosted on AWS and your TiDB node size is at least 8 vCPU.
> - For [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters, this variable is read-only.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether to enable the acceleration of `ADD INDEX` and `CREATE INDEX` to improve the speed of backfilling for index creation. Setting this variable value to `ON` can bring performance improvement for index creation on tables with a large amount of data.
- Starting from v7.1.0, the index acceleration operation supports checkpoints. Even if the TiDB owner node is restarted or changed due to failures, TiDB can still recover progress from checkpoints that are automatically updated on a regular basis.
- To verify whether a completed `ADD INDEX` operation is accelerated, you can execute the [`ADMIN SHOW DDL JOBS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl#admin-show-ddl-jobs) statement to see whether `ingest` is displayed in the `JOB_TYPE` column.

> **Note:**
>
> * Index acceleration requires a [`temp-dir`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#temp-dir-new-in-v630) that is writable and has enough free space. If the `temp-dir` is unusable, TiDB falls back to non-accelerated index building. It is recommended to put the `temp-dir` on a SSD disk.
>
> * Before you upgrade TiDB to v6.5.0 or later, it is recommended that you check whether the [`temp-dir`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#temp-dir-new-in-v630) path of TiDB is correctly mounted to an SSD disk. Make sure that the operating system user that runs TiDB has the read and write permissions for this directory. Otherwise, The DDL operations might experience unpredictable issues. This path is a TiDB configuration item, which takes effect after TiDB is restarted. Therefore, setting this configuration item before upgrading can avoid another restart.

> **Warning:**
>
> Currently, this feature is not fully compatible with [altering multiple columns or indexes in a single `ALTER TABLE` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table). When adding a unique index with the index acceleration, you need to avoid altering other columns or indexes in the same statement.
