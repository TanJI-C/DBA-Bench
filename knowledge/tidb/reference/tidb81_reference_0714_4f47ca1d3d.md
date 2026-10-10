# Connection security and SQL behavior variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > require_secure_transport <span class="version-mark">New in v6.1.0</span> | System Variables > Variable reference > skip_name_resolve <span class="version-mark">New in v5.2.0</span> | System Variables > Variable reference > socket | System Variables > Variable reference > sql_log_bin | System Variables > Variable reference > sql_mode | System Variables > Variable reference > sql_require_primary_key <span class="version-mark">New in v6.3.0</span> | System Variables > Variable reference > sql_select_limit <span class="version-mark">New in v4.0.2</span> | System Variables > Variable reference > ssl_ca | System Variables > Variable reference > ssl_cert | System Variables > Variable reference > ssl_key | System Variables > Variable reference > system_time_zone`
- Source Line Ranges: `856-1034`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `cloud`, `dm`, `ticdc`, `shared`
- Topic Tags: `tls`, `connection-security`, `dns`, `socket`, `binlog`, `sql-mode`, `primary-key`, `select-limit`, `ssl`, `time-zone`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0714_4f47ca1d3d`
- Source ID: `tidb-docs-8.1:system-variables.md#require-secure-transport-span-class-version-mark-new-in-v6-1-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d4a9eef30f020bb5d2d0e357b92527cc418dd7f10a7097cc21ed5b59bc405f83`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#require-secure-transport-span-class-version-mark-new-in-v6-1-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables for connection security, DNS name resolution during handshake, local socket path, TiDB Binlog logging, SQL compatibility mode, primary key enforcement, SELECT row limits, SSL certificate file paths, or the bootstrapped system time zone.
- Retrieval Keywords: require_secure_transport, skip_name_resolve, socket, sql_log_bin, sql_mode, sql_require_primary_key, sql_select_limit, ssl_ca, ssl_cert, ssl_key, system_time_zone, security.require-secure-transport, Enable TLS between TiDB Clients and Servers, tidb-server resolves hostnames as a part of the connection handshake, CREATE USER 'appuser'@'apphost' IDENTIFIED BY 'app-password', TiDB Binlog, ONLY_FULL_GROUP_BY, STRICT_TRANS_TABLES, NO_ZERO_IN_DATE, NO_ZERO_DATE, ERROR_FOR_DIVISION_BY_ZERO, NO_AUTO_CREATE_USER, NO_ENGINE_SUBSTITUTION, SET_VAR, ssl-ca, ssl-cert, ssl-key, time_zone
- Follow-up Guidance: The content notes that `skip_name_resolve=ON` prevents users with a hostname in their identity from logging in, and that `sql_require_primary_key` is strongly recommended with TiCDC while DM task configuration can set `sql_require_primary_key` to `OFF` in `session` to avoid task creation failure.
- Classification Note: This is a reference chunk because it enumerates system variable definitions, scopes, defaults, types, and notes for TiDB SQL and connection behavior.

## Official Source Content

### require_secure_transport New in v6.1.0

> **Note:**
>
> Currently, this variable is not supported on [TiDB Cloud Dedicated](https://docs.pingcap.com/tidbcloud/select-cluster-tier#tidb-cloud-dedicated). DO **NOT** enable this variable for TiDB Cloud Dedicated clusters. Otherwise, you might get SQL client connection failures. This restriction is a temporary control measure and will be resolved in a future release.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF` for TiDB Self-Managed and [TiDB Cloud Dedicated](https://docs.pingcap.com/tidbcloud/select-cluster-tier#tidb-cloud-dedicated), `ON` for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential)

- This variable ensures that all connections to TiDB are either on a local socket, or using TLS. See [Enable TLS between TiDB Clients and Servers](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers) for additional details.

- This variable ensures that all connections to TiDB are either on a local socket, or using TLS.

- Setting this variable to `ON` requires you to connect to TiDB from a session that has TLS enabled. This helps prevent lock-out scenarios when TLS is not configured correctly.
- This setting was previously a `tidb.toml` option (`security.require-secure-transport`), but changed to a system variable starting from TiDB v6.1.0.
- Starting from v6.5.6, v7.1.2, v7.5.1, and v8.0.0, when Security Enhanced Mode (SEM) is enabled, setting this variable to `ON` is prohibited to avoid potential connectivity issues for users.
### skip_name_resolve New in v5.2.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable controls whether the `tidb-server` instance resolves hostnames as a part of the connection handshake.
- When the DNS is unreliable, you can enable this option to improve network performance.

> **Note:**
>
> When `skip_name_resolve=ON`, users with a hostname in their identity will no longer be able to log into the server. For example:
>
> ```sql
> CREATE USER 'appuser'@'apphost' IDENTIFIED BY 'app-password';
> ```
>
> In this example, it is recommended to replace `apphost` with an IP address or the wildcard (`%`).
### socket

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: ""
- The local unix socket file that the `tidb-server` is listening on when speaking the MySQL protocol.
### sql_log_bin

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter).

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- Indicates whether to write changes to [TiDB Binlog](https://docs.pingcap.com/tidb/stable/tidb-binlog-overview) or not.

> **Note:**
>
> It is not recommended to set `sql_log_bin` as a global variable because the future versions of TiDB might only allow setting this as a session variable.
### sql_mode

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Default value: `ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION`
- This variable controls a number of MySQL compatibility behaviors. See [SQL Mode](https://docs.pingcap.com/tidb/stable/sql-mode) for more information.
### sql_require_primary_key New in v6.3.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable controls whether to enforce the requirement that a table has a primary key. After this variable is enabled, attempting to create or alter a table without a primary key will produce an error.
- This feature is based on the similarly named [`sql_require_primary_key`](https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html#sysvar_sql_require_primary_key) in MySQL 8.0.
- It is strongly recommended to enable this variable when using TiCDC. This is because replicating changes to a MySQL sink requires that tables have a primary key.

- If you enable this variable and are using TiDB Data Migration (DM) to migrate data, it is recommended that you add `sql_require_ primary_key` to the `session` part in the [DM Task Configuration File](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full#task-configuration-file-template-advanced) and set it to `OFF`. Otherwise, it will cause DM to fail to create tasks.
### sql_select_limit New in v4.0.2

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `18446744073709551615`
- Range: `[0, 18446744073709551615]`
- Unit: Rows
- The maximum number of rows returned by the `SELECT` statements.
### ssl_ca

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: ""
- The location of the certificate authority file (if there is one). The value of this variable is defined by the TiDB configuration item [`ssl-ca`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-ca).

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: ""
- The location of the certificate authority file (if there is one). The value of this variable is defined by the TiDB configuration item [`ssl-ca`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-ca).
### ssl_cert

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: ""
- The location of the certificate file (if there is a file) that is used for SSL/TLS connections. The value of this variable is defined by the TiDB configuration item [`ssl-cert`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-cert).

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: ""
- The location of the certificate file (if there is a file) that is used for SSL/TLS connections. The value of this variable is defined by the TiDB configuration item [`ssl-cert`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-cert).
### ssl_key

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: ""
- The location of the private key file (if there is one) that is used for SSL/TLS connections. The value of this variable is defined by TiDB configuration item [`ssl-key`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-cert).

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: ""
- The location of the private key file (if there is one) that is used for SSL/TLS connections. The value of this variable is defined by TiDB configuration item [`ssl-key`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#ssl-key).
### system_time_zone

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: (system dependent)
- This variable shows the system time zone from when TiDB was first bootstrapped. See also [`time_zone`](#time_zone).
