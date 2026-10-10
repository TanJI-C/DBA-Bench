# statement summary system variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_stmt_summary_enable_persistent <span class="version-mark">New in v6.6.0</span> | System Variables > Variable reference > tidb_stmt_summary_filename <span class="version-mark">New in v6.6.0</span> | System Variables > Variable reference > tidb_stmt_summary_file_max_backups <span class="version-mark">New in v6.6.0</span> | System Variables > Variable reference > tidb_stmt_summary_file_max_days <span class="version-mark">New in v6.6.0</span> | System Variables > Variable reference > tidb_stmt_summary_file_max_size <span class="version-mark">New in v6.6.0</span> | System Variables > Variable reference > tidb_stmt_summary_history_size <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > tidb_stmt_summary_internal_query <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > tidb_stmt_summary_max_sql_length <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > tidb_stmt_summary_max_stmt_count <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > tidb_stmt_summary_refresh_interval <span class="version-mark">New in v4.0</span>`
- Source Line Ranges: `5386-5607`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `dashboard`, `sql`, `cloud`
- Topic Tags: `statement-summary`, `persistence`, `experimental`, `sql-digests`, `history`, `refresh-interval`, `sql-length`, `internal-queries`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0743_fee9021293`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-stmt-summary-enable-persistent-span-class-version-mark-new-in-v6-6-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2470c64879bfe16718f09206b5be919f7a185c31e294a68f433d62e3f2e61ecd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-stmt-summary-enable-persistent-span-class-version-mark-new-in-v6-6-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when identifying statement summary system variables for persistence, history capacity, internal queries, SQL length, statement count, or refresh interval.
- Retrieval Keywords: tidb_stmt_summary_enable_persistent, tidb_stmt_summary_filename, tidb_stmt_summary_file_max_backups, tidb_stmt_summary_file_max_days, tidb_stmt_summary_file_max_size, tidb_stmt_summary_history_size, tidb_stmt_summary_internal_query, tidb_stmt_summary_max_sql_length, tidb_stmt_summary_max_stmt_count, tidb_stmt_summary_refresh_interval, statement summary tables, statements_summary, statements_summary_history, statements summary persistence, TiDB Dashboard, SQL digests
- Follow-up Guidance: The content refers to statement summary tables, persist statements summary, TiDB Dashboard, and matching tidb configuration file items for additional details.
- Classification Note: This is reference content because it enumerates multiple statement summary system variables with their scope, defaults, limits, read-only status, and what each variable controls.

## Official Source Content

### tidb_stmt_summary_enable_persistent New in v6.6.0

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

> **Warning:**
>
> Statements summary persistence is an experimental feature. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

- Scope: GLOBAL
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is read-only. It controls whether to enable [statements summary persistence](https://docs.pingcap.com/tidb/stable/statement-summary-tables#persist-statements-summary).

- The value of this variable is the same as that of the configuration item [`tidb_stmt_summary_enable_persistent`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_stmt_summary_enable_persistent-new-in-v660).
### tidb_stmt_summary_filename New in v6.6.0

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

> **Warning:**
>
> Statements summary persistence is an experimental feature. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

- Scope: GLOBAL
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: String
- Default value: `"tidb-statements.log"`
- This variable is read-only. It specifies the file to which persistent data is written when [statements summary persistence](https://docs.pingcap.com/tidb/stable/statement-summary-tables#persist-statements-summary) is enabled.

- The value of this variable is the same as that of the configuration item [`tidb_stmt_summary_filename`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_stmt_summary_filename-new-in-v660).
### tidb_stmt_summary_file_max_backups New in v6.6.0

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

> **Warning:**
>
> Statements summary persistence is an experimental feature. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

- Scope: GLOBAL
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- This variable is read-only. It specifies the maximum number of data files that can be persisted when [statements summary persistence](https://docs.pingcap.com/tidb/stable/statement-summary-tables#persist-statements-summary) is enabled.

- The value of this variable is the same as that of the configuration item [`tidb_stmt_summary_file_max_backups`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_stmt_summary_file_max_backups-new-in-v660).
### tidb_stmt_summary_file_max_days New in v6.6.0

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

> **Warning:**
>
> Statements summary persistence is an experimental feature. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

- Scope: GLOBAL
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `3`
- Unit: day
- This variable is read-only. It specifies the maximum number of days to keep persistent data files when [statements summary persistence](https://docs.pingcap.com/tidb/stable/statement-summary-tables#persist-statements-summary) is enabled.

- The value of this variable is the same as that of the configuration item [`tidb_stmt_summary_file_max_days`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_stmt_summary_file_max_days-new-in-v660).
### tidb_stmt_summary_file_max_size New in v6.6.0

> **Note:**
>
> This TiDB variable is not applicable to TiDB Cloud.

> **Warning:**
>
> Statements summary persistence is an experimental feature. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

- Scope: GLOBAL
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `64`
- Unit: MiB
- This variable is read-only. It specifies the maximum size of a persistent data file when [statements summary persistence](https://docs.pingcap.com/tidb/stable/statement-summary-tables#persist-statements-summary) is enabled.

- The value of this variable is the same as that of the configuration item [`tidb_stmt_summary_file_max_size`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_stmt_summary_file_max_size-new-in-v660).
### tidb_stmt_summary_history_size New in v4.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `24`
- Range: `[0, 255]`
- This variable is used to set the history capacity of [statement summary tables](https://docs.pingcap.com/tidb/stable/statement-summary-tables).
### tidb_stmt_summary_internal_query New in v4.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to control whether to include the SQL information of TiDB in [statement summary tables](https://docs.pingcap.com/tidb/stable/statement-summary-tables).
### tidb_stmt_summary_max_sql_length New in v4.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `4096`
- Range: `[0, 2147483647]`
- Unit: Bytes

- This variable is used to control the length of the SQL string in [statement summary tables](https://docs.pingcap.com/tidb/stable/statement-summary-tables) and the [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro).

- This variable is used to control the length of the SQL string in [statement summary tables](https://docs.pingcap.com/tidb/stable/statement-summary-tables).
### tidb_stmt_summary_max_stmt_count New in v4.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `3000`
- Range: `[1, 32767]`
- This variable is used to limit the number of SQL digests that the [`statements_summary`](https://docs.pingcap.com/tidb/stable/statement-summary-tables#statements_summary) and [`statements_summary_history`](https://docs.pingcap.com/tidb/stable/statement-summary-tables#statements_summary_history) tables can store in memory totally.

> **Note:**
>
> When [`tidb_stmt_summary_enable_persistent`](https://docs.pingcap.com/tidb/stable/statement-summary-tables#persist-statements-summary) is enabled, `tidb_stmt_summary_max_stmt_count` only limits the number of SQL digests that the [`statements_summary`](https://docs.pingcap.com/tidb/stable/statement-summary-tables#statements_summary) table can store in memory.
### tidb_stmt_summary_refresh_interval New in v4.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `1800`
- Range: `[1, 2147483647]`
- Unit: Seconds
- This variable is used to set the refresh time of [statement summary tables](https://docs.pingcap.com/tidb/stable/statement-summary-tables).
