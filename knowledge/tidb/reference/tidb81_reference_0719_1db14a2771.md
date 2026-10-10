# TiDB enable-related system variables: analyze, commit, DDL, planner, and security

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_enable_analyze_snapshot <span class="version-mark">New in v6.2.0</span> | System Variables > Variable reference > tidb_enable_async_commit <span class="version-mark">New in v5.0</span> | System Variables > Variable reference > tidb_enable_auto_analyze <span class="version-mark">New in v6.1.0</span> | System Variables > Variable reference > tidb_enable_auto_analyze_priority_queue <span class="version-mark">New in v8.0.0</span> | System Variables > Variable reference > tidb_enable_auto_increment_in_generated | System Variables > Variable reference > tidb_enable_batch_dml | System Variables > Variable reference > tidb_enable_cascades_planner | System Variables > Variable reference > tidb_enable_check_constraint <span class="version-mark">New in v7.2.0</span> | System Variables > Variable reference > tidb_enable_chunk_rpc <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > tidb_enable_clustered_index <span class="version-mark">New in v5.0</span> | System Variables > Variable reference > tidb_enable_ddl <span class="version-mark">New in v6.3.0</span> | System Variables > Variable reference > tidb_enable_collect_execution_info | System Variables > Variable reference > tidb_enable_column_tracking <span class="version-mark">New in v5.4.0</span> | System Variables > Variable reference > tidb_enable_enhanced_security`
- Source Line Ranges: `1862-2047`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`, `cloud`
- Topic Tags: `system-variables`, `statistics`, `analyze`, `async-commit`, `auto-analyze`, `ddl`, `planner`, `clustered-index`, `slow-log`, `security`, `sem`, `check-constraint`, `batch-dml`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0719_1db14a2771`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-enable-analyze-snapshot-span-class-version-mark-new-in-v6-2-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `47e30643302a30c13d0bca1c0451b8b159966867951d1eb4070390986d5628e9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-enable-analyze-snapshot-span-class-version-mark-new-in-v6-2-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB enable-related system variables for ANALYZE behavior, async commit, auto analyze, batch DML, cascades planner, CHECK constraint, Chunk RPC, clustered index defaults, DDL owner eligibility, execution info collection, column tracking, or Security Enhanced Mode.
- Retrieval Keywords: tidb_enable_analyze_snapshot, ANALYZE reads historical data, ANALYZE reads latest data, GC life time is shorter than transaction duration, tidb_enable_async_commit, async commit, two-phase transaction commit, TiDB Binlog, TiCDC, tidb_enable_auto_analyze, performance.run-auto-analyze, tidb_enable_auto_analyze_priority_queue, automatically collecting statistics priority queue, newly created indexes, partitioned tables with partition changes, health scores, tidb_enable_auto_increment_in_generated, AUTO_INCREMENT columns, generated column, expression index, tidb_enable_batch_dml, deprecated batch-dml, non-transactional DML, tidb_batch_dml_size, tidb_batch_insert, tidb_batch_delete, tidb_enable_cascades_planner, cascades planner, tidb_enable_check_constraint, CHECK constraint, tidb_enable_chunk_rpc, Chunk data encoding format in Coprocessor, tidb_enable_clustered_index, CLUSTERED, NONCLUSTERED, INT_ONLY, alter-primary-key, clustered index, tidb_enable_ddl, DDL owner, tidb_enable_collect_execution_info, slow query log, usage statistics of indexes, information_schema.tidb_index_usage, tidb_enable_column_tracking, PREDICATE COLUMNS, Collect statistics on some columns, tidb_enable_enhanced_security, Security Enhanced Mode, enable-sem, RESTRICTED_TABLES_ADMIN, RESTRICTED_STATUS_ADMIN, RESTRICTED_VARIABLES_ADMIN, RESTRICTED_USER_ADMIN
- Follow-up Guidance: The chunk also states scope, whether the variable persists to the cluster, whether it applies to the SET_VAR hint, default values, and warnings or notes for these variables.
- Classification Note: This is reference content because it enumerates system variables and their exact scopes, defaults, possible values, persistence behavior, and feature descriptions.

## Official Source Content

### tidb_enable_analyze_snapshot New in v6.2.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable controls whether to read historical data or the latest data when performing `ANALYZE`. If this variable is set to `ON`, `ANALYZE` reads the historical data available at the time of `ANALYZE`. If this variable is set to `OFF`, `ANALYZE` reads the latest data.
- Before v5.2, `ANALYZE` reads the latest data. From v5.2 to v6.1, `ANALYZE` reads the historical data available at the time of `ANALYZE`.

> **Warning:**
>
> If `ANALYZE` reads the historical data available at the time of `ANALYZE`, the long duration of `AUTO ANALYZE` might cause the `GC life time is shorter than transaction duration` error because the historical data is garbage-collected.
### tidb_enable_async_commit New in v5.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether to enable the async commit feature for the second phase of the two-phase transaction commit to perform asynchronously in the background. Enabling this feature can reduce the latency of transaction commit.

> **Note:**
>
> - The default value of `ON` only applies to new clusters. if your cluster was upgraded from an earlier version of TiDB, the value `OFF` will be used instead.
> - If you have enabled TiDB Binlog, enabling this variable cannot improve the performance. To improve the performance, it is recommended to use [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc-overview) instead.
> - Enabling this parameter only means that Async Commit becomes an optional mode of transaction commit. In fact, the most suitable mode of transaction commit is determined by TiDB.
### tidb_enable_auto_analyze New in v6.1.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- Determines whether TiDB automatically updates table statistics as a background operation.
- This setting was previously a `tidb.toml` option (`performance.run-auto-analyze`), but changed to a system variable starting from TiDB v6.1.0.
### tidb_enable_auto_analyze_priority_queue New in v8.0.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is used to control whether to enable the priority queue to schedule the tasks of automatically collecting statistics. When this variable is enabled, TiDB prioritizes collecting statistics for tables that are more valuable to collect, such as newly created indexes and partitioned tables with partition changes. Additionally, TiDB prioritizes tables with lower health scores, placing them at the front of the queue.
### tidb_enable_auto_increment_in_generated

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to determine whether to include the `AUTO_INCREMENT` columns when creating a generated column or an expression index.
### tidb_enable_batch_dml

> **Warning:**
>
> This variable is associated with the deprecated batch-dml feature, which might cause data corruption. Therefore, it is not recommended to enable this variable for batch-dml. Instead, use [non-transactional DML](https://docs.pingcap.com/tidb/stable/non-transactional-dml).

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable controls whether to enable the deprecated batch-dml feature. When it is enabled, certain statements might be split into multiple transactions, which is non-atomic and should be used with care. When using batch-dml, you must ensure that there are no concurrent operations on the data you are operating on. To make it work, you must also specify a positive value for `tidb_batch_dml_size` and enable at least one of `tidb_batch_insert` and `tidb_batch_delete`.
### tidb_enable_cascades_planner

> **Warning:**
>
> Currently, cascades planner is an experimental feature. It is not recommended that you use it in production environments.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Boolean
- Default value: `OFF`
- This variable is used to control whether to enable the cascades planner.
### tidb_enable_check_constraint New in v7.2.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to control whether to enable the [`CHECK` constraint](https://docs.pingcap.com/tidb/stable/constraints#check) feature.
### tidb_enable_chunk_rpc New in v4.0

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is used to control whether to enable the `Chunk` data encoding format in Coprocessor.
### tidb_enable_clustered_index New in v5.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Enumeration
- Default value: `ON`
- Possible values: `OFF`, `ON`, `INT_ONLY`
- This variable is used to control whether to create the primary key as a [clustered index](https://docs.pingcap.com/tidb/stable/clustered-indexes) by default. "By default" here means that the statement does not explicitly specify the keyword `CLUSTERED`/`NONCLUSTERED`. Supported values are `OFF`, `ON`, and `INT_ONLY`:
    - `OFF` indicates that primary keys are created as non-clustered indexes by default.
    - `ON` indicates that primary keys are created as clustered indexes by default.
    - `INT_ONLY` indicates that the behavior is controlled by the configuration item `alter-primary-key`. If `alter-primary-key` is set to `true`, all primary keys are created as non-clustered indexes by default. If it is set to `false`, only the primary keys which consist of an integer column are created as clustered indexes.
### tidb_enable_ddl New in v6.3.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `ON`
- Possible values: `OFF`, `ON`
- This variable controls whether the corresponding TiDB instance can become a DDL owner or not. If there is only one TiDB instance in the current TiDB cluster, you cannot prevent it from becoming a DDL owner, which means you cannot set it to `OFF`.
### tidb_enable_collect_execution_info

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable controls whether to record the execution information of each operator in the slow query log and whether to record the [usage statistics of indexes](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-index-usage).
### tidb_enable_column_tracking New in v5.4.0

> **Warning:**
>
> Currently, collecting statistics on `PREDICATE COLUMNS` is an experimental feature. It is not recommended that you use it in production environments.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable controls whether to enable TiDB to collect `PREDICATE COLUMNS`. After enabling the collection, if you disable it, the information of previously collected `PREDICATE COLUMNS` is cleared. For details, see [Collect statistics on some columns](https://docs.pingcap.com/tidb/stable/statistics#collect-statistics-on-some-columns).
### tidb_enable_enhanced_security

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean

- Default value: `OFF`
- This variable indicates whether the TiDB server you are connected to has the Security Enhanced Mode (SEM) enabled. To change its value, you need to modify the value of `enable-sem` in your TiDB server configuration file and restart the TiDB server.

- Default value: `ON`
- This variable is read-only. For TiDB Cloud, the Security Enhanced Mode (SEM) is enabled by default.

- SEM is inspired by the design of systems such as [Security-Enhanced Linux](https://en.wikipedia.org/wiki/Security-Enhanced_Linux). It reduces the abilities of users with the MySQL `SUPER` privilege and instead requires `RESTRICTED` fine-grained privileges to be granted as a replacement. These fine-grained privileges include:
    - `RESTRICTED_TABLES_ADMIN`: The ability to write data to system tables in the `mysql` schema and to see sensitive columns on `information_schema` tables.
    - `RESTRICTED_STATUS_ADMIN`: The ability to see sensitive variables in the command `SHOW STATUS`.
    - `RESTRICTED_VARIABLES_ADMIN`: The ability to see and set sensitive variables in `SHOW [GLOBAL] VARIABLES` and `SET`.
    - `RESTRICTED_USER_ADMIN`: The ability to prevent other users from making changes or dropping a user account.
