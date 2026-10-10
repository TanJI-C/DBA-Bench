# General TiDB server configuration options

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-configuration-file.md`
- Source Title: `TiDB Configuration File`
- Source Heading Path: `TiDB Configuration File | TiDB Configuration File > `split-table` | TiDB Configuration File > `tidb-max-reuse-chunk` <span class="version-mark">New in v6.4.0</span> | TiDB Configuration File > `tidb-max-reuse-column` <span class="version-mark">New in v6.4.0</span> | TiDB Configuration File > `token-limit` | TiDB Configuration File > `temp-dir` <span class="version-mark">New in v6.3.0</span> | TiDB Configuration File > `oom-use-tmp-storage` | TiDB Configuration File > `tmp-storage-path` | TiDB Configuration File > `tmp-storage-quota` | TiDB Configuration File > `lease` | TiDB Configuration File > `compatible-kill-query` | TiDB Configuration File > `check-mb4-value-in-utf8` | TiDB Configuration File > `treat-old-version-utf8-as-utf8mb4` | TiDB Configuration File > `alter-primary-key` (Deprecated) | TiDB Configuration File > `server-version``
- Source Line Ranges: `5-129`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`, `tikv`
- Topic Tags: `config-file`, `server-settings`, `memory`, `temporary-storage`, `ddl`, `kill-query`, `charset`, `collation`, `primary-key`, `version-compatibility`, `connections`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0315_c7e19b4e87`
- Source ID: `tidb-docs-8.1:tidb-configuration-file.md#tidb-configuration-file`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3f0c66310aaa6b2abe3b8031fc1a669a13ce57c0c24989dd82ea04f765d1a36f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb-configuration-file
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiDB configuration file details for server settings such as `split-table`, chunk or column reuse limits, temporary storage, DDL lease, `KILL` compatibility, UTF-8 handling, deprecated primary key alteration, or `server-version` behavior.
- Retrieval Keywords: split-table, tidb-max-reuse-chunk, tidb-max-reuse-column, token-limit, temp-dir, oom-use-tmp-storage, tidb_enable_tmp_storage_on_oom, tmp-storage-path, tmp-storage-quota, Out of Global Storage Quota!, lease, compatible-kill-query, enable-global-kill, KILL TIDB xxx, check-mb4-value-in-utf8, tidb_check_mb4_value_in_utf8, treat-old-version-utf8-as-utf8mb4, alter-primary-key, @tidb_enable_clustered_index, INT_ONLY, NONCLUSTERED, server-version, VERSION(), tidb_ddl_enable_fast_reorg, IMPORT INTO, tidb_mem_quota_query
- Follow-up Guidance: The source also points to related references for modifying configuration, `KILL [TIDB]`, `IMPORT INTO`, `tidb_ddl_enable_fast_reorg`, and system variables such as `tidb_enable_tmp_storage_on_oom` and `tidb_mem_quota_query`.
- Classification Note: This is classified as TiDB self-managed configuration because the content enumerates `config.toml` server options and their effects, defaults, limits, deprecations, and interactions with TiDB system variables.

## Official Source Content

# TiDB Configuration File

The TiDB configuration file supports more options than command-line parameters. You can download the default configuration file [`config.toml.example`](https://github.com/pingcap/tidb/blob/release-8.1/pkg/config/config.toml.example) and rename it to `config.toml`. This document describes only the options that are not involved in [command line options](https://docs.pingcap.com/tidb/stable/command-line-flags-for-tidb-configuration).

> **Tip:**
>
> If you need to adjust the value of a configuration item, refer to [Modify the configuration](https://docs.pingcap.com/tidb/stable/maintain-tidb-using-tiup#modify-the-configuration).
### `split-table`

- Determines whether to create a separate Region for each table.
- Default value: `true`
- It is recommended to set it to `false` if you need to create a large number of tables (for example, more than 100 thousand tables).
### `tidb-max-reuse-chunk` New in v6.4.0

- Controls the maximum cached chunk objects of chunk allocation. Setting this configuration item to too large a value might increase the risk of OOM.
- Default value: `64`
- Minimum value: `0`
- Maximum value: `2147483647`
### `tidb-max-reuse-column` New in v6.4.0

- Controls the maximum cached column objects of chunk allocation. Setting this configuration item to too large a value might increase the risk of OOM.
- Default value: `256`
- Minimum value: `0`
- Maximum value: `2147483647`
### `token-limit`

+ The number of sessions that can execute requests concurrently.
+ Type: Integer
+ Default value: `1000`
+ Minimum value: `1`
+ Maximum Value (64-bit platforms): `18446744073709551615`
+ Maximum Value (32-bit platforms): `4294967295`
### `temp-dir` New in v6.3.0

+ File system location used by TiDB to store temporary data. If a feature requires local storage in TiDB nodes, TiDB stores the corresponding temporary data in this location.
+ When creating an index, if [`tidb_ddl_enable_fast_reorg`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630) is enabled, data that needs to be backfilled for a newly created index will be at first stored in the TiDB local temporary directory, and then imported into TiKV in batches, thus accelerating the index creation.
+ When [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into) is used to import data, the sorted data is first stored in the TiDB local temporary directory, and then imported into TiKV in batches.
+ Default value: `"/tmp/tidb"`

> **Note:**
>
> If the directory does not exist, TiDB will automatically create it upon startup. If the directory creation fails or TiDB does not have the read and write permissions on that directory, [`Fast Online DDL`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ddl_enable_fast_reorg-new-in-v630) might experience unpredictable issues.
### `oom-use-tmp-storage`

> **Warning:**
>
> Since v6.3.0, this configuration item is deprecated and superseded by the system variable [`tidb_enable_tmp_storage_on_oom`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_tmp_storage_on_oom). When the TiDB cluster is upgraded to v6.3.0 or a later version, it will automatically initialize the variable with the value of `oom-use-tmp-storage`. After that, changing the value of `oom-use-tmp-storage` **does not** take effect anymore.

+ Controls whether to enable the temporary storage for some operators when a single SQL statement exceeds the memory quota specified by the system variable [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query).
+ Default value: `true`
### `tmp-storage-path`

+ Specifies the temporary storage path for some operators when a single SQL statement exceeds the memory quota specified by the system variable [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query).
+ Default value: `<temporary directory of OS>/<OS user ID>_tidb/MC4wLjAuMDo0MDAwLzAuMC4wLjA6MTAwODA=/tmp-storage`. `MC4wLjAuMDo0MDAwLzAuMC4wLjA6MTAwODA=` is the `Base64` encoding result of `<host>:<port>/<statusHost>:<statusPort>`.
+ This configuration takes effect only when the system variable [`tidb_enable_tmp_storage_on_oom`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_tmp_storage_on_oom) is `ON`.
### `tmp-storage-quota`

+ Specifies the quota for the storage in `tmp-storage-path`. The unit is byte.
+ When a single SQL statement uses a temporary disk and the total volume of the temporary disk of the TiDB server exceeds this configuration value, the current SQL operation is cancelled and the `Out of Global Storage Quota!` error is returned.
+ When the value of this configuration is smaller than `0`, the above check and limit do not apply.
+ Default value: `-1`
+ When the remaining available storage in `tmp-storage-path` is lower than the value defined by `tmp-storage-quota`, the TiDB server reports an error when it is started, and exits.
### `lease`

+ The timeout of the DDL lease.
+ Default value: `45s`
+ Unit: second
### `compatible-kill-query`

+ Determines whether to set the `KILL` statement to be MySQL compatible.
+ Default value: `false`
+ `compatible-kill-query` takes effect only when [`enable-global-kill`](#enable-global-kill-new-in-v610) is set to `false`.
+ When [`enable-global-kill`](#enable-global-kill-new-in-v610) is `false`, `compatible-kill-query` controls whether you need to append the `TIDB` keyword when killing a query.
    - When `compatible-kill-query` is `false`, the behavior of `KILL xxx` in TiDB is different from that in MySQL. To kill a query in TiDB, you need to append the `TIDB` keyword, such as `KILL TIDB xxx`.
    - When `compatible-kill-query` is `true`, to kill a query in TiDB, there is no need to append the `TIDB` keyword. It is **STRONGLY NOT RECOMMENDED** to set `compatible-kill-query` to `true` in your configuration file UNLESS you are certain that clients will be always connected to the same TiDB instance. This is because pressing <kbd>Control</kbd>+<kbd>C</kbd> in the default MySQL client opens a new connection in which `KILL` is executed. If there is a proxy between the client and the TiDB cluster, the new connection might be routed to a different TiDB instance, which possibly kills a different session by mistake.
+ When [`enable-global-kill`](#enable-global-kill-new-in-v610) is `true`, `KILL xxx` and `KILL TIDB xxx` have the same effect.
+ For more information about the `KILL` statement, see [KILL [TIDB]](/sql-statements/sql-statement-kill.md).
### `check-mb4-value-in-utf8`

- Determines whether to enable the `utf8mb4` character check. When this feature is enabled, if the character set is `utf8` and the `mb4` characters are inserted in `utf8`, an error is returned.
- Default value: `false`
- Since v6.1.0, whether to enable the `utf8mb4` character check is determined by the TiDB configuration item `instance.tidb_check_mb4_value_in_utf8` or the system variable `tidb_check_mb4_value_in_utf8`. `check-mb4-value-in-utf8` still takes effect. But if both `check-mb4-value-in-utf8` and `instance.tidb_check_mb4_value_in_utf8` are set, the latter takes effect.
### `treat-old-version-utf8-as-utf8mb4`

- Determines whether to treat the `utf8` character set in old tables as `utf8mb4`.
- Default value: `true`
### `alter-primary-key` (Deprecated)

- Determines whether to add or remove the primary key constraint to or from a column.
- Default value: `false`
- With this default setting, adding or removing the primary key constraint is not supported. You can enable this feature by setting `alter-primary-key` to `true`. However, if a table already exists before the switch is on, and the data type of its primary key column is an integer, dropping the primary key from the column is not possible even if you set this configuration item to `true`.

> **Note:**
>
> This configuration item has been deprecated, and currently takes effect only when the value of `@tidb_enable_clustered_index` is `INT_ONLY`. If you need to add or remove the primary key, use the `NONCLUSTERED` keyword instead when creating the table. For more details about the primary key of the `CLUSTERED` type, refer to [clustered index](https://docs.pingcap.com/tidb/stable/clustered-indexes).
### `server-version`

+ Modifies the version string returned by TiDB in the following situations:
    - When the built-in `VERSION()` function is used.
    - When TiDB establishes the initial connection to the client and returns the initial handshake packet with version string of the server. For details, see [MySQL Initial Handshake Packet](https://dev.mysql.com/doc/dev/mysql-server/latest/page_protocol_connection_phase.html#sect_protocol_connection_phase_initial_handshake).
+ Default value: ""
+ By default, the format of the TiDB version string is `8.0.11-TiDB-${tidb_version}`.

> **Note:**
>
> TiDB nodes use the value of `server-version` to verify the current TiDB version. Therefore, to avoid unexpected behaviors, before upgrading the TiDB cluster, you need to set the value of `server-version` to empty or the real version of the current TiDB cluster.
