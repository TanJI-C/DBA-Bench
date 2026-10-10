# System variable reference: default_collation_for_utf8mb4 to max_allowed_packet

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > default_collation_for_utf8mb4 <span class="version-mark">New in v7.4.0</span> | System Variables > Variable reference > default_password_lifetime <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > default_week_format | System Variables > Variable reference > disconnect_on_expired_password <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > div_precision_increment <span class="version-mark">New in v8.0.0</span> | System Variables > Variable reference > error_count | System Variables > Variable reference > foreign_key_checks | System Variables > Variable reference > group_concat_max_len | System Variables > Variable reference > have_openssl | System Variables > Variable reference > have_ssl | System Variables > Variable reference > hostname | System Variables > Variable reference > identity <span class="version-mark">New in v5.3.0</span> | System Variables > Variable reference > init_connect | System Variables > Variable reference > innodb_lock_wait_timeout | System Variables > Variable reference > interactive_timeout | System Variables > Variable reference > last_insert_id | System Variables > Variable reference > last_plan_from_binding <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > last_plan_from_cache <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > last_sql_use_alloc <span class="version-mark">New in v6.4.0</span> | System Variables > Variable reference > license | System Variables > Variable reference > log_bin | System Variables > Variable reference > max_allowed_packet <span class="version-mark">New in v6.1.0</span>`
- Source Line Ranges: `454-669`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `cloud`
- Topic Tags: `system-variables`, `variable-reference`, `session-scope`, `global-scope`, `read-only`, `password-expiration`, `collation`, `timeouts`, `plan-cache`, `tls`, `packets`, `foreign-keys`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0711_f1a847dd4a`
- Source ID: `tidb-docs-8.1:system-variables.md#default-collation-for-utf8mb4-span-class-version-mark-new-in-v7-4-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `73ac25b7671a7aa570ff8d0b6c0f4e1acb0eb702e8b0bd1e52884f3bd7af8b7b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#default-collation-for-utf8mb4-span-class-version-mark-new-in-v7-4-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB system variable reference for variables from `default_collation_for_utf8mb4` through `max_allowed_packet`, including scope, defaults, ranges, read-only behavior, and what each variable controls.
- Retrieval Keywords: default_collation_for_utf8mb4, default_password_lifetime, default_week_format, disconnect_on_expired_password, div_precision_increment, error_count, foreign_key_checks, group_concat_max_len, have_openssl, have_ssl, hostname, identity, last_insert_id, init_connect, innodb_lock_wait_timeout, interactive_timeout, last_plan_from_binding, last_plan_from_cache, last_sql_use_alloc, license, log_bin, max_allowed_packet, SHOW COLLATION, SHOW CHARACTER SET, CREATE TABLE CHARACTER SET utf8mb4, ALTER TABLE CHARACTER SET utf8mb4, CREATE DATABASE CHARACTER SET utf8mb4, ALTER DATABASE CHARACTER SET utf8mb4, GROUP_CONCAT(), WEEK(), LAST_INSERT_ID(), AUTO_INCREMENT, AUTO_RANDOM, plan binding, plan cache, TiDB Binlog, security.disconnect-on-expired-password, CLIENT_INTERACTIVE, mysql_real_connect(), CONNECTION_ADMIN, SUPER
- Follow-up Guidance: The content also points to related behavior such as `security.disconnect-on-expired-password` for expired-password connection handling and notes that `identity` is an alias for `last_insert_id`.
- Classification Note: This chunk is classified as reference content because it lists system variables with their exact scopes, defaults, ranges, read-only notes, and concise definitions.

## Official Source Content

### default_collation_for_utf8mb4 New in v7.4.0

- Scope: GLOBAL | SESSION
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: String
- Default value: `utf8mb4_bin`
- Value options: `utf8mb4_bin`, `utf8mb4_general_ci`, `utf8mb4_0900_ai_ci`
- This variable is used to set the default [collation](https://docs.pingcap.com/tidb/stable/character-set-and-collation) for the `utf8mb4` character set. It affects the behavior of the following statements:
    - The default collation displayed in the [`SHOW COLLATION`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-collation) and [`SHOW CHARACTER SET`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-character-set) statements.
    - If [`CREATE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table) and [`ALTER TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table) statements contain the `CHARACTER SET utf8mb4` clause against a table or a column without specifying a collation, the collation specified by this variable is used. This does not affect the behavior when `CHARACTER SET` clause is not used.
    - If [`CREATE DATABASE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-database) and [`ALTER DATABASE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-database) statements contain `CHARACTER SET utf8mb4` clause without specifying a collation, the collation specified by this variable is used. This does not affect the behavior when `CHARACTER SET` clause is not used.
    - If the `COLLATE` clause is not used, any literal string in the format of `_utf8mb4'string'` uses the collation specified by this variable.
### default_password_lifetime New in v6.5.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 65535]`
- Sets the global policy for automatic password expiration. The default value `0` indicates that the password never expires. If this system variable is set to a positive integer `N`, it means that the password lifetime is `N` days, and you must change your password within `N` days.
### default_week_format

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 7]`
- Sets the week format used by the `WEEK()` function.
### disconnect_on_expired_password New in v6.5.0

- Scope: GLOBAL
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- This variable is read-only. It indicates whether TiDB disconnects the client connection when the password is expired. If the variable is set to `ON`, the client connection is disconnected when the password is expired. If the variable is set to `OFF`, the client connection is restricted to the "sandbox mode" and the user can only execute the password reset operation.

- If you need to change the behavior of the client connection for the expired password, modify the [`security.disconnect-on-expired-password`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#disconnect-on-expired-password-new-in-v650) configuration item in the configuration file.

- If you need to change the default behavior of the client connection for the expired password, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
### div_precision_increment New in v8.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `4`
- Range: `[0, 30]`
- This variable specifies the number of digits by which to increase the scale of the result of a division operation performed using the `/` operator. This variable is the same as MySQL.
### error_count

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- A read-only variable that indicates the number of errors that resulted from the last statement that generated messages.
### foreign_key_checks

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: Before v6.6.0, the default value is `OFF`. Starting from v6.6.0, the default value is `ON`.
- This variable controls whether to enable foreign key constraint checking.
### group_concat_max_len

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `1024`
- Range: `[4, 18446744073709551615]`
- The maximum buffer size for items in the `GROUP_CONCAT()` function.
### have_openssl

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `DISABLED`
- A read-only variable for MySQL compatibility. Set to `YES` by the server when the server has TLS enabled.
### have_ssl

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `DISABLED`
- A read-only variable for MySQL compatibility. Set to `YES` by the server when the server has TLS enabled.
### hostname

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: (system hostname)
- The hostname of the TiDB server as a read-only variable.
### identity New in v5.3.0

This variable is an alias for [`last_insert_id`](#last_insert_id).
### init_connect

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: ""
- The `init_connect` feature permits a SQL statement to be automatically executed when you first connect to a TiDB server. If you have the `CONNECTION_ADMIN` or `SUPER` privileges, this `init_connect` statement will not be executed. If the `init_connect` statement results in an error, your user connection will be terminated.
### innodb_lock_wait_timeout

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `50`
- Range: `[1, 3600]`
- Unit: Seconds
- The lock wait timeout for pessimistic transactions (default).
### interactive_timeout

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `28800`
- Range: `[1, 31536000]`
- Unit: Seconds
- This variable represents the idle timeout of the interactive user session. Interactive user session refers to the session established by calling [`mysql_real_connect()`](https://dev.mysql.com/doc/c-api/5.7/en/mysql-real-connect.html) API using the `CLIENT_INTERACTIVE` option (for example, MySQL Shell and MySQL Client). This variable is fully compatible with MySQL.
### last_insert_id

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 18446744073709551615]`
- This variable returns the last `AUTO_INCREMENT` or `AUTO_RANDOM` value generated by an insert statement.
- The value of `last_insert_id` is the same as the value returned by the function `LAST_INSERT_ID()`.
### last_plan_from_binding New in v4.0

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to show whether the execution plan used in the previous statement was influenced by a [plan binding](https://docs.pingcap.com/tidb/stable/sql-plan-management)
### last_plan_from_cache New in v4.0

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to show whether the execution plan used in the previous `execute` statement is taken directly from the plan cache.
### last_sql_use_alloc New in v6.4.0

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `OFF`
- This variable is read-only. It is used to show whether the previous statement uses a cached chunk object (chunk allocation).
### license

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `Apache License 2.0`
- This variable indicates the license of your TiDB server installation.
### log_bin

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable indicates whether [TiDB Binlog](https://docs.pingcap.com/tidb/stable/tidb-binlog-overview) is used.
### max_allowed_packet New in v6.1.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `67108864`
- Range: `[1024, 1073741824]`
- The value should be an integer multiple of 1024. If the value is not divisible by 1024, a warning will be prompted and the value will be rounded down. For example, when the value is set to 1025, the actual value in TiDB is 1024.
- The maximum packet size allowed by the server and the client in one transmission of packets.
- In the `SESSION` scope, this variable is read-only.
- This variable is compatible with MySQL.
