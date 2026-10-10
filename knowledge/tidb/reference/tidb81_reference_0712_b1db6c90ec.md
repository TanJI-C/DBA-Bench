# Password policy, MPP settings, and connection or execution limits

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > password_history <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > mpp_exchange_compression_mode <span class="version-mark">New in v6.6.0</span> | System Variables > Variable reference > mpp_version <span class="version-mark">New in v6.6.0</span> | System Variables > Variable reference > password_reuse_interval <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > max_connections | System Variables > Variable reference > max_execution_time | System Variables > Variable reference > max_prepared_stmt_count`
- Source Line Ranges: `670-786`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `sql`
- Topic Tags: `system-variables`, `password-policy`, `mpp`, `compression`, `connections`, `timeouts`, `prepared-statements`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0712_b1db6c90ec`
- Source ID: `tidb-docs-8.1:system-variables.md#password-history-span-class-version-mark-new-in-v6-5-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bdd237f1a769d232b611a0e4b9a3746024561a339b6491a5dbcd1ff10a751692`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#password-history-span-class-version-mark-new-in-v6-5-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables for password reuse policy, MPP exchange compression and MPP version selection, or limits for connections, statement execution time, and prepared statements.
- Retrieval Keywords: password_history, password_reuse_interval, mpp_exchange_compression_mode, mpp_version, max_connections, max_execution_time, max_prepared_stmt_count, MPP Exchange operator, MAX_EXECUTION_TIME hint, PREPARE statements, SHOW WARNINGS, Truncated incorrect max_prepared_stmt_count value
- Follow-up Guidance: The content also states that max_execution_time is overridden by the MAX_EXECUTION_TIME hint and that setting max_prepared_stmt_count above 1048576 produces warning 1292 and uses 1048576 instead.
- Classification Note: This is reference content because it lists system variable definitions with scope, persistence, defaults, ranges, value options, and documented effects for TiDB and TiFlash-related MPP behavior.

## Official Source Content

### password_history New in v6.5.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 4294967295]`
- This variable is used to establish a password reuse policy that allows TiDB to limit password reuse based on the number of password changes. The default value `0` means disabling the password reuse policy based on the number of password changes. When this variable is set to a positive integer `N`, the reuse of the last `N` passwords is not allowed.
### mpp_exchange_compression_mode New in v6.6.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Default value: `UNSPECIFIED`
- Value options: `NONE`, `FAST`, `HIGH_COMPRESSION`, `UNSPECIFIED`
- This variable is used to specify the data compression mode of the MPP Exchange operator. This variable takes effect when TiDB selects the MPP execution plan with the version number `1`. The meanings of the variable values are as follows:
    - `UNSPECIFIED`: means unspecified. TiDB will automatically select the compression mode. Currently, TiDB automatically selects the `FAST` mode.
    - `NONE`: no data compression is used.
    - `FAST`: fast mode. The overall performance is good and the compression ratio is less than `HIGH_COMPRESSION`.
    - `HIGH_COMPRESSION`: the high compression ratio mode.
### mpp_version New in v6.6.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Default value: `UNSPECIFIED`
- Value options: `UNSPECIFIED`, `0`, `1`, `2`
- This variable is used to specify different versions of the MPP execution plan. After a version is specified, TiDB selects the specified version of the MPP execution plan. The meanings of the variable values are as follows:
    - `UNSPECIFIED`: means unspecified. TiDB automatically selects the latest version `2`.
    - `0`: compatible with all TiDB cluster versions. Features with the MPP version greater than `0` do not take effect in this mode.
    - `1`: new in v6.6.0, used to enable data exchange with compression on TiFlash. For details, see [MPP version and exchange data compression](https://docs.pingcap.com/tidb/stable/explain-mpp#mpp-version-and-exchange-data-compression).
    - `2`: new in v7.3.0, used to provide more accurate error messages when MPP tasks encounter errors on TiFlash. 
### password_reuse_interval New in v6.5.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 4294967295]`
- This variable is used to establish a password reuse policy that allows TiDB to limit password reuse based on time elapsed. The default value `0` means disabling the password reuse policy based on time elapsed. When this variable is set to a positive integer `N`, the reuse of any password used in the last `N` days is not allowed.
### max_connections

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 100000]`
- The maximum number of concurrent connections permitted for a single TiDB instance. This variable can be used for resources control.
- The default value `0` means no limit. When the value of this variable is larger than `0`, and the number of connections reaches the value, the TiDB server rejects new connections from clients.
### max_execution_time

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `0`
- Range: `[0, 2147483647]`
- Unit: Milliseconds
- The maximum execution time of a statement. The default value is unlimited (zero).

> **Note:**
>
> Before v6.4.0, the `max_execution_time` system variable takes effect on all types of statements. Starting from v6.4.0, this variable only controls the maximum execution time of read-only statements. The precision of the timeout value is roughly 100ms. This means the statement might not be terminated in exact milliseconds as you specify.

For a SQL statement with the [`MAX_EXECUTION_TIME`](https://docs.pingcap.com/tidb/stable/optimizer-hints#max_execution_timen) hint, the maximum execution time of this statement is limited by the hint instead of this variable. The hint can also be used with SQL bindings as described [in the SQL FAQ](https://docs.pingcap.com/tidb/stable/faq/sql-faq#how-to-prevent-the-execution-of-a-particular-sql-statement).

For a SQL statement with the [`MAX_EXECUTION_TIME`](https://docs.pingcap.com/tidb/stable/optimizer-hints#max_execution_timen) hint, the maximum execution time of this statement is limited by the hint instead of this variable. The hint can also be used with SQL bindings as described [in the SQL FAQ](https://docs.pingcap.com/tidb/stable/sql-faq).
### max_prepared_stmt_count

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `-1`
- Range: `[-1, 1048576]`
- Specifies the maximum number of [`PREPARE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-prepare) statements in the current TiDB instance.
- The value of `-1` means no limit on the maximum number of `PREPARE` statements in the current TiDB instance.
- If you set the variable to a value that exceeds the upper limit `1048576`, `1048576` is used instead:

```sql
mysql> SET GLOBAL max_prepared_stmt_count = 1048577;
Query OK, 0 rows affected, 1 warning (0.01 sec)

mysql> SHOW WARNINGS;
+---------+------+--------------------------------------------------------------+
| Level   | Code | Message                                                      |
+---------+------+--------------------------------------------------------------+
| Warning | 1292 | Truncated incorrect max_prepared_stmt_count value: '1048577' |
+---------+------+--------------------------------------------------------------+
1 row in set (0.00 sec)

mysql> SHOW GLOBAL VARIABLES LIKE 'max_prepared_stmt_count';
+-------------------------+---------+
| Variable_name           | Value   |
+-------------------------+---------+
| max_prepared_stmt_count | 1048576 |
+-------------------------+---------+
1 row in set (0.00 sec)
```
